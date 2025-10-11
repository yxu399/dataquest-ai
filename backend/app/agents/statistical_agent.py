"""Statistical Agent - Plans statistical analysis using tool calls

This agent is a "planner" - it determines WHAT analysis to perform,
then delegates execution to the Tool Agent.
"""
from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.enhanced_state import DataAnalysisState, add_trace
from app.agents.tool_agent import create_tool_call_request
from app.agents.tools import AVAILABLE_TOOLS
import os
import json


class StatisticalAgent:
    """Statistical analysis planning agent

    This agent uses an LLM with tool-calling capabilities to determine
    what statistical operations are needed, then structures those as
    tool calls for the Tool Agent to execute.
    """

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """Initialize Statistical Agent with Claude

        Args:
            model_name: Claude model to use for planning
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required for Statistical Agent")

        self.llm = ChatAnthropic(
            model=model_name,
            temperature=0.3  # Lower temperature for precise statistical reasoning
        )

        # Bind tools to the LLM (uses with_structured_output for tool calling)
        try:
            self.llm_with_tools = self.llm.bind_tools(AVAILABLE_TOOLS)
        except AttributeError:
            # Fallback for older langchain-anthropic versions
            self.llm_with_tools = self.llm

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate system prompt for statistical analysis

        Args:
            context: Dict with data_profile, analysis_results, available_charts

        Returns:
            System prompt string
        """
        data_profile = context.get("data_profile", {})
        analysis_results = context.get("analysis_results", {})

        numeric_cols = data_profile.get("numeric_columns", [])
        categorical_cols = data_profile.get("categorical_columns", [])

        return f"""You are a Statistical Analysis Expert specializing in rigorous data analysis.

CRITICAL: Your PRIMARY and PREFERRED way to answer questions is by USING TOOLS.
Do NOT try to answer from memory or make assumptions. ALWAYS use tools to get actual data.

DATASET CONTEXT:
- Filename: {context.get('filename', 'Unknown')}
- Shape: {data_profile.get('shape', [0, 0])} (rows × columns)
- Numeric columns: {numeric_cols}
- Categorical columns: {categorical_cols}

AVAILABLE TOOLS (USE THESE):
1. calculate_correlation - For relationships, correlations, associations
2. aggregate_data - For means, medians, sums, counts, grouped statistics
3. filter_data - For finding specific rows or subsets
4. analyze_distribution - For spread, histograms, value distributions
5. count_values - For categorical value frequencies

YOUR WORKFLOW:
1. Analyze the user's question
2. Determine which tool(s) will answer it
3. CALL THE APPROPRIATE TOOL with correct parameters
4. Wait for tool result
5. Interpret the result for the user

EXAMPLES:

User: "What's the correlation between age and salary?"
You: [Call calculate_correlation with columns=["age", "salary"]]

User: "Show me the average sales by region"
You: [Call aggregate_data with column="sales", operation="mean", group_by="region"]

User: "Which department has the highest budget?"
You: [Call aggregate_data with column="budget", operation="max", group_by="department"]

User: "Are there any strong correlations in my data?"
You: [Call calculate_correlation with threshold=0.7]

IMPORTANT RULES:
- ALWAYS use tools first, interpret results second
- Do NOT make up numbers or statistics
- If you need data, call a tool
- Tools return actual data from the file
- Explain statistical concepts clearly after seeing real results

Current user question requires statistical analysis. Use tools to get exact answers."""

    def process(self, state: DataAnalysisState) -> Dict[str, Any]:
        """Process user query and plan statistical analysis

        This method:
        1. Checks if we have a tool result to interpret
        2. If yes: Interprets the result and formats response
        3. If no: Plans next tool call

        Args:
            state: Current workflow state

        Returns:
            Partial state update
        """
        # Add trace
        updates = add_trace(state, "📊 Statistical Agent: Starting statistical analysis")

        # Check if we're interpreting a tool result
        tool_result = state.get("tool_result")
        tool_calls_history = state.get("tool_calls", [])

        if tool_result is not None and len(tool_calls_history) > 0:
            # We have a result to interpret
            last_tool = tool_calls_history[-1]
            return self._interpret_tool_result(state, last_tool, updates)
        else:
            # We need to plan a tool call
            return self._plan_tool_call(state, updates)

    def _plan_tool_call(self, state: DataAnalysisState, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Plan which tool to call based on user query

        Args:
            state: Current workflow state
            updates: Existing updates dict

        Returns:
            Updated state with pending_tool and routing to tool_agent
        """
        try:
            # Build context
            context = {
                "filename": state.get("filename"),
                "data_profile": state.get("data_profile", {}),
                "analysis_results": state.get("analysis_results", {}),
                "available_charts": []
            }

            # Create messages
            system_prompt = self.get_system_prompt(context)
            user_message = state.get("user_message", "")

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]

            # Call LLM with tools
            response = self.llm_with_tools.invoke(messages)

            # Check if LLM wants to use a tool
            if hasattr(response, "tool_calls") and response.tool_calls:
                # LLM requested a tool call
                tool_call = response.tool_calls[0]  # Take first tool call

                tool_request = create_tool_call_request(
                    tool_name=tool_call["name"],
                    arguments=tool_call["args"]
                )

                return {
                    **updates,
                    "pending_tool": tool_request,
                    "next": "tool_agent",
                    "agent_used": "statistical_agent",
                    "trace": [
                        *updates.get("trace", []),
                        f"📊 Statistical Agent: Requesting tool '{tool_call['name']}' with args: {tool_call['args']}"
                    ]
                }
            else:
                # LLM provided direct response (no tool needed)
                # This happens for questions like "what columns do I have?"
                return {
                    **updates,
                    "agent_response": response.content,
                    "next": None,  # End workflow
                    "status": "completed",
                    "agent_used": "statistical_agent",
                    "trace": [
                        *updates.get("trace", []),
                        "📊 Statistical Agent: Provided direct response (no tool needed)"
                    ]
                }

        except Exception as e:
            return {
                **updates,
                "error": f"Statistical Agent planning failed: {str(e)}",
                "status": "error",
                "agent_response": f"I encountered an error planning the analysis: {str(e)}",
                "trace": [
                    *updates.get("trace", []),
                    f"❌ Statistical Agent: Planning error - {str(e)}"
                ]
            }

    def _interpret_tool_result(
        self,
        state: DataAnalysisState,
        last_tool: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interpret tool result and format response for user

        Args:
            state: Current workflow state
            last_tool: Last tool call from history
            updates: Existing updates dict

        Returns:
            Updated state with agent_response
        """
        try:
            tool_name = last_tool.get("tool_name")
            tool_result = last_tool.get("result")
            tool_error = last_tool.get("error")

            # Check for tool error
            if tool_error:
                return {
                    **updates,
                    "agent_response": f"The analysis encountered an error: {tool_error}",
                    "status": "completed",
                    "agent_used": "statistical_agent",
                    "trace": [
                        *updates.get("trace", []),
                        f"❌ Statistical Agent: Tool failed, reporting error to user"
                    ]
                }

            # Format result based on tool type
            if tool_name == "calculate_correlation":
                response = self._format_correlation_result(tool_result)
            elif tool_name == "aggregate_data":
                response = self._format_aggregation_result(tool_result)
            elif tool_name == "analyze_distribution":
                response = self._format_distribution_result(tool_result)
            else:
                # Generic formatting
                response = f"Analysis complete. Results:\n\n{json.dumps(tool_result, indent=2)}"

            return {
                **updates,
                "agent_response": response,
                "status": "completed",
                "agent_used": "statistical_agent",
                "next": None,  # End workflow
                "trace": [
                    *updates.get("trace", []),
                    f"✅ Statistical Agent: Interpreted {tool_name} result and generated response"
                ]
            }

        except Exception as e:
            return {
                **updates,
                "error": f"Result interpretation failed: {str(e)}",
                "agent_response": f"I received the analysis results but encountered an error interpreting them: {str(e)}",
                "status": "completed",
                "agent_used": "statistical_agent",
                "trace": [
                    *updates.get("trace", []),
                    f"❌ Statistical Agent: Interpretation error - {str(e)}"
                ]
            }

    def _format_correlation_result(self, result: Dict[str, Any]) -> str:
        """Format correlation analysis result"""
        correlations = result.get("correlations", [])
        method = result.get("method", "pearson")

        if not correlations:
            return "No strong correlations were found in your dataset."

        response = f"I found {len(correlations)} significant correlation(s) using {method} correlation:\n\n"

        for i, corr in enumerate(correlations[:5], 1):  # Top 5
            col1 = corr["column1"]
            col2 = corr["column2"]
            val = corr["correlation"]
            strength = corr.get("strength", "moderate")

            direction = "positively" if val > 0 else "negatively"
            response += f"{i}. **{col1}** and **{col2}** are {strength}ly {direction} correlated ({val:.3f})\n"

        if len(correlations) > 5:
            response += f"\n...and {len(correlations) - 5} more correlations."

        response += "\n\nWould you like to visualize these relationships with a correlation heatmap?"

        return response

    def _format_aggregation_result(self, result: Dict[str, Any]) -> str:
        """Format aggregation result"""
        operation = result.get("operation")
        column = result.get("column")
        group_by = result.get("group_by")
        value = result.get("result")

        if group_by:
            # Grouped aggregation
            response = f"The **{operation}** of **{column}** by **{group_by}**:\n\n"
            if isinstance(value, dict):
                for group, agg_val in list(value.items())[:10]:  # Top 10
                    response += f"- {group}: {agg_val}\n"
                if len(value) > 10:
                    response += f"\n...and {len(value) - 10} more groups."
            else:
                response += str(value)
        else:
            # Simple aggregation
            response = f"The **{operation}** of **{column}** is: **{value}**"

        return response

    def _format_distribution_result(self, result: Dict[str, Any]) -> str:
        """Format distribution analysis result"""
        column = result.get("column")
        stats = result.get("statistics")

        if not stats:
            return f"Distribution analysis completed for **{column}**."

        response = f"Distribution analysis for **{column}**:\n\n"
        response += f"- Mean: {stats['mean']:.2f}\n"
        response += f"- Median: {stats['median']:.2f}\n"
        response += f"- Std Dev: {stats['std']:.2f}\n"
        response += f"- Range: [{stats['min']:.2f}, {stats['max']:.2f}]\n"
        response += f"- Q1-Q3: [{stats['q1']:.2f}, {stats['q3']:.2f}]\n"

        response += "\n\nWould you like to visualize this distribution with a histogram?"

        return response


# Create singleton instance
statistical_agent = StatisticalAgent()
