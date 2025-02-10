from boto3 import client
import os

def parse_guardrail_response(response: dict, logger=None) -> dict:
    try:
        """
        Parse the Bedrock guardrail response and return a structured explanation
        of why the content was blocked.
        """
        result = {
            "status": response.get("action", "UNKNOWN"),
            "is_blocked": False,
            "reasons": [],
            "details": {}
        }
        
        if response["action"] == "GUARDRAIL_INTERVENED":
            result["is_blocked"] = True
            
            if "assessments" in response:
                for assessment in response["assessments"]:
                    if "contentPolicy" in assessment:
                        filters = assessment["contentPolicy"].get("filters", [])
                        
                        for filter_info in filters:
                            violation = {
                                "type": filter_info.get("type"),
                                "confidence": filter_info.get("confidence"),
                                "strength": filter_info.get("filterStrength"),
                                "action": filter_info.get("action")
                            }
                            result["reasons"].append(violation)
            
            if "guardrailCoverage" in response:
                result["details"]["coverage"] = response["guardrailCoverage"]
                
            if "usage" in response:
                result["details"]["usage"] = response["usage"]
        
        return result
    except Exception as e:
        logger.error(f"Error parsing guardrail response with error: {e}")
        return {"error": str(e)}


def security_check(text: str, logger=None) -> dict:
    try:
        bedrock = client(
            "bedrock-runtime", 
            region_name="us-east-1", 
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), 
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        response = bedrock.apply_guardrail(
            guardrailIdentifier="8j0uvjqavz1m",
            guardrailVersion="1",
            source="INPUT",
                content=[{"text": {"text": text}}] 
            )

        return parse_guardrail_response(response)
    except Exception as e:
        logger.error(f"Error in security check with error: {e}")
        return {"error": str(e)}
