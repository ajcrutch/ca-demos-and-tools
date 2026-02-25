import requests
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

URL = "https://sharedingress-nsk-barge-nonprod-us-west1.nordstrom.app/app10094/looker-ca-agent/query"

def query_agent():
    logging.info("Testing /query endpoint with a simple query...")
    
    payload = {
        "question": "Show me top 5 items by sales",
        "conversation_id": "test-nonprod-001",
        "reset": True,
        "max_turns": 3
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(URL, json=payload, headers=headers)
        response.raise_for_status() # Raise exception for bad status codes
        
        logging.info("Request successful!")
        logging.info("Response Status Code: %s", response.status_code)
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        logging.error("An error occurred while querying the endpoint: %s", e)
        if hasattr(e.response, "text"):
            logging.error("Response text: %s", e.response.text)

if __name__ == "__main__":
    query_agent()
