import requests
import json
import time

endpoint_url = "https://sharedingress-nsk-barge-nonprod-us-west1.nordstrom.app/app10094/looker-ca-agent/query"
question = "How are my gifting categories performing to plan?"

payload = {
    "question": question,
    "conversation_id": "test-session",
    "reset": True,
    "max_turns": 3
}

headers = {
    "Content-Type": "application/json"
}

print(f"Sending request to {endpoint_url}...")
print(f"Question: '{question}'")
start_time = time.time()
try:
    response = requests.post(endpoint_url, json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    end_time = time.time()
    total_duration_ms = int((end_time - start_time) * 1000)
    
    print(f"Success! Request took {total_duration_ms}ms")
    
    # Save the payload
    out_file = "custom_agent_payload.json"
    with open(out_file, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Payload saved to {out_file}. Please give this file content back to Jetski!")
    
except Exception as e:
    print(f"Error occurred: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response content: {e.response.text}")
