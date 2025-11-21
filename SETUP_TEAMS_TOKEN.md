# Hướng dẫn Setup Teams Token Authentication

## Tổng quan

Bot Teams này đã được cấu hình để lấy `teams_token` từ user thông qua SSO (Single Sign-On) và gửi xuống backend để xử lý authentication và tích hợp Graph API.

## Các thành phần đã được triển khai

### 1. **Manifest Configuration** (`appPackage/manifest.json`)
- ✅ Đã thêm `webApplicationInfo` để hỗ trợ SSO
- ✅ Đã cấu hình `validDomains` với bot domain

### 2. **Token Service** (`src/token_service.py`)
- ✅ Service để gửi token xuống backend
- ✅ Xử lý HTTP request với error handling

### 3. **SSO Handlers** (`src/app.py`)
- ✅ Handler cho `signin/verifyState` - xử lý SSO verification
- ✅ Handler cho `signin/tokenExchange` - xử lý token exchange
- ✅ Command handler để user có thể trigger authentication bằng cách gõ: `auth`, `authenticate`, `login`, `đăng nhập`, `xác thực`

### 4. **Configuration** (`src/config.py`)
- ✅ Thêm `BACKEND_URL` - URL của backend service
- ✅ Thêm `BACKEND_AUTH_ENDPOINT` - Endpoint để gửi token (mặc định: `/api/auth/teams-token`)

## Setup Requirements

### 1. **Azure AD App Registration**

Bạn cần cấu hình Azure AD App Registration với các quyền sau:

1. Truy cập [Azure Portal](https://portal.azure.com/) > **Azure Active Directory** > **App registrations**
2. Tìm hoặc tạo app registration với `CLIENT_ID` (BOT_ID)
3. Vào **API permissions** và thêm các quyền:
   - `User.Read` (Delegated) - Để đọc thông tin user
   - Các quyền Graph API khác tùy theo nhu cầu
4. **Grant admin consent** cho các quyền
5. Vào **Expose an API**:
   - Set Application ID URI: `api://<BOT_DOMAIN>/<BOT_ID>`
   - Thêm scope nếu cần
6. Vào **Authentication**:
   - Thêm redirect URI: `https://token.botframework.com/.auth/web/redirect`
   - Enable **Access tokens** và **ID tokens**

### 2. **Environment Variables**

Thêm các biến môi trường sau vào file `.env` hoặc Azure App Service Configuration:

```env
# Existing variables
CLIENT_ID=<your-bot-client-id>
CLIENT_SECRET=<your-bot-client-secret>
TENANT_ID=<your-tenant-id>
BOT_TYPE=UserAssignedMsi  # hoặc để trống nếu dùng Client Secret
AZURE_OPENAI_API_KEY=<your-openai-key>
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=<your-model-name>
AZURE_OPENAI_ENDPOINT=<your-openai-endpoint>

# New variables for backend integration
BACKEND_URL=https://your-backend-api.com
BACKEND_AUTH_ENDPOINT=/api/auth/teams-token
```

### 3. **Backend API Endpoint**

Backend của bạn cần có endpoint để nhận token. Ví dụ payload:

**Request:**
```json
POST /api/auth/teams-token
Content-Type: application/json

{
  "teams_token": "eyJ0eXAiOiJKV1QiLCJub...",
  "user_id": "29:1abc...",
  "tenant_id": "12345678-1234-1234-1234-123456789012",
  "conversation_id": "a:1abc...",
  "channel_id": "msteams"
}
```

**Response (success):**
```json
{
  "success": true,
  "message": "Token received and processed",
  "user_info": {
    "id": "29:1abc...",
    "email": "user@example.com"
  }
}
```

**Response (error):**
```json
{
  "error": "Invalid token",
  "message": "Token validation failed"
}
```

### 4. **Backend Implementation Example**

Ví dụ backend endpoint (Python/FastAPI):

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

class TeamsTokenRequest(BaseModel):
    teams_token: str
    user_id: str
    tenant_id: str
    conversation_id: str = None
    channel_id: str = None

@app.post("/api/auth/teams-token")
async def receive_teams_token(request: TeamsTokenRequest):
    """
    Nhận token từ Teams bot và sử dụng để gọi Graph API
    """
    try:
        # Validate token bằng cách gọi Graph API
        async with httpx.AsyncClient() as client:
            # Lấy thông tin user từ Graph API
            response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={
                    "Authorization": f"Bearer {request.teams_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code == 200:
                user_info = response.json()
                
                # Lưu token và user info vào database hoặc cache
                # ... your logic here ...
                
                return {
                    "success": True,
                    "message": "Token received and processed",
                    "user_info": user_info
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token"
                )
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing token: {str(e)}"
        )
```

## Cách sử dụng

### 1. **User trigger authentication**

User có thể gõ các lệnh sau trong Teams chat:
- `auth`
- `authenticate`
- `login`
- `đăng nhập`
- `xác thực`

Bot sẽ tự động:
1. Initiate SSO flow
2. Lấy token từ Teams
3. Gửi token xuống backend
4. Thông báo kết quả cho user

### 2. **Automatic authentication**

SSO flow cũng có thể được trigger tự động khi:
- User lần đầu tương tác với bot
- Bot cần access token để gọi Graph API

## Testing

### Local Testing

1. Đảm bảo bot đang chạy local trên port 3978
2. Sử dụng ngrok hoặc Teams Toolkit để expose bot
3. Test SSO flow trong Teams
4. Kiểm tra logs để xem token có được gửi xuống backend không

### Production Testing

1. Deploy bot lên Azure App Service
2. Cấu hình environment variables
3. Test SSO flow trong Teams production
4. Monitor logs và backend để đảm bảo token được nhận đúng

## Troubleshooting

### Lỗi: "Không thể lấy token"
- Kiểm tra Azure AD App Registration có đúng quyền không
- Kiểm tra `webApplicationInfo` trong manifest có đúng không
- Kiểm tra redirect URI trong Azure AD

### Lỗi: "Backend URL not configured"
- Đảm bảo `BACKEND_URL` đã được set trong environment variables
- Kiểm tra backend có đang chạy và accessible không

### Lỗi: "Token validation failed"
- Kiểm tra token có hợp lệ không
- Kiểm tra token có đúng scope không (User.Read)
- Kiểm tra backend có thể gọi Graph API với token không

## Security Considerations

1. **Token Storage**: Không lưu token trong plain text, sử dụng encryption
2. **HTTPS Only**: Đảm bảo tất cả communication đều qua HTTPS
3. **Token Expiry**: Xử lý token expiry và refresh token nếu cần
4. **Validation**: Luôn validate token trước khi sử dụng
5. **Scope**: Chỉ request các scope cần thiết

## Next Steps

1. ✅ Setup Azure AD App Registration
2. ✅ Configure environment variables
3. ✅ Implement backend endpoint
4. ✅ Test SSO flow
5. ✅ Integrate Graph API calls trong backend
6. ✅ Add token refresh logic nếu cần
7. ✅ Add error handling và retry logic

## Tài liệu tham khảo

- [Microsoft Teams SSO Documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/bots/how-to/authentication/auth-aad-sso-bots)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/overview)
- [Microsoft Teams SDK Python](https://github.com/microsoft/teams-ai-python)

