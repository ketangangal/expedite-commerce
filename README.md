# expedite-commerce

## Architecture Diagram 
## Overview

### Agents
| Agent Request | Description |
|-----------------|-------------|
| Master Agent | Analyze customer feedback to and response to customer |
| Sub Agent | Analyze customer feedback and instructions and call tools |

### Tools
| Tool Request | Description |
|-----------------|-------------|
| Sentiment Analysis | Analyze customer feedback to identify trends and areas for improvement |
| Keyword Extraction | Extract keywords from customer feedback |
| Summary | Summarize customer feedback |
| Topic Categorization | Categorize customer feedback into predefined topics |

### Security
| Security Request | Description |
|-----------------|-------------|
| Security Check | Check if the request is secure using guardrails |

### Cache
| Cache Request | Description |
|-----------------|-------------|
| Cache Check | Check if the request is cached using DynamoDB |
| Cache Store | Store the request in the cache using DynamoDB |
| Cache Retrieve | Retrieve the request from the cache using DynamoDB |

### Cloudwatch Monitoring
| Cloudwatch Request | Description |
|-----------------|-------------|
| Cloudwatch Log | Log the calls to cloudwatch |


## API
| API Request | Description |
|-----------------|-------------|
| API Call | Call the FastAPI application | 
| Batch API Call | Call the FastAPI application in batch |

### Single Invoke
```json
{
  "stream": "SingleInvoke",
  "request": {
    "feedback_id": "15345",
    "customer_name": "John Doe",
    "feedback_text": "The product is great, but the delivery was delayed.",
    "timestamp": "2025-01-10T10:30:00Z",
    "instructions": "Focus on identifying the sentiment and summarizing actionable insights."
  }
}
```

### Batch Invoke
```json
{
  "stream": "BatchInvoke",
  "request": [
    {
      "feedback_id": "15345",
      "customer_name": "John Doe",
      "feedback_text": "The product is great, but the delivery was delayed.",
      "timestamp": "2025-01-10T10:30:00Z",
      "instructions": "Focus on identifying the sentiment and summarizing actionable insights."
    }
  ]
}
```

## Deployment
Deploy the FastAPI application using AWS Lambda and API Gateway.


