#!/bin/bash

# Force IPv4
ENDPOINT="https://sharedingress-nsk-barge-nonprod-us-west1.nordstrom.app/app10094/looker-ca-agent/query"
PROXY_PORT=8888
PROXY_URL="socks5h://127.0.0.1:$PROXY_PORT"

echo "Checking if port $PROXY_PORT is listening (IPv4)..."
if command -v nc >/dev/null 2>&1; then
    nc -z -v -w 2 127.0.0.1 $PROXY_PORT
else
    echo "nc not found, skipping port check."
fi
echo ""

echo "Testing connectivity to: $ENDPOINT"
echo "Using Proxy: $PROXY_URL"
echo "Timeout set to 10 seconds..."

# Clear any existing proxy vars for this run to be sure
unset ALL_PROXY
unset http_proxy
unset https_proxy

RESPONSE=$(curl -v -s --connect-timeout 10 -X POST "$ENDPOINT" \
  --proxy "$PROXY_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me top 5 items by sales",
    "conversation_id": "test-connectivity-002",
    "reset": true,
    "max_turns": 1
  }' 2>&1)

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Connection established!"
    echo "Response:"
    echo "$RESPONSE" | tail -n 20
else
    echo ""
    echo "❌ FAILED: Could not connect (Exit Code: $EXIT_CODE)"
    echo "Error details:"
    echo "$RESPONSE" | tail -n 10
    echo ""
    echo "TROUBLESHOOTING:"
    echo "1. Verify SOCKS proxy on Mac: 'lsof -i :1337' (Should see LISTEN)"
    echo "2. Verify SSH tunnel (Window 2) is still alive."
    echo "3. Try re-running 'ssh -R 8888:127.0.0.1:1337 ...' on Mac."
fi
