from tools.tool_executor import ToolExecutor
from litellm import completion

# Master Agent
def master_agent(input_request: dict, tools: list, config: dict, logger=None):
    try:
        # This is master agent Prompt
        prompt = """You are a master agent responsible for handling general user interactions, greetings, and generic inquiries. 
        However, when the user provides instructions or mentions product-related details, you must delegate the task to a specialized sub-agent.  

        NOTE:
        - If the input is a general inquiry, greeting, or small talk, respond directly.  
        - If the user input contains instructions or product-related details, do not respond directly. 
        Instead, forward the request to the sub-agent using the exact instruction and feedback text provided by the user.
        - Make sure you only call sub-agent once.
        - Ensure responses are clear and structured.

        This keeps the master agent focused on general conversations while offloading specific tasks to the sub-agent.

        USER_INPUTS:
            Feedback_text: {feedback_text}
            Instructions: {instructions}
        """.format(
            feedback_text=input_request.get("feedback_text", "N/A"),
            instructions=input_request.get("instructions", "N/A")
        )

        logger.info(f"Master Agent LLM call initiated for feedback_id: {input_request.get('feedback_id', 'N/A')}")
        # LLm call
        response = completion(
            **config, 
            messages=[{"role": "user", "content": prompt}],
            tools=tools
        )

        logger.info(f"Master Agent Response : {response.json()}")

        # sub agent call
        if response.choices[0].message.tool_calls:
            logger.info(f"Number of tool calls : {len(response.choices[0].message.tool_calls)}")
            master_tools_executor = ToolExecutor(config=config)
            result = master_tools_executor(
                input_request=input_request, 
                tool_calls=response.choices[0].message.tool_calls,
                logger=logger
            )
            logger.info(f"Master Agent Final Answer: {result}")
            input_request["agent_response"] = result["agent_response"][0]["subagent"]
            return result
        input_request["agent_response"] = [response.choices[0].message.content]

        logger.info(f"Master Agent Final Answer: {input_request}")
        return input_request
    except Exception as e:
        logger.error(f"Error in master agent for feedback_id: {input_request.get('feedback_id', 'N/A')} with error: {e}")
        return {"error": str(e)}


# Sub Agent
def sub_agent(input_request: dict, tools: list, config: dict, logger=None):
    try:
        logger.info(f"Sub Agent initiated for feedback_id: {input_request.get('feedback_id', 'N/A')}")
        prompt = """You are a specialized sub-agent equipped with four tools:  

        1. SentimentAnalysisTool – Analyzes sentiment (positive, negative, neutral) with confidence scores.  
        2. TopicCategorizationTool – Categorizes feedback into predefined topics (`Product Quality`, `Delivery`, `Support`).  
        3. KeywordContextualizationTool – Extracts context-aware keywords with relevance scores.  
        4. SummarizationTool – Generates concise summaries and actionable recommendations.  

        Your task is to answer the user based on feedback and instruction given.   
            - If an instruction is provided, select only the relevant tools accordingly.  
            - If no instruction is provided, use **all four tools** to extract comprehensive insights.  
            - You can use multiple tools at once when necessary.  

        #### **User Input:**  
            Feedback_text : {feedback_text}
            Instruction : {instructions}
        """.format(
            feedback_text=input_request.get("feedback_text", "N/A"),
            instructions=input_request.get("instructions", "N/A")
        )

        # LLm call
        logger.info(f"Sub Agent LLM call initiated for feedback_id: {input_request.get('feedback_id', 'N/A')}")
        response = completion(
            **config, 
            messages=[
                {"role": "user", "content": prompt},
                ],
            tools=tools
        )
        
        logger.info(f"Sub Agent Response : {response}")
        
        # sub agent call
        if response.choices[0].message.tool_calls:
            sub_agent_tools_executor = ToolExecutor(config=config)
            result = sub_agent_tools_executor(
                input_request=input_request, 
                tool_calls=response.choices[0].message.tool_calls,
                logger=logger
            )
            logger.info(f"Sub Agent Final Answer: {result}")
            return result["agent_response"]
        
        logger.info(f"Sub Agent Final Answer: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in sub agent for feedback_id: {input_request.get('feedback_id', 'N/A')} with error: {e}")
        return {"error": str(e)}
