# LangGraph Multi-Agent Integration Plan for DataQuest AI

## Overview

This document outlines the integration of your existing LangGraph multi-agent architecture from the chatbot project into DataQuest AI. This will replace the current `simple_workflow.py` with a sophisticated multi-agent data analysis system.

## Current Architecture (To Be Replaced)

### Current System: `simple_workflow.py`
- **Type**: Simple pandas-based pipeline
- **Pattern**: Monolithic function with sequential processing
- **Limitations**:
  - Single execution path
  - No intelligent routing
  - Limited extensibility
  - No agent specialization

### Current Chat Service: `chat_service.py`
- **Pattern**: Single AI endpoint with fallback rules
- **Processing**: Direct Claude API call or keyword matching
- **Context**: Basic data profile and analysis results

## Target Architecture: LangGraph Multi-Agent System

### Agent Specializations for Data Analysis

Based on your chatbot's 5-agent structure, we'll create 5 data-analysis-specific agents:

#### 1. **Profiling Agent** (replaces "therapist")
**Purpose**: Initial data understanding and structure analysis
**Responsibilities**:
- Dataset shape and schema analysis
- Data type detection (numeric/categorical)
- Missing value detection and patterns
- Data quality assessment
- Sample data extraction

**System Prompt Template**:
```python
You are a Data Profiling Specialist. Your expertise is in understanding dataset structure, identifying data types, detecting quality issues, and providing initial assessments. When analyzing data:
- Focus on structure, shape, and data types
- Identify missing data patterns and quality issues
- Provide clear, actionable insights about data quality
- Suggest next steps for deeper analysis
```

**Example Queries**:
- "What does this dataset look like?"
- "Is my data complete?"
- "Tell me about the structure"
- "What columns do I have?"

#### 2. **Statistical Agent** (replaces "logical")
**Purpose**: Rigorous statistical analysis and correlation discovery
**Responsibilities**:
- Correlation analysis (Pearson, Spearman)
- Hypothesis testing
- Statistical summaries (mean, median, std, quartiles)
- Distribution analysis
- Outlier detection

**System Prompt Template**:
```python
You are a Statistical Analysis Expert. You excel at mathematical rigor, correlation discovery, and statistical inference. When analyzing data:
- Calculate precise statistics (correlations, distributions, summary stats)
- Identify significant patterns and relationships
- Apply appropriate statistical tests
- Explain findings with mathematical precision
- Recommend visualizations based on statistical properties
```

**Example Queries**:
- "Show me correlations"
- "What's the relationship between X and Y?"
- "Find patterns in my data"
- "Are there any outliers?"

#### 3. **Visualization Agent** (replaces "study_buddy")
**Purpose**: Chart recommendations and visual analysis strategies
**Responsibilities**:
- Recommend appropriate chart types
- Determine optimal visualizations based on data types
- Suggest multi-chart comparisons
- Guide visual exploration strategies
- Prepare chart data structures

**System Prompt Template**:
```python
You are a Data Visualization Expert. You guide users in choosing the right visualizations for their data and questions. When recommending charts:
- Match chart types to data characteristics (categorical vs numeric)
- Suggest appropriate visualizations for the user's question
- Explain why specific visualizations work best
- Provide clear guidance on interpreting visual patterns
- Format responses with: CHART_SUGGESTION: [type]
```

**Example Queries**:
- "What charts can I create?"
- "Show me a visualization"
- "How can I visualize this?"
- "Compare these columns visually"

#### 4. **Insight Agent** (replaces "creative")
**Purpose**: Generate business insights and narrative interpretations
**Responsibilities**:
- Generate actionable insights from analysis
- Create narrative explanations of patterns
- Identify business implications
- Suggest strategic recommendations
- Synthesize findings across analyses

**System Prompt Template**:
```python
You are a Business Insights Analyst. You transform raw data patterns into meaningful business insights and strategic recommendations. When generating insights:
- Connect data patterns to business value
- Create clear, actionable recommendations
- Tell the story hidden in the data
- Highlight surprising or important findings
- Make complex patterns understandable
```

**Example Queries**:
- "What does this mean for my business?"
- "Give me key insights"
- "What are the main findings?"
- "What should I focus on?"

#### 5. **Query Agent** (replaces "planning")
**Purpose**: Handle specific data queries and column-level analysis
**Responsibilities**:
- Answer specific questions about data values
- Handle column-specific queries
- Filter and aggregate data
- Compare specific data points
- Provide direct answers from the dataset

