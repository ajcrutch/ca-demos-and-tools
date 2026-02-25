import requests
import time
import logging
from typing import Any
from prism.common.schemas.trace import AskQuestionResponse, DurationMetrics

logger = logging.getLogger(__name__)

class CustomApiClient:
    """Client for interacting with a Custom Agent API endpoint."""

    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url

    def ask_question(self, agent_id: str, question: str, client_id: str | None = None, client_secret: str | None = None) -> AskQuestionResponse:
        """Sends a question to the custom API and returns a standard formatted response."""
        
        # Prepare the payload identical to the expected curl command
        payload = {
            "question": question,
            "conversation_id": "test-session",
            "reset": True,
            "max_turns": 3
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.endpoint_url,
                json=payload,
                headers=headers,
                timeout=120  # Looker queries can take some time
            )
            response.raise_for_status()
            data = response.json()
            
            end_time = time.time()
            total_duration_ms = int((end_time - start_time) * 1000)
            
            # Map Custom Agent Output to a standard Gemini Data Analytics Message Mock
            # These fields align with the JSON structure returned by our internal looker-ca-agent
            messages = []
            
            # 1. System Message (Text)
            if data.get("summary"):
                messages.append({
                    "system_message": {
                        "text": {
                            "parts": [data["summary"]]
                        }
                    }
                })
                
            # 2. System Message (Data/Looker Query information)
            looker_query = {}
            if data.get("payload"):
                payload_data = data["payload"]
                looker_query = {
                    "model": payload_data.get("model"),
                    "explore": payload_data.get("explore"),
                    "fields": payload_data.get("fields", []),
                    "limit": str(payload_data.get("limit", "500")),
                    "sorts": payload_data.get("sorts", [])
                }
                
                # Handle filter transformation if present
                if payload_data.get("filters"):
                    filters_list = []
                    for k, v in payload_data["filters"].items():
                        filters_list.append({"field": k, "value": str(v)})
                    looker_query["filters"] = filters_list
                    
                messages.append({
                    "system_message": {
                        "data": {
                            "query": {
                                "looker": looker_query
                            },
                        }
                    }
                })

            # Check if there's any raw text / grounded text or fallback which can act as a textual alternative
            if data.get("results"):
                 # We can embed the result data snippet in the system data message as well if needed
                 pass

            duration_metrics = DurationMetrics(
                time_to_first_response=total_duration_ms, # We don't have streaming, so TTL is total duration
                total_duration=total_duration_ms
            )

            return AskQuestionResponse(
                response=messages,
                duration=duration_metrics
            )

        except requests.exceptions.RequestException as e:
            logger.error("Error connecting to custom API agent: %s", e)
            end_time = time.time()
            total_duration_ms = int((end_time - start_time) * 1000)
            
            return AskQuestionResponse(
                response=[],
                duration=DurationMetrics(total_duration=total_duration_ms),
                error_message=str(e)
            )
