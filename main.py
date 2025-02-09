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
from contextlib import asynccontextmanager

logger, cloudwatch_handler = None, None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global logger, cloudwatch_handler
    logger, cloudwatch_handler = setup_cloudwatch_logger()
    yield
    try:
        logger.removeHandler(cloudwatch_handler)
        cloudwatch_handler.close()
    except Exception as e:
        print(f"Error during cleanup: {e}")

app = FastAPI(lifespan=lifespan)


class Request(BaseModel):
    feedback_id: str
    customer_name: str
    feedback_text: str
    timestamp: str
    instructions: str


@app.post("/invoke")
async def root(request: Request):
    try:
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
    except Exception as e:
        logger.error(f"Error in main with error: {e}")
        return {"error": str(e)}


class BatchRequest(BaseModel):
    requests: list[Request]

@app.post("/batch-invoke")
async def batch_invoke(request: BatchRequest):
    try:
        # TODO: Make parallel requests for faster processing
        # Calculation : number of cores on the machine * 2 (for parallel processing)
        # Example : 4 cores = 8 requests per second
        # TODO: ADD a queue to the requests
        logger.info(f"Received batch request for {len(request.requests)} requests")
        output = []
        for req in request.requests:
            logger.info(f"Processing request: {req.feedback_id}")
            response = await root(req)
            logger.info(f"Response for request: {req.feedback_id} is: {response}")
            output.append(response)
        return {"message": "Batch request processed successfully", "output": output}
    except Exception as e:
        logger.error(f"Error in batch invoke with error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



