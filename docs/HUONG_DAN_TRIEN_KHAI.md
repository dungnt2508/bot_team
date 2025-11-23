# 🚀 Hướng dẫn Triển khai Bot Assistant Microsoft Teams

## 📋 Tổng quan

Codebase này đã được setup sẵn để tạo một **Bot Assistant** trong Microsoft Teams với các tính năng:
- ✅ AI Chat Assistant sử dụng Azure OpenAI hoặc LiteLLM
- ✅ SSO (Single Sign-On) authentication
- ✅ Tích hợp với backend để gửi Teams token
- ✅ Stateful conversation (nhớ lịch sử chat)
- ✅ Hỗ trợ personal chat, group chat, và team chat

## ✅ Đánh giá Codebase

### **KẾT LUẬN: Codebase HOÀN TOÀN CÓ THỂ triển khai!**

Codebase đã có đầy đủ:
- ✅ Microsoft Teams Bot Framework setup
- ✅ Azure Identity Integration (Managed Identity)
- ✅ SSO handlers đã được implement
- ✅ Token service để gửi token xuống backend
- ✅ Configuration management với dotenv
- ✅ Requirements.txt với đầy đủ dependencies

### Cấu trúc Project

```
bot_team/
├── src/
│   ├── app.py              # Main bot application với SSO handlers
│   ├── config.py           # Configuration management
│   ├── token_service.py    # Service gửi token xuống backend
│   ├── instructions.txt    # AI prompt instructions
│   └── requirements.txt    # Python dependencies
├── appPackage/
│   └── manifest.json       # Teams app manifest (đã có SSO config)
├── env/
│   └── .env.local.user     # ⚠️ BẠN CẦN TẠO FILE NÀY
├── infra/                   # Azure infrastructure templates
├── m365agents.yml          # Teams Toolkit configuration
└── start_bot.py            # Script để chạy bot local
```

## 🎯 Các bước Triển khai

### **BƯỚC 1: Cài đặt Prerequisites**

#### 1.1. Cài đặt Python và Dependencies

```bash
# Đảm bảo Python >= 3.12, < 3.14
python --version

# Tạo virtual environment (nếu chưa có)
cd bot_team
python -m venv env

# Activate virtual environment
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Cài đặt dependencies
pip install -r src/requirements.txt
```

#### 1.2. Cài đặt Microsoft 365 Agents Toolkit

