#!/bin/bash
# Script helper để test bot Teams bằng curl
# Sử dụng: ./test_bot_curl.sh

echo "🔐 Testing Bot Teams với curl"
echo "================================"
echo ""

# Check nếu bot đang chạy
if ! curl -s http://localhost:3978/api/messages > /dev/null 2>&1; then
    echo "❌ Bot không chạy trên port 3978!"
    echo "💡 Hãy start bot trước: python src/app.py"
    exit 1
fi

# Generate JWT token
echo "📝 Generating JWT token..."
TOKEN=$(python test_helpers/generate_jwt_token.py | grep -A 1 "✅ JWT Token" | tail -1 | xargs)

if [ -z "$TOKEN" ]; then
    echo "❌ Không thể generate token. Hãy kiểm tra config CLIENT_ID và CLIENT_SECRET"
    exit 1
fi

# Test với curl
echo ""
echo "🧪 Testing bot với message 'Hello'..."
echo ""

curl -X POST \
  'http://localhost:3978/api/messages' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "message",
    "from": {
      "id": "test-user-123",
      "name": "Test User"
    },
    "conversation": {
      "id": "test-conv-123"
    },
    "text": "Hello"
  }'

echo ""
echo ""
echo "✅ Test completed!"

