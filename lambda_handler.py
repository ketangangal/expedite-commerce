import json
import hashlib
import uvicorn
from fastapi import FastAPI
from config import llm_config
from agents import master_agent
from tool_schemas import SubAgent
from utils import generate_function_schema
from gatekeeper import security_check
from cache import retrieve_feedback_cache, store_feedback_cache
from cw_logger import setup_cloudwatch_logger
from pydantic import BaseModel
from datetime import datetime

logger, cloudwatch_handler = None, None
logger, cloudwatch_handler = setup_cloudwatch_logger()

class Request(BaseModel):
    feedback_id: str
    customer_name: str
    feedback_text: str
    timestamp: str
    instructions: str


def invoke(request: Request):
    logger.info(f"Received request for feedback_id: {request.feedback_id}")
    # Check if the request is cached
    cache_key_name = f"{request.feedback_text}_and_{request.instructions}"
    cache_key = hashlib.sha256(cache_key_name.encode()).hexdigest()
    logger.info(f"Cache key for feedback_id: {request.feedback_id} is: {cache_key}")
    cached_result = retrieve_feedback_cache(request.feedback_id, cache_key, logger)
    if cached_result:
        output = {
            "cache_key": cache_key,
            "feedback_id": request.feedback_id,
            "cached_result": cached_result[cache_key]["cached_result"],
            "last_updated": cached_result[cache_key]["last_updated"]
        }
        logger.info(f"Cache Hit: {output}")
        return output

    # Security check
    logger.info(f"Security check for feedback_id: {request.feedback_id}")
    response = security_check(text=request.model_dump_json(), logger=logger)
    if response["is_blocked"]:
        logger.info(f"Security check failed for feedback_id: {request.feedback_id} with response: {response}")
        return response
    
    logger.info(f"Master agent initiated for feedback_id: {request.feedback_id}")
    response = master_agent(
        input_request=request.model_dump(),
        tools=[generate_function_schema(SubAgent)],
        config=llm_config,
        logger=logger
    )

    logger.info(f"Master agent completed for feedback_id: {request.feedback_id} with response: {response}")
    # Store the response in the cache
    last_updated = store_feedback_cache(request.feedback_id, cache_key, response["agent_response"], logger)
    logger.info(f"Response stored in cache for feedback_id: {request.feedback_id} with cache_key: {cache_key}")
    response["last_updated"] = last_updated
    return response


def batch_invoke(requests: list):
    responses = []
    for request in requests:
        response = invoke(Request(**request))
        responses.append(response)
    return responses

def lambda_handler(event, context):
    stream = event.get("stream", False)
    request = event.get("request", None)
    if stream == "SingleInvoke":
        response = invoke(Request(**request))
        return {'statusCode': 200, 'body': json.dumps(response)}

    elif stream == 'BatchInvoke':
        logger.info(f"Received batch request for {len(request)} requests")
        output = batch_invoke(requests=event["request"])
        return {"message": "Batch request processed successfully", "output": output}

    else:
        logger.error(f"Invalid request: {event}")
        return {"error": "Invalid request"}