**System Prompt Template**:
```python
You are a Data Query Specialist. You answer specific questions about data values, columns, and relationships. When responding to queries:
- Extract exact values from the dataset
- Handle column-specific questions precisely
- Perform aggregations and comparisons
- Provide direct, factual answers
- Reference specific data points when available
```

**Example Queries**:
- "What's the average salary?"
- "Which department has the most projects?"
- "Show me the top 5 values"
- "Compare X across Y categories"

### Message Classifier for Data Analysis

Your chatbot's classifier routes by emotional/logical/study/creative/planning. For DataQuest, we'll classify by **analysis intent**:

```python
from typing import Literal
from pydantic import BaseModel, Field

class DataAnalysisClassifier(BaseModel):
    """Classifier for routing data analysis queries to appropriate agents"""

    query_type: Literal[
        "profiling",      # Structure, types, quality
        "statistical",    # Correlations, patterns, distributions
        "visualization",  # Chart requests, visual exploration
        "insights",       # Business value, recommendations
        "query"          # Specific data questions
    ] = Field(description="The type of data analysis query")

    confidence: float = Field(description="Confidence in classification (0-1)")
    reasoning: str = Field(description="Why this classification was chosen")
```

### Classification Rules (Pattern-Based Fallback)

When Claude API is unavailable, use keyword-based routing:

```python
CLASSIFICATION_PATTERNS = {
    "profiling": [
        "structure", "schema", "columns", "data types", "missing",
        "quality", "what does", "tell me about", "describe"
    ],
    "statistical": [
        "correlation", "relationship", "pattern", "outlier",
        "distribution", "statistics", "mean", "median", "significant"
    ],
    "visualization": [
        "chart", "plot", "graph", "visualize", "show me",
        "create", "bar", "scatter", "histogram", "heatmap"
    ],
    "insights": [
        "insight", "finding", "key", "summary", "important",
        "recommendation", "business", "what does this mean", "implication"
    ],
    "query": [
        "which", "what", "how many", "average", "total",
        "highest", "lowest", "top", "compare", "specific"
    ]
}
```

## Implementation Phases

### Phase 1: Core LangGraph Infrastructure (Week 1)

**Files to Create**:
1. `backend/app/agents/langgraph_workflow.py` - Main workflow
2. `backend/app/agents/state.py` - State management
3. `backend/app/agents/classifier.py` - Query classification
4. `backend/app/agents/base_agent.py` - Base agent class

**Dependencies to Add**:
```bash
uv add langgraph langchain-anthropic langchain-core
```

**Key Components**:
```python
# state.py
from typing import TypedDict, List, Optional, Dict, Any

class DataAnalysisState(TypedDict):
    """State for data analysis workflow"""

    # User input
    user_message: str
    conversation_history: List[Dict[str, str]]

    # Data context
    file_path: str
    filename: str
    data_profile: Dict[str, Any]
    analysis_results: Dict[str, Any]
    insights: List[str]

    # Routing
    query_type: str
    next: str

    # Agent outputs
    agent_response: str
    chart_type: Optional[str]
    chart_data: Optional[Dict]

    # Metadata
    processing_time: float
    agent_used: str
```

### Phase 2: Agent Implementation (Week 2)

**Create Agent Classes**:
```python
# base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic

class BaseDataAgent(ABC):
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620"):
        self.llm = ChatAnthropic(model=model_name, temperature=0.7)

    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Return agent-specific system prompt"""
        pass

    @abstractmethod
    def process(self, state: DataAnalysisState) -> DataAnalysisState:
        """Process the user query with agent-specific logic"""
        pass
```

**Each agent implements**:
- `ProfilingAgent(BaseDataAgent)`
- `StatisticalAgent(BaseDataAgent)`
- `VisualizationAgent(BaseDataAgent)`
- `InsightAgent(BaseDataAgent)`
- `QueryAgent(BaseDataAgent)`

### Phase 3: Workflow Integration (Week 3)

**Main Workflow**:
```python
# langgraph_workflow.py
from langgraph.graph import StateGraph, END

def create_data_analysis_graph():
    """Create the multi-agent data analysis workflow"""

    graph_builder = StateGraph(DataAnalysisState)

    # Add nodes
    graph_builder.add_node("classifier", classify_query)
    graph_builder.add_node("router", router)
    graph_builder.add_node("profiling_agent", profiling_agent.process)
    graph_builder.add_node("statistical_agent", statistical_agent.process)
    graph_builder.add_node("visualization_agent", visualization_agent.process)
    graph_builder.add_node("insight_agent", insight_agent.process)
    graph_builder.add_node("query_agent", query_agent.process)

    # Set entry point
    graph_builder.set_entry_point("classifier")

    # Add edges
    graph_builder.add_edge("classifier", "router")

    # Conditional routing from router
    graph_builder.add_conditional_edges(
        "router",
        lambda state: state["next"],
        {
            "profiling": "profiling_agent",
            "statistical": "statistical_agent",
            "visualization": "visualization_agent",
            "insights": "insight_agent",
            "query": "query_agent"
        }
    )

    # All agents end
    for agent in ["profiling_agent", "statistical_agent",
                  "visualization_agent", "insight_agent", "query_agent"]:
        graph_builder.add_edge(agent, END)

    return graph_builder.compile()
```

