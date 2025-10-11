from langgraph.graph import StateGraph, START, END
from .data_profiler import (
    DataAnalysisState,
    data_profiler_agent,
    statistical_analyst_agent,
    insights_generator_agent,
)


def create_analysis_workflow():
    """Create the complete data analysis workflow"""

    # Create the workflow graph
    workflow = StateGraph(DataAnalysisState)

    # Add nodes (agents)
    workflow.add_node("profiler", data_profiler_agent)
    workflow.add_node("analyst", statistical_analyst_agent)
    workflow.add_node("insights", insights_generator_agent)

    # Define the flow
    workflow.add_edge(START, "profiler")
    workflow.add_edge("profiler", "analyst")
    workflow.add_edge("analyst", "insights")
    workflow.add_edge("insights", END)

    # Compile the workflow
    return workflow.compile()


# Create a global instance
analysis_workflow = create_analysis_workflow()