**Option A: VS Code Extension (Khuyến nghị)**
- Cài đặt extension: [Microsoft 365 Agents Toolkit](https://aka.ms/teams-toolkit)
- Version: latest

**Option B: CLI**
- Cài đặt: [Microsoft 365 Agents Toolkit CLI](https://aka.ms/teams-toolkit-cli)

#### 1.3. Tài khoản cần thiết

- ✅ [Azure OpenAI](https://aka.ms/oai/access) account (hoặc LiteLLM proxy)
- ✅ [Microsoft 365 account](https://docs.microsoft.com/microsoftteams/platform/toolkit/accounts) cho development
- ✅ Azure subscription (cho deployment)

---

### **BƯỚC 2: Cấu hình Environment Variables**

#### 2.1. Tạo file `.env.local.user`

**QUAN TRỌNG**: File này chứa secrets và không được commit lên Git.

```bash
cd bot_team/env
# Tạo file .env.local.user
```

Nội dung file `env/.env.local.user`:

```env
# ============================================
# Azure OpenAI Configuration (Option 1)
# ============================================
SECRET_AZURE_OPENAI_API_KEY=your-azure-openai-key-here
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=your-model-name
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# ============================================
# LiteLLM Proxy Configuration (Option 2 - Nếu dùng LiteLLM)
# ============================================
# LITELLM_API_KEY=your-litellm-key
# LITELLM_BASE_URL=https://your-litellm-proxy.com
# LITELLM_DEFAULT_CHAT_MODEL=gpt-4
# LITELLM_DEFAULT_EMBEDDING_MODEL=text-embedding-ada-002

# ============================================
# Backend Integration (Cho Teams Token)
# ============================================
BACKEND_URL=https://your-backend-api.com
BACKEND_AUTH_ENDPOINT=/api/auth/teams-token

# ============================================
# Bot Configuration (Sẽ được tự động tạo bởi Teams Toolkit)
# ============================================
# CLIENT_ID=... (tự động tạo)
# CLIENT_SECRET=... (tự động tạo)
# TENANT_ID=... (tự động tạo)
# BOT_TYPE=UserAssignedMsi (hoặc để trống)
```

**Lưu ý**: 
- Chọn **MỘT** trong hai options: Azure OpenAI HOẶC LiteLLM
- Nếu có cả hai, LiteLLM sẽ được ưu tiên (xem `config.py`)

#### 2.2. Thêm vào `.gitignore`

Đảm bảo file `.gitignore` có:

```gitignore
# Environment files
.env
.env.local
.env.local.user
.env.*.user
env/.env.local.user
env/.env.*.user
```

---

### **BƯỚC 3: Setup Azure Resources**

#### 3.1. Azure Bot Service Registration

1. Truy cập [Azure Portal](https://portal.azure.com/)
2. Tạo **Azure Bot** resource:
   - Name: `your-bot-name`
   - Subscription: chọn subscription của bạn
   - Resource Group: tạo mới hoặc chọn existing
   - Pricing tier: F0 (Free) hoặc S1 (Standard)

3. Sau khi tạo, lấy thông tin:
   - **Bot ID** (Application ID)
   - **Client Secret** (tạo mới trong "Configuration")
   - **Tenant ID**

#### 3.2. Azure AD App Registration (Cho SSO)

1. Truy cập [Azure Portal](https://portal.azure.com/) > **Azure Active Directory** > **App registrations**
2. Tìm app registration với **Application ID** = Bot ID ở trên
3. Cấu hình **API permissions**:
   - Click **Add a permission**
   - Chọn **Microsoft Graph** > **Delegated permissions**
   - Thêm: `User.Read`
   - Click **Grant admin consent** (QUAN TRỌNG!)

4. Cấu hình **Expose an API**:
   - Click **Expose an API**
   - Set **Application ID URI**: `api://<BOT_DOMAIN>/<BOT_ID>`
     - Ví dụ: `api://botframework.com/12345678-1234-1234-1234-123456789012`
   - Click **Add a scope** (nếu cần)

5. Cấu hình **Authentication**:
   - Click **Authentication**
   - Thêm **Redirect URI**:
     - Type: **Web**
     - URI: `https://token.botframework.com/.auth/web/redirect`
   - Enable:
     - ✅ **Access tokens**
     - ✅ **ID tokens**
   - Click **Save**

#### 3.3. Azure OpenAI (Nếu dùng Azure OpenAI)

1. Tạo **Azure OpenAI** resource trong Azure Portal
2. Deploy model (ví dụ: `gpt-4`, `gpt-35-turbo`)
3. Lấy thông tin:
   - **API Key** (trong "Keys and Endpoint")
   - **Endpoint** (ví dụ: `https://your-resource.openai.azure.com/`)
   - **Deployment Name** (tên model đã deploy)

---

### **BƯỚC 4: Provision Resources với Teams Toolkit**

#### 4.1. Sign in Microsoft 365

1. Mở VS Code
2. Click icon **Microsoft 365 Agents Toolkit** ở sidebar
3. Trong section **Account**, click **Sign in**
4. Đăng nhập với Microsoft 365 account

#### 4.2. Provision Azure Resources

1. Mở Command Palette (`Ctrl+Shift+P` hoặc `Cmd+Shift+P`)
2. Chọn: **Teams: Provision in the Cloud**
3. Chọn:
   - **Subscription**: Azure subscription của bạn
   - **Resource Group**: tạo mới hoặc chọn existing
   - **Region**: chọn region gần bạn
4. Đợi provisioning hoàn tất (5-10 phút)

**Kết quả**: Teams Toolkit sẽ tự động:
- ✅ Tạo Azure Bot Service
- ✅ Tạo Azure App Service (để host bot)
- ✅ Tạo App Registration trong Azure AD
- ✅ Tạo Teams App
- ✅ Ghi các thông tin vào `env/.env.local`

#### 4.3. Verify Environment Files

Sau khi provision, kiểm tra `env/.env.local` có các biến:
- `TEAMS_APP_ID`
- `BOT_ID`
- `SECRET_BOT_PASSWORD`
- `TENANT_ID`
- `BOT_ENDPOINT`

---

### **BƯỚC 5: Chạy Bot Local (Development)**

#### 5.1. Chạy Bot

**Option A: Sử dụng VS Code (Khuyến nghị)**

1. Mở file `src/app.py`
2. Nhấn `F5` hoặc click **Run and Debug**
3. Chọn: **Debug in Teams (Edge)** hoặc **Debug in Teams (Chrome)**
4. Teams sẽ mở trong browser
5. Click **Add** để install app vào Teams

**Option B: Sử dụng Script**

```bash
cd bot_team
python start_bot.py
```

Sau đó sử dụng ngrok hoặc Teams Toolkit để expose bot:
```bash
# Sử dụng Teams Toolkit CLI
teamsfx preview --local
```

#### 5.2. Test Bot

1. Trong Teams, gửi message cho bot
2. Bot sẽ trả lời dựa trên `instructions.txt`
3. Test SSO: gõ `auth` hoặc `đăng nhập`
4. Kiểm tra logs trong console

---

### **BƯỚC 6: Setup Backend Endpoint (Nếu cần)**

Nếu bạn muốn bot gửi Teams token xuống backend:

#### 6.1. Implement Backend Endpoint

Backend cần có endpoint để nhận token:

**Request:**
```http
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

**Response (Success):**
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

**Response (Error):**
```json
{
  "error": "Invalid token",
  "message": "Token validation failed"
}
```

#### 6.2. Ví dụ Backend (FastAPI)

Xem chi tiết trong `SETUP_TEAMS_TOKEN.md`

---

### **BƯỚC 7: Deploy lên Azure (Production)**

#### 7.1. Deploy Bot

1. Mở Command Palette (`Ctrl+Shift+P`)
2. Chọn: **Teams: Deploy to the Cloud**
3. Đợi deployment hoàn tất (5-10 phút)

#### 7.2. Cấu hình Environment Variables trong Azure

1. Truy cập Azure Portal > **App Service** (đã tạo ở Bước 4)
2. Vào **Configuration** > **Application settings**
3. Thêm các biến:
   - `AZURE_OPENAI_API_KEY` (hoặc `LITELLM_API_KEY`)
   - `AZURE_OPENAI_ENDPOINT` (hoặc `LITELLM_BASE_URL`)
   - `AZURE_OPENAI_MODEL_DEPLOYMENT_NAME` (hoặc `LITELLM_DEFAULT_CHAT_MODEL`)
   - `BACKEND_URL` (nếu có)
   - `BACKEND_AUTH_ENDPOINT` (nếu có)

**Lưu ý**: Không set `CLIENT_ID`, `CLIENT_SECRET` trong App Service nếu dùng Managed Identity.

#### 7.3. Publish Teams App

1. Mở Command Palette
2. Chọn: **Teams: Publish to Teams**
3. Chọn environment (dev/staging/prod)
4. App sẽ được publish lên Teams Admin Center

---

## 🔍 Troubleshooting

### Lỗi: "Environment variable not found"

**Giải pháp:**
1. Kiểm tra file `env/.env.local.user` có tồn tại không
2. Kiểm tra tên biến có đúng không (case-sensitive)
3. Restart application sau khi thay đổi env file

### Lỗi: "Cannot connect to your app"

**Giải pháp:**
1. Đảm bảo bot đang chạy trên port 3978
2. Kiểm tra firewall không block port 3978
3. Sử dụng ngrok hoặc Teams Toolkit để expose bot

### Lỗi: "SSO authentication failed"

**Giải pháp:**
1. Kiểm tra Azure AD App Registration có đúng quyền không
2. Kiểm tra `webApplicationInfo` trong manifest.json
3. Kiểm tra redirect URI trong Azure AD
4. Đảm bảo đã **Grant admin consent** cho permissions

### Lỗi: "Backend URL not configured"

**Giải pháp:**
1. Thêm `BACKEND_URL` vào `env/.env.local.user`
2. Kiểm tra backend có đang chạy và accessible không
3. Kiểm tra CORS settings trong backend

---

## 📚 Tài liệu Tham khảo

- [Microsoft 365 Agents Toolkit Documentation](https://docs.microsoft.com/microsoftteams/platform/toolkit/teams-toolkit-fundamentals)
- [Microsoft Teams SDK Python](https://github.com/microsoft/teams-ai-python)
- [Microsoft Teams SSO Documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/bots/how-to/authentication/auth-aad-sso-bots)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/overview)

---

## ✅ Checklist Triển khai

### Prerequisites
- [ ] Python >= 3.12, < 3.14 đã cài đặt
- [ ] Microsoft 365 Agents Toolkit đã cài đặt
- [ ] Azure OpenAI account (hoặc LiteLLM proxy)
- [ ] Microsoft 365 account cho development
- [ ] Azure subscription

### Configuration
- [ ] Tạo file `env/.env.local.user`
- [ ] Thêm Azure OpenAI config (hoặc LiteLLM)
- [ ] Thêm Backend URL (nếu cần)
- [ ] Thêm `env/.env.local.user` vào `.gitignore`

### Azure Setup
- [ ] Azure Bot Service đã tạo
- [ ] Azure AD App Registration đã cấu hình
- [ ] API permissions đã được grant admin consent
- [ ] Redirect URI đã được thêm
- [ ] Azure OpenAI resource đã tạo (nếu dùng)

### Development
- [ ] Dependencies đã cài đặt (`pip install -r src/requirements.txt`)
- [ ] Bot chạy được local
- [ ] Test bot trong Teams local
- [ ] Test SSO authentication
- [ ] Test integration với backend (nếu có)

### Production
- [ ] Deploy bot lên Azure App Service
- [ ] Cấu hình environment variables trong Azure
- [ ] Publish Teams app
- [ ] Test bot trong production Teams
- [ ] Monitor logs và errors

---

## 🎉 Kết luận

Codebase này **HOÀN TOÀN SẴN SÀNG** để triển khai! Chỉ cần:

1. ✅ Setup environment variables (15 phút)
2. ✅ Provision Azure resources với Teams Toolkit (10 phút)
3. ✅ Test local (5 phút)
4. ✅ Deploy production (10 phút)

**Tổng thời gian ước tính: 40-60 phút**

Chúc bạn triển khai thành công! 🚀