### Phase 4: Service Integration (Week 4)

**Update `chat_service.py`**:
```python
class ChatService:
    def __init__(self):
        self.use_langgraph = os.getenv("ANTHROPIC_API_KEY") is not None

        if self.use_langgraph:
            from app.agents.langgraph_workflow import create_data_analysis_graph
            self.workflow = create_data_analysis_graph()
            print("✅ LangGraph multi-agent workflow initialized")
        else:
            self.workflow = None
            print("⚠️ Using fallback responses (no API key)")

    async def process_message(self, user_message: str, analysis_data: Any,
                             conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process with LangGraph workflow or fallback"""

        if self.use_langgraph and self.workflow:
            return await self._process_with_langgraph(
                user_message, analysis_data, conversation_history
            )
        else:
            return self._process_with_fallback(
                user_message, self._build_analysis_context(analysis_data)
            )

    async def _process_with_langgraph(self, user_message: str,
                                     analysis_data: Any,
                                     conversation_history: List[Dict]) -> Dict[str, Any]:
        """Process with LangGraph multi-agent workflow"""

        # Build initial state
        state = {
            "user_message": user_message,
            "conversation_history": conversation_history or [],
            "filename": analysis_data.filename,
            "data_profile": analysis_data.data_profile or {},
            "analysis_results": analysis_data.analysis_results or {},
            "insights": analysis_data.insights or []
        }

        # Run workflow
        result = await self.workflow.ainvoke(state)

        return {
            "content": result["agent_response"],
            "chart_type": result.get("chart_type"),
            "chart_data": result.get("chart_data"),
            "metadata": {
                "agent_used": result.get("agent_used"),
                "query_type": result.get("query_type"),
                "processing_time": result.get("processing_time")
            }
        }
```

## Data Loading Strategy Update

### Critical Fix: Remove full_data Storage

**Current Problem** (simple_workflow.py:39):
```python
"full_data": clean_nan_values(df.to_dict('records'))  # Stores ENTIRE dataset!
```

**New Strategy**:
1. **Never store full_data in database**
2. **Load data on-demand** when agents need it
3. **Use sampling** for large datasets

**Implementation**:
```python
# In each agent's process method
def load_data_for_analysis(file_path: str, max_rows: int = 10000) -> pd.DataFrame:
    """Load data with sampling for large datasets"""

    df = pd.read_csv(file_path)

    if len(df) > max_rows:
        # Sample for large datasets
        df = df.sample(n=max_rows, random_state=42)
        print(f"⚠️ Sampled {max_rows:,} rows from {len(df):,} total")

    return df
```

**Database Schema Changes** (Priority 0 fixes):
```python
# models/database.py - REMOVE full_data field
data_profile = Column(JSON, nullable=True)  # Only store metadata, NOT data
analysis_results = Column(JSON, nullable=True)
insights = Column(JSON, nullable=True)

# Add file reference for on-demand loading
file_path = Column(String, nullable=False)  # Store path to reload when needed
```

## Benefits of LangGraph Architecture

### 1. **Specialized Expertise**
Each agent has focused knowledge:
- Profiling agent understands data structures
- Statistical agent applies mathematical rigor
- Visualization agent knows chart best practices
- Insight agent generates business value
- Query agent handles precise data questions

### 2. **Intelligent Routing**
Queries automatically routed to the right specialist:
- "What does my data look like?" → Profiling Agent
- "Show me correlations" → Statistical Agent
- "Create a bar chart" → Visualization Agent
- "What does this mean?" → Insight Agent
- "Which has the highest value?" → Query Agent

### 3. **Scalability**
Easy to add new agents:
- Trend Analysis Agent (time series)
- ML Recommendation Agent (model suggestions)
- Data Quality Agent (cleaning recommendations)
- Export Agent (format conversions)

### 4. **Maintainability**
- Each agent is independent and testable
- Clear separation of concerns
- Easy to update agent prompts
- Simple to add new capabilities

