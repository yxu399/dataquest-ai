# backend/app/services/chat_service.py
"""Chat service for processing user messages and providing AI-driven responses"""

import json
import os
from typing import Dict, Any, List, Optional
import pandas as pd

class ChatService:
    def __init__(self):
        # Initialize Anthropic client with fallback
        self.client = None
        self.use_ai = False
        
        try:
            from anthropic import Anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = Anthropic(api_key=api_key)
                self.use_ai = True
                print("✅ Anthropic client initialized successfully")
            else:
                print("⚠️ ANTHROPIC_API_KEY not found, using fallback responses")
        except Exception as e:
            print(f"⚠️ Error initializing Anthropic client: {e}")
            print("🔄 Using fallback chat responses")
    
    async def process_message(
        self,
        user_message: str,
        analysis_data: Any,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Process user message with analysis context"""
        
        try:
            # Extract analysis context
            context = self._build_analysis_context(analysis_data)
            
            # Use AI if available, otherwise use intelligent fallback
            if self.use_ai and self.client:
                return await self._process_with_ai(user_message, context, conversation_history)
            else:
                return self._process_with_fallback(user_message, context)
                
        except Exception as e:
            print(f"Chat service error: {e}")
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}",
                "error": str(e)
            }
    
    async def _process_with_ai(self, user_message: str, context: Dict, conversation_history: List = None) -> Dict[str, Any]:
        """Process with Claude AI"""
        
        try:
            # Build conversation context
            conversation_context = self._build_conversation_context(conversation_history or [])
            
            # Create prompts
            system_prompt = self._create_system_prompt(context)
            user_prompt = self._create_user_prompt(user_message, context)
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    *conversation_context,
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            claude_response = response.content[0].text
            return self._parse_claude_response(claude_response, context)
            
        except Exception as e:
            print(f"AI processing error: {e}")
            # Fallback to rule-based response
            return self._process_with_fallback(user_message, context)
    
    def _process_with_fallback(self, user_message: str, context: Dict) -> Dict[str, Any]:
        """Intelligent fallback responses using data context"""
        
        message_lower = user_message.lower()
        data_profile = context["data_profile"]
        analysis_results = context["analysis_results"]
        insights = context["insights"]
        
        # Extract potential column names from the user's message
        column_mentions = self._extract_column_mentions(user_message, data_profile)
        
        # Handle column-specific questions
        if column_mentions:
            return self._handle_column_specific_query(user_message, column_mentions, context)
        
        # Key insights request
        if any(word in message_lower for word in ["insight", "key", "finding", "summary"]):
            insight_text = "Here are the key insights from your data:\n\n"
            if insights:
                for i, insight in enumerate(insights[:5], 1):
                    insight_text += f"{i}. {insight}\n"
            else:
                insight_text += "• Dataset contains {} rows and {} columns\n".format(
                    data_profile.get("shape", [0, 0])[0],
                    data_profile.get("shape", [0, 0])[1]
                )
                if analysis_results.get("summary", {}).get("missing_percentage", 0) > 0:
                    insight_text += f"• {analysis_results['summary']['missing_percentage']}% missing data detected\n"
                else:
                    insight_text += "• Complete dataset with no missing values\n"
                
                corr_count = len(analysis_results.get("correlations", []))
                if corr_count > 0:
                    insight_text += f"• Found {corr_count} strong correlations between variables\n"
            
            return {
                "content": insight_text.strip(),
                "chart_type": None
            }
        
        # Correlation requests
        if any(word in message_lower for word in ["correlation", "relationship", "heatmap"]):
            corr_count = len(analysis_results.get("correlations", []))
            if corr_count > 0:
                content = f"I found {corr_count} strong correlations in your dataset. The correlation heatmap will show relationships between all numeric variables. CHART_SUGGESTION: correlation"
                return {
                    "content": content,
                    "chart_type": "correlation"
                }
            else:
                return {
                    "content": "No strong correlations were detected in your dataset.",
                    "chart_type": None
                }
        
        # Bar chart requests
        if any(word in message_lower for word in ["bar", "categor", "distribution"]) and "numeric" not in message_lower:
            cat_cols = len(data_profile.get("categorical_columns", []))
            if cat_cols > 0:
                return {
                    "content": f"I'll show you the distribution of your categorical data. You have {cat_cols} categorical columns to explore.",
                    "chart_type": "bar"
                }
            else:
                return {
                    "content": "No categorical columns found in your dataset for bar charts.",
                    "chart_type": None
                }
        
        # Scatter plot requests
        if any(word in message_lower for word in ["scatter", "relationship", "numeric"]):
            num_cols = len(data_profile.get("numeric_columns", []))
            if num_cols >= 2:
                return {
                    "content": f"I'll create a scatter plot to explore relationships between your {num_cols} numeric variables. CHART_SUGGESTION: scatter",
                    "chart_type": "scatter"
                }
            else:
                return {
                    "content": "You need at least 2 numeric columns for scatter plots.",
                    "chart_type": None
                }
        
        # Histogram requests
        if any(word in message_lower for word in ["histogram", "distribution", "spread"]):
            num_cols = len(data_profile.get("numeric_columns", []))
            if num_cols > 0:
                return {
                    "content": f"I'll show you the distribution of your numeric data using histograms. You have {num_cols} numeric columns available.",
                    "chart_type": "histogram"
                }
            else:
                return {
                    "content": "No numeric columns found for histogram visualization.",
                    "chart_type": None
                }
        
        # Box plot requests
        if any(word in message_lower for word in ["box", "boxplot", "summary", "quartile"]):
            num_cols = len(data_profile.get("numeric_columns", []))
            if num_cols > 0:
                return {
                    "content": f"I'll create box plots showing statistical summaries (quartiles, median, outliers) for your {num_cols} numeric columns.",
                    "chart_type": "boxplot"
                }
            else:
                return {
                    "content": "No numeric columns found for box plot visualization.",
                    "chart_type": None
                }
        
        # Default helpful response
        available_charts = context["available_charts"]
        chart_list = ", ".join(available_charts) if available_charts else "basic charts"
        
        return {
            "content": f"""I'm here to help you explore your dataset! Your data has {data_profile.get("shape", [0, 0])[0]} rows and {data_profile.get("shape", [0, 0])[1]} columns.

I can help you with:
• View key insights from your analysis
• Create visualizations: {chart_list}
• Explore specific columns or relationships

Try asking me things like:
• "Show me the key insights"
• "Create a correlation heatmap"
• "Show distribution of [column name]"
• "Compare [column1] and [column2]"

What would you like to explore?""",
            "chart_type": None
        }
    
    def _build_analysis_context(self, analysis_data) -> Dict[str, Any]:
        """Build context from analysis results"""
        
        context = {
            "filename": analysis_data.filename,
            "status": analysis_data.status,
            "data_profile": analysis_data.data_profile or {},
            "analysis_results": analysis_data.analysis_results or {},
            "insights": analysis_data.insights or [],
            "available_charts": []
        }
        
        # Determine available chart types
        data_profile = context["data_profile"]
        analysis_results = context["analysis_results"]
        
        if data_profile.get("numeric_columns"):
            context["available_charts"].extend(["scatter", "histogram", "boxplot"])
        
        if data_profile.get("categorical_columns"):
            context["available_charts"].append("bar")
        
        if analysis_results.get("correlations"):
            context["available_charts"].append("correlation")
        
        return context
    
    def _build_conversation_context(self, conversation_history: List[Dict]) -> List[Dict]:
        """Convert conversation history to Claude message format"""
        messages = []
        for msg in conversation_history[-6:]:
            if msg.get("type") == "user":
                messages.append({"role": "user", "content": msg.get("content", "")})
            elif msg.get("type") == "assistant":
                messages.append({"role": "assistant", "content": msg.get("content", "")})
        return messages
    
    def _create_system_prompt(self, context: Dict[str, Any]) -> str:
        """Create system prompt for Claude"""
        data_profile = context["data_profile"]
        analysis_results = context["analysis_results"]
        insights = context["insights"]
        available_charts = context["available_charts"]
        
        return f"""You are an expert data analyst AI assistant helping users explore their dataset through natural language conversation.

DATASET CONTEXT:
- Filename: {context["filename"]}
- Shape: {data_profile.get("shape", "Unknown")} (rows × columns)
- Numeric columns: {data_profile.get("numeric_columns", [])}
- Categorical columns: {data_profile.get("categorical_columns", [])}
- Missing data: {data_profile.get("missing_data", {})}

ANALYSIS RESULTS:
- Correlations found: {len(analysis_results.get("correlations", []))}
- Statistical summary: {analysis_results.get("summary", {})}
- Key insights: {insights[:3] if insights else ["No insights available"]}

AVAILABLE VISUALIZATIONS: {available_charts}

When suggesting a chart, end your response with: CHART_SUGGESTION: [chart_type]

Provide specific, data-driven insights based on actual analysis results."""
    
    def _create_user_prompt(self, user_message: str, context: Dict[str, Any]) -> str:
        """Create user prompt with context"""
        return f'User question: "{user_message}"\n\nAnalyze this question in the context of the dataset and provide a helpful response.'
    
    def _parse_claude_response(self, claude_response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response"""
        response_data = {
            "content": claude_response,
            "chart_type": None,
            "chart_data": None,
            "analysis": None
        }
        
        if "CHART_SUGGESTION:" in claude_response:
            parts = claude_response.split("CHART_SUGGESTION:")
            response_data["content"] = parts[0].strip()
            chart_type = parts[1].strip().lower()
            
            if chart_type in context["available_charts"]:
                response_data["chart_type"] = chart_type
                response_data["chart_data"] = self._get_chart_data(chart_type, context)
        
        return response_data
    
    def _get_chart_data(self, chart_type: str, context: Dict[str, Any]) -> Optional[Dict]:
        """Get chart data based on type"""
        analysis_results = context["analysis_results"]
        data_profile = context["data_profile"]
        
        if chart_type == "correlation":
            return analysis_results.get("correlations", [])
        elif chart_type == "bar":
            return analysis_results.get("categorical_distribution", {})
        elif chart_type in ["scatter", "histogram", "boxplot"]:
            return {
                "numeric_columns": data_profile.get("numeric_columns", []),
                "sample_data": data_profile.get("sample_data", []),
                "full_data": data_profile.get("full_data", [])
            }
        return None
    
    def _extract_column_mentions(self, user_message: str, data_profile: Dict) -> List[str]:
        """Extract potential column names from user message"""
        mentions = []
        message_lower = user_message.lower()
        
        # Get all available columns
        all_columns = []
        all_columns.extend(data_profile.get("numeric_columns", []))
        all_columns.extend(data_profile.get("categorical_columns", []))
        
        # Look for exact column name matches
        for column in all_columns:
            if column.lower() in message_lower:
                mentions.append(column)
        
        # Look for partial matches or related terms
        column_keywords = {
            "department": ["department", "dept", "division", "team", "group"],
            "project": ["project", "proj", "initiative", "task"],
            "count": ["count", "number", "quantity", "total", "amount"],
            "salary": ["salary", "wage", "pay", "income", "compensation"],
            "age": ["age", "years", "year old"],
            "city": ["city", "location", "place", "area"],
            "name": ["name", "title", "label"]
        }
        
        for column in all_columns:
            column_lower = column.lower()
            if column_lower in column_keywords:
                keywords = column_keywords[column_lower]
                if any(keyword in message_lower for keyword in keywords):
                    if column not in mentions:
                        mentions.append(column)
        
        return mentions
    
    def _handle_column_specific_query(self, user_message: str, columns: List[str], context: Dict) -> Dict[str, Any]:
        """Handle queries about specific columns"""
        message_lower = user_message.lower()
        data_profile = context["data_profile"]
        analysis_results = context["analysis_results"]
        
        # Check if asking about variation/distribution
        if any(word in message_lower for word in ["vary", "varies", "variation", "distribution", "different", "across"]):
            # Determine appropriate chart type
            categorical_cols = [col for col in columns if col in data_profile.get("categorical_columns", [])]
            numeric_cols = [col for col in columns if col in data_profile.get("numeric_columns", [])]
            
            if categorical_cols and numeric_cols:
                # Group by categorical, analyze numeric - use boxplot for better visualization
                return {
                    "content": f"I can show you how {', '.join(numeric_cols)} varies across different {', '.join(categorical_cols)}. A box plot would be perfect to show the distribution of {', '.join(numeric_cols)} for each {', '.join(categorical_cols)} category.",
                    "chart_type": "boxplot",
                    "chart_data": self._get_chart_data("boxplot", context)
                }
            elif len(categorical_cols) >= 1:
                # Distribution of categories
                return {
                    "content": f"I can show you the distribution of {', '.join(categorical_cols)} using a bar chart to see how values are distributed across different categories.",
                    "chart_type": "bar"
                }
            elif len(numeric_cols) >= 1:
                # Distribution of numeric values
                return {
                    "content": f"I can show you how {', '.join(numeric_cols)} is distributed using a histogram to see the pattern of values.",
                    "chart_type": "histogram"
                }
        
        # Check if asking about relationships
        if any(word in message_lower for word in ["relationship", "correlation", "relate", "connection", "between"]):
            if len(columns) >= 2:
                return {
                    "content": f"I can analyze the relationship between {' and '.join(columns)}. Let me show you a correlation analysis.",
                    "chart_type": "scatter" if len(columns) == 2 else "correlation"
                }
        
        # Default response about specific columns
        if len(columns) == 1:
            col = columns[0]
            col_type = "numeric" if col in data_profile.get("numeric_columns", []) else "categorical"
            return {
                "content": f"I found the '{col}' column in your dataset. This is a {col_type} variable. You can explore its distribution, summary statistics, or relationships with other variables. What specific analysis would you like?",
                "chart_type": "histogram" if col_type == "numeric" else "bar"
            }
        else:
            return {
                "content": f"I found these columns in your dataset: {', '.join(columns)}. I can help you explore their distributions, relationships, or create visualizations. What would you like to analyze?",
                "chart_type": "correlation" if len(columns) > 2 else "scatter"
            }
