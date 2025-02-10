import boto3
import json
import os
from datetime import datetime


def store_feedback_cache(feedback_id, cache_key, cached_result, logger):
    try:
        TABLE_NAME = "FeedbackCache"
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        
        last_updated = datetime.now().isoformat()
        ttl = int(datetime.now().timestamp()) + 60  # 1 minute

        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "feedback_id": {"S": feedback_id},
                "cache_key": {"S": cache_key},
                "cached_result": {"S": json.dumps(cached_result)},
                "last_updated": {"S": last_updated},
                "ttl": {"N": str(ttl)}
            }
        )
        return last_updated
    except Exception as e:
        logger.error(f"Error storing feedback cache for feedback_id: {feedback_id} with cache_key: {cache_key} with error: {e}")

def retrieve_feedback_cache(feedback_id: str, cache_key=None, logger=None):
    try:
        TABLE_NAME = "FeedbackCache"

        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        
        if cache_key:
            response = dynamodb.get_item(
                TableName=TABLE_NAME,
                Key={
                    "feedback_id": {"S": feedback_id},
                    "cache_key": {"S": cache_key}
                }
            )
            if "Item" in response:
                return {
                    response["Item"]["cache_key"]["S"]: {
                        "cached_result": json.loads(response["Item"]["cached_result"]["S"]),
                        "last_updated": response["Item"]["last_updated"]["S"]
                    }
                }  # Return cached result
            return None
        
        else:
            response = dynamodb.query(
                TableName=TABLE_NAME,
                KeyConditionExpression="feedback_id = :fid",
                ExpressionAttributeValues={":fid": {"S": feedback_id}}
            )
            output = {
                item["cache_key"]["S"]: {
                    "cached_result": json.loads(item["cached_result"]["S"]),
                    "last_updated": item["last_updated"]["S"]
                } for item in response.get("Items", [])
            }
            if output:
                return output
            else:
                return None
    except Exception as e:
        logger.error(f"Error retrieving feedback cache for feedback_id: {feedback_id} with cache_key: {cache_key} with error: {e}")
        return None