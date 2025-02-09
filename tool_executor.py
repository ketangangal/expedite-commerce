import json
from utils import generate_function_schema
from tools import *
from tool_schemas import *


class ToolExecutor:
    def __init__(self, config: dict) -> None:
        from agents import sub_agent
        self.config = config
        self.tools = [
            (SubAgent, sub_agent),
            (SentimentAnalysisTool, sentiment_analysis_tool),
            (TopicCategorizationTool, topic_categorization_tool),
            (KeywordContextualizationTool, keyword_contextualization_tool),
            (SummarizationTool, summarization_tool)
        ]
        self.tools_by_name = {schema.model_json_schema().get("title", "N/A"): tool for schema, tool in self.tools}

        # sub agent tools
        sub_agent_tools = [SentimentAnalysisTool, TopicCategorizationTool, KeywordContextualizationTool, SummarizationTool]
        self.sub_agent_tools = [generate_function_schema(base_model=schema) for schema in sub_agent_tools]

    def __call__(self, input_request: dict, tool_calls: list, logger=None):
        try:
            output = []
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Action Name: {tool_name}\nAction Input: {tool_args}")
                
                if tool_name != "SubAgent":
                    tool_result = self.tools_by_name[tool_name](**tool_args, config=self.config, logger=logger)
                else:
                    tool_result = self.tools_by_name[tool_name](
                        input_request=input_request,
                        tools = self.sub_agent_tools,
                        config=self.config,
                        logger=logger
                        )
                    
                logger.info(f"Action Result: {tool_result}")
                output.append({f'{tool_name.lower().replace("tool","")}': tool_result})
            input_request["agent_response"] = output
            return input_request
        except Exception as e:
            logger.error(f"Error in tool executor with error: {e}")
            return {"error": str(e)}

    

