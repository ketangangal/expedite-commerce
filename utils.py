from pydantic import BaseModel

def generate_function_schema(base_model: BaseModel):
    """Generate a function schema from a Pydantic BaseModel.

    Args:
        base_model (BaseModel): The Pydantic BaseModel to generate the schema from.

    Returns:
        dict: The function schema.
    """
    try:
        schema = base_model.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": schema.get("title", base_model.__name__),
                "description": schema.get("description", "None"),
                "parameters": {
                    "type": schema.get("type", "object"),
                    "properties": schema.get("properties")
                }
            }
        }
    except Exception as e:
        return {"error": str(e)}
