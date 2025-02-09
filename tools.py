from litellm import completion
import json


# Sentiment Analysis Tool
def sentiment_analysis_tool(query: str, config: dict, logger=None):
    try:
        # Prompt
        prompt = """Analyze the sentiment of the following user feedback and provide a JSON response with sentiment scores for positive, negative, and neutral categories. 
        
        NOTE: Ensure the sum of all values equals 1. Do not provide any explanation.  

        Output format:  
        ```json  
        {{ "positive": <score>, "negative": <score>, "neutral": <score>}}
        ```

        Feedback: {user_feedback}
        """.format(user_feedback=query)

        response = completion(
            **config, 
            messages=[
                {"role": "user", "content": prompt},
                ]
        )

        # Parsing and Loading
        output = response.choices[0].message.content.strip("```json").strip('```')[1:-1]
        return json.loads(output)
    except Exception as e:
        logger.error(f"Error in sentiment analysis tool with error: {e}")
        return {"error": str(e)}


# Topic Categorization Tool
def topic_categorization_tool(query: str, config: dict, logger=None):
    try:
        # Prompt
        prompt = """Categorize the following user feedback into one of the predefined topics: `Product Quality`, `Delivery`, `Support`.
    
        NOTE: Select only one category and assign it a confidence score between 0 and 1. 
        Do not provide any explanation.  

        Output format:  
        ```json  
        {{ "category": <Selected Category>, "score": <confidence_score>}}
        ```"  

        Feedback: {product_info}
        """.format(product_info=query)

        response = completion(
            **config, 
            messages=[
                {"role": "user", "content": prompt},
                ]
        )

        # Parsing and Loading
        output = response.choices[0].message.content.strip("```json").strip('```')[1:-1]
        return json.loads(output)
    except Exception as e:
        logger.error(f"Error in topic categorization tool with error: {e}")
        return {"error": str(e)}


# Keyword Contextualization Tool
def keyword_contextualization_tool(query: str, config: dict, logger=None):
    try:
        # Prompt
        prompt = """Extract context-aware keywords from the following user feedback along with their relevance scores. 
        
        NOTE: Provide a JSON response where each keyword is mapped to a relevance score between 0 and 1. 
        Do not provide any explanation. 

        Output format:  
        ```json  
        {{ "keywords": {{ "<keyword1>": <score>, "<keyword2>": <score>, "<keyword3>": <score> }}}}
        ```"  

        Feedback: {user_feedback}
        """.format(user_feedback=query)

        response = completion(
            **config, 
            messages=[
                {"role": "user", "content": prompt},
                ]
        )

        # Parsing and Loading
        output = response.choices[0].message.content.strip("```json").strip('```')[1:-1]
        return json.loads(output)
    except Exception as e:
        logger.error(f"Error in keyword contextualization tool with error: {e}")
        return {"error": str(e)}


# Summarization Tool
def summarization_tool(query: str, config: dict, logger=None):
    try:
        # Prompt
        prompt = """Summarize the following user feedback concisely and provide actionable recommendations. 
        
        NOTE: Ensure the summary captures the core message, and the recommendations are practical and relevant. 
        Do not provide any explanation.  

        Output format:  
        ```json  
        {{  
        "summary": "<short concise summary>",  
        "recommendations": ["<short actionable recommendation 1>", "<short actionable recommendation 2>"]  
        }}  
        ```"  

        Feedback: {user_feedback}
        """.format(user_feedback=query)

        response = completion(
            **config, 
            messages=[
                {"role": "user", "content": prompt},
                ]
        )

        # Parsing and Loading
        output = response.choices[0].message.content.strip("```json").strip('```')[1:-1]
        return json.loads(output)
    except Exception as e:
        logger.error(f"Error in summarization tool with error: {e}")
        return {"error": str(e)}
