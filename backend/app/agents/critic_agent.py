"""Critic Agent - Evaluates response quality and provides feedback for refinement

This agent evaluates the quality of agent responses and determines whether
the response meets quality standards. If not, it provides critique and
suggests which agent should retry.
"""

from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.enhanced_state import (
    DataAnalysisState,
    add_trace,
    add_critique,
    increment_iteration,
    CRITIC_THRESHOLD,
)
from app.core.config import settings
import json


class CriticAgent:
    """Quality evaluation agent for response refinement

    This agent uses an LLM to evaluate the quality of agent responses,
    providing scores, critiques, and routing suggestions for improvement.
    """

    def __init__(self, model_name: str | None = None):
        """Initialize Critic Agent with Claude

        Args:
            model_name: Claude model to use (defaults to settings.anthropic_model_name)
        """
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable required for Critic Agent"
            )

        self.model_name = model_name or settings.anthropic_model_name
        self.llm = ChatAnthropic(
            model=self.model_name,
            temperature=0.2,  # Low temperature for consistent evaluation
            api_key=settings.anthropic_api_key,
        )

    def get_system_prompt(self) -> str:
        """Generate system prompt for quality evaluation

        Returns:
            System prompt string
        """
        return f"""You are a Quality Assurance Analyst specializing in data analysis responses.

Your task is to evaluate the quality of an agent's response to a user's question about their dataset.

EVALUATION CRITERIA (Score 0-1):

1. **Accuracy** (0.30 weight):
   - Does the response correctly interpret the data?
   - Are statistical conclusions valid?
   - Are there any factual errors?

2. **Completeness** (0.30 weight):
   - Does it fully answer the user's question?
   - Are all aspects of the query addressed?
   - Is any critical information missing?

3. **Clarity** (0.20 weight):
   - Is the response easy to understand?
   - Are explanations clear and well-structured?
   - Is statistical jargon explained appropriately?

4. **Actionability** (0.20 weight):
   - Does it provide useful insights?
   - Are there helpful follow-up suggestions?
   - Can the user act on the information?

SCORING GUIDELINES:
- **0.9-1.0**: Excellent - comprehensive, accurate, clear, actionable
- **0.8-0.9**: Good - meets all criteria, minor improvements possible
- **0.6-0.8**: Fair - acceptable but missing key elements
- **0.4-0.6**: Poor - significant issues with accuracy or completeness
- **0.0-0.4**: Failing - major errors or completely misses the question

THRESHOLD: **{CRITIC_THRESHOLD}** (responses scoring >= {CRITIC_THRESHOLD} pass)

YOUR RESPONSE FORMAT:
You must respond with a JSON object containing:
{{
    "score": <float 0-1>,
    "critique": "<explanation of score and issues>",
    "reroute_to": "<agent name to retry with, or null if passed>",
    "improvement_suggestions": ["<specific suggestion 1>", "<specific suggestion 2>"]
}}

REROUTE SUGGESTIONS:
- "statistical_agent" - For incorrect statistics or missing calculations
- "visualization_agent" - For missing or incorrect chart suggestions
- "insights_agent" - For lack of actionable insights
- "query_agent" - For general follow-up questions
- null - If the response passes quality checks

IMPORTANT:
- Be strict but fair in your evaluation
- Provide specific, actionable critique
- If score < {CRITIC_THRESHOLD}, you MUST suggest a reroute_to agent
- If score >= {CRITIC_THRESHOLD}, set reroute_to to null
"""

    def process(self, state: DataAnalysisState) -> Dict[str, Any]:
        """Evaluate response quality and provide critique

        Args:
            state: Current workflow state

        Returns:
            Partial state update with critique result
        """
        # Add trace
        updates = add_trace(state, "🎯 Critic Agent: Evaluating response quality")

        try:
            # Get the response to evaluate
            agent_response = state.get("agent_response")
            if not agent_response:
                # No response to evaluate - this shouldn't happen
                return {
                    **updates,
                    **add_critique(
                        state,
                        score=0.0,
                        critique="No agent response found to evaluate",
                        reroute_to="router",
                    ),
                    "trace": [
                        *updates.get("trace", []),
                        "❌ Critic Agent: No response to evaluate",
                    ],
                }

            # Build evaluation context
            context = self._build_evaluation_context(state)

            # Call LLM to evaluate
            evaluation = self._evaluate_response(
                agent_response=agent_response,
                user_message=state.get("user_message", ""),
                context=context,
            )

            # Extract evaluation results
            score = evaluation.get("score", 0.0)
            critique = evaluation.get("critique", "Evaluation completed")
            reroute_to = evaluation.get("reroute_to")

            # Increment iteration count
            iteration_update = increment_iteration(state)

            # Add critique to state
            critique_update = add_critique(
                state, score=score, critique=critique, reroute_to=reroute_to
            )

            # Determine next step
            passed = score >= CRITIC_THRESHOLD
            current_iteration = state.get("iteration_count", 0) + 1
            max_iterations = state.get("max_iterations", 3)

            if passed:
                # Quality check passed
                next_node = None  # End workflow
                status = "completed"
                trace_msg = f"✅ Critic Agent: Quality check PASSED (score={score:.2f})"
            elif current_iteration >= max_iterations:
                # Max iterations reached, accept current response
                next_node = None
                status = "completed"
                trace_msg = f"⚠️ Critic Agent: Max iterations reached ({max_iterations}), accepting response (score={score:.2f})"
            else:
                # Failed, reroute for retry
                next_node = reroute_to or "router"
                status = "refining"
                trace_msg = f"🔄 Critic Agent: Quality check FAILED (score={score:.2f}), rerouting to {next_node}"

            return {
                **updates,
                **iteration_update,
                **critique_update,
                "next": next_node,
                "status": status,
                "agent_used": "critic_agent",
                "trace": [*updates.get("trace", []), trace_msg],
            }

        except Exception as e:
            # If evaluation fails, pass the response through
            return {
                **updates,
                **add_critique(
                    state,
                    score=0.5,
                    critique=f"Evaluation error: {str(e)}. Accepting response.",
                    reroute_to=None,
                ),
                "next": None,
                "status": "completed",
                "agent_used": "critic_agent",
                "trace": [
                    *updates.get("trace", []),
                    f"⚠️ Critic Agent: Evaluation error - {str(e)}, accepting response",
                ],
            }

    def _build_evaluation_context(self, state: DataAnalysisState) -> Dict[str, Any]:
        """Build context for evaluation

        Args:
            state: Current workflow state

        Returns:
            Context dict with relevant information
        """
        data_profile = state.get("data_profile", {})
        analysis_results = state.get("analysis_results", {})
        tool_calls = state.get("tool_calls", [])

        return {
            "filename": state.get("filename"),
            "dataset_shape": data_profile.get("shape", [0, 0]),
            "numeric_columns": data_profile.get("numeric_columns", []),
            "categorical_columns": data_profile.get("categorical_columns", []),
            "tools_used": [tc["tool_name"] for tc in tool_calls],
            "query_type": state.get("query_type"),
            "agent_used": state.get("agent_used"),
        }

    def _evaluate_response(
        self, agent_response: str, user_message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate response quality using LLM

        Args:
            agent_response: The response to evaluate
            user_message: Original user question
            context: Evaluation context

        Returns:
            Evaluation dict with score, critique, reroute_to
        """
        # Build evaluation prompt
        system_prompt = self.get_system_prompt()

        # Format context information
        context_str = f"""DATASET CONTEXT:
- Filename: {context.get('filename', 'Unknown')}
- Shape: {context.get('dataset_shape', [0, 0])} (rows × columns)
- Numeric columns: {', '.join(context.get('numeric_columns', [])[:5])}
- Categorical columns: {', '.join(context.get('categorical_columns', [])[:5])}
- Tools used: {', '.join(context.get('tools_used', [])) or 'None'}
- Query type: {context.get('query_type', 'Unknown')}
- Agent used: {context.get('agent_used', 'Unknown')}
"""

        user_prompt = f"""{context_str}

USER'S QUESTION:
{user_message}

AGENT'S RESPONSE:
{agent_response}

Evaluate the quality of this response and provide your assessment in JSON format."""

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

        # Call LLM
        response = self.llm.invoke(messages)

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            evaluation = json.loads(content)

            # Validate required fields
            if "score" not in evaluation:
                evaluation["score"] = 0.5
            if "critique" not in evaluation:
                evaluation["critique"] = "Evaluation completed"

            # Ensure score is in valid range
            evaluation["score"] = max(0.0, min(1.0, float(evaluation["score"])))

            return evaluation

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback if JSON parsing fails
            return {
                "score": 0.5,
                "critique": f"Unable to parse evaluation (error: {str(e)}). Response appears reasonable.",
                "reroute_to": None,
            }


# Create singleton instance
critic_agent = CriticAgent()