### 5. **Accurate Resume Claims**
After implementation, you can truthfully say:
- ✅ "Implemented multi-agent LangGraph workflow"
- ✅ "Designed 5 specialized AI agents for data analysis"
- ✅ "Built intelligent query classification and routing system"
- ✅ "Architected StateGraph with conditional agent selection"

## Testing Strategy

### Unit Tests for Each Agent
```python
# tests/test_agents.py
def test_profiling_agent():
    agent = ProfilingAgent()
    state = create_test_state(query="What does my data look like?")
    result = agent.process(state)
    assert result["agent_response"]
    assert "columns" in result["agent_response"].lower()

def test_statistical_agent():
    agent = StatisticalAgent()
    state = create_test_state(query="Show me correlations")
    result = agent.process(state)
    assert result["agent_response"]
    assert result["chart_type"] == "correlation"
```

### Integration Tests
```python
# tests/test_langgraph_workflow.py
@pytest.mark.asyncio
async def test_full_workflow():
    workflow = create_data_analysis_graph()

    state = {
        "user_message": "What patterns are in my data?",
        "data_profile": sample_data_profile,
        "analysis_results": sample_analysis_results
    }

    result = await workflow.ainvoke(state)

    assert result["agent_used"] in [
        "profiling", "statistical", "visualization", "insights", "query"
    ]
    assert result["agent_response"]
```

### Performance Benchmarks
```python
# tests/test_langgraph_performance.py
def test_agent_routing_speed(benchmark):
    """Test classification and routing speed"""
    def classify_and_route():
        state = {"user_message": "Show me correlations"}
        return classify_query(state)

    result = benchmark(classify_and_route)
    # Target: <100ms for classification
    assert benchmark.stats["mean"] < 0.1
```

## Migration Path

### Backward Compatibility

**Keep simple_workflow.py as fallback**:
```python
# main.py or config
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "true").lower() == "true"

if USE_LANGGRAPH:
    from app.agents.langgraph_workflow import run_data_analysis
else:
    from app.agents.simple_workflow import run_data_analysis
```

### Gradual Rollout

1. **Week 1**: Core infrastructure, no user-facing changes
2. **Week 2**: Agent implementation, testing with feature flag
3. **Week 3**: Workflow integration, beta testing
4. **Week 4**: Full deployment, monitoring

### Rollback Plan

If issues arise:
```python
# Set environment variable to disable
USE_LANGGRAPH=false

# Or in code
if LANGGRAPH_ERROR_RATE > 0.05:  # 5% error rate
    print("⚠️ High error rate, falling back to simple_workflow")
    USE_LANGGRAPH = False
```

## Success Metrics

### Performance Targets
- **Classification speed**: <100ms
- **Agent response time**: <2s (with Claude API)
- **End-to-end processing**: <3s
- **Fallback response**: <100ms (no API)

### Quality Targets
- **Correct agent routing**: >95%
- **User satisfaction**: >4.5/5
- **Response accuracy**: >90%
- **Chart appropriateness**: >90%

### Monitoring
```python
# Add to each agent
import time

def process(self, state: DataAnalysisState) -> DataAnalysisState:
    start_time = time.time()

    # Agent processing...

    processing_time = time.time() - start_time
    state["processing_time"] = processing_time
    state["agent_used"] = self.__class__.__name__

    # Log metrics
    logger.info(f"{self.__class__.__name__} processed in {processing_time:.2f}s")

    return state
```

## Next Steps

1. **Review this plan** and provide feedback
2. **Set up development branch**: `git checkout -b feature/langgraph-integration`
3. **Install dependencies**: `uv add langgraph langchain-anthropic langchain-core`
4. **Implement Phase 1**: Core infrastructure
5. **Create agent classes**: One by one with tests
6. **Integration testing**: Full workflow validation
7. **Deploy with feature flag**: Gradual rollout
8. **Update resume**: With accurate LangGraph claims

## Questions to Address

1. **Agent Priorities**: Which agent should be implemented first?
   - Recommendation: Start with Profiling → Statistical → Visualization

2. **Prompt Engineering**: Do you have existing prompts from the chatbot to adapt?
   - Can reuse your therapist/logical/etc. prompt patterns

3. **Error Handling**: How should agent failures be handled?
   - Recommendation: Fallback to simple_workflow on agent error

4. **Conversation Memory**: How much history should agents see?
   - Current: Last 6 messages
   - Recommendation: Keep same, add state persistence for multi-turn analysis

5. **API Rate Limits**: How to handle Claude API throttling?
   - Add exponential backoff
   - Cache common queries
   - Implement request queuing

---

**Ready to start implementation? Let me know which phase you'd like to begin with!**
