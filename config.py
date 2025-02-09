from dotenv import load_dotenv
import os   

# Model Config
load_dotenv()

llm_config = {
    "model": f"azure/{os.getenv('AZURE_DEPLOYMENT')}",
    "api_key": os.getenv("AZURE_API_KEY"),
    "base_url": os.getenv("AZURE_ENDPOINT"),
    "api_version": os.getenv("AZURE_API_VERSION")
}