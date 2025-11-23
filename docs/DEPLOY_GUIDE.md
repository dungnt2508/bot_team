# Hướng dẫn Deploy Bot Teams lên Azure

## Tổng quan
- Bot Teams được deploy lên Azure App Service thông qua Microsoft 365 Agents Toolkit. Quy trình gồm 3 bước:
1. Provision Azure resources (lần đầu)
2. Deploy code lên Azure App Service
3. Publish Teams app


## Prerequisites
- Trước khi deploy, cần:
```
Azure subscription
Microsoft 365 account (đã sign in trong Teams Toolkit)
Microsoft 365 Agents Toolkit đã cài đặt (VS Code Extension hoặc CLI)
Backend đã deploy và có URL (nếu tích hợp)
```

## Bước 1: Provision Azure Resources (Lần đầu)
- 1.1. Sign in Microsoft 365

    Mở VS Code
    Click icon Microsoft 365 Agents Toolkit ở sidebar
    Trong section Account, click Sign in
    Đăng nhập với Microsoft 365 account - done
- 1.2. Provision Resources
    Mở Command Palette (Ctrl+Shift+P hoặc Cmd+Shift+P)
    Chọn: Microsoft 365 Agents: Provision
    Chọn:
    Subscription: Azure subscription của bạn
    Resource Group: tạo mới hoặc chọn existing
    Region: chọn region gần bạn (ví dụ: Southeast Asia)
    Đợi provisioning hoàn tất (5-10 phút)
    Kết quả: Teams Toolkit sẽ tự động:
    Tạo Azure Bot Service
    Tạo Azure App Service (Linux, Python 3.12)
    Tạo User Assigned Managed Identity
    Tạo App Registration trong Azure AD
    Tạo Teams App
    Ghi các thông tin vào env/.env.local
- 1.3. Verify Environment Files
    Sau khi provision, kiểm tra env/.env.local có các biến:
    TEAMS_APP_ID
    BOT_ID (Client ID)
    SECRET_BOT_PASSWORD
    TENANT_ID
    BOT_ENDPOINT
    BOT_AZURE_APP_SERVICE_RESOURCE_ID


## Bước 2: Cấu hình Environment Variables
- 2.1. Cấu hình trong Azure Portal
    Truy cập Azure Portal: https://portal.azure.com
    Tìm App Service đã tạo (tên: bot-xxx hoặc tên bạn đã set)
    Vào Configuration > Application settings
    Thêm các biến sau:
    Azure OpenAI (nếu dùng Azure OpenAI)
    AZURE_OPENAI_API_KEY = <your-azure-openai-key>AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = <your-model-name>AZURE_OPENAI_ENDPOINT = https://<your-resource>.openai.azure.com/
    LiteLLM (nếu dùng LiteLLM Proxy)
    LITELLM_API_KEY = <your-litellm-key>LITELLM_BASE_URL = https://<your-litellm-proxy>.comLITELLM_DEFAULT_CHAT_MODEL = gpt-4LITELLM_DEFAULT_EMBEDDING_MODEL = text-embedding-ada-002
    Backend Integration (QUAN TRỌNG - cho tích hợp với Backend)
    BACKEND_URL = https://your-backend-api.comBACKEND_AUTH_ENDPOINT = /api/auth/teams-token
    Lưu ý:
    Không set CLIENT_ID, CLIENT_SECRET trong App Service nếu dùng Managed Identity (đã được set tự động)
    BOT_TYPE đã được set tự động là UserAssignedMsi
    Click Save sau khi thêm các biến
- 2.2. Restart App Service
    Sau khi thêm environment variables:
    Vào Overview
    Click Restart
    Đợi restart hoàn tất (1-2 phút)    


## Bước 3: Deploy Code lên Azure    
- 3.1. Deploy bằng VS Code (Khuyến nghị)
    Mở Command Palette (Ctrl+Shift+P)
    Chọn: Teams: Deploy to the Cloud
    Chọn environment: dev, staging, hoặc prod
    Đợi deployment hoàn tất (5-10 phút)
    Quá trình deploy sẽ:
    Zip folder src/ (theo .webappignore)
    Deploy lên Azure App Service qua zip deploy
    Install dependencies từ requirements.txt
    Start bot với command: python app.py
- 3.2. Deploy bằng CLI
```
cd bot_team
teamsfx deploy --env dev
```

- 3.3. Verify Deployment
    Vào Azure Portal > App Service > Deployment Center
    Kiểm tra deployment status
    Vào Log stream để xem logs
    Kiểm tra có lỗi không


## Bước 4: Cấu hình Azure Bot Service
- 4.1. Verify Bot Registration
    Vào Azure Portal > Bot Services
    Tìm bot đã tạo
    Vào Configuration
    Verify:
    Messaging endpoint: https://<your-app-service>.azurewebsites.net/api/messages
    Microsoft App ID: đúng với BOT_ID trong env file
- 4.2. Cấu hình OAuth (cho SSO)
    Vào Azure Portal > Azure Active Directory > App registrations
    Tìm app với Application ID = BOT_ID
    Vào API permissions:
    Thêm: Microsoft Graph > Delegated > User.Read
    Grant admin consent
    Vào Authentication:
    Redirect URI: https://token.botframework.com/.auth/web/redirect
    Enable: Access tokens, ID tokens

## Bước 5: Publish Teams App
- 5.1. Publish lên Teams Admin Center
    Mở Command Palette (Ctrl+Shift+P)
    Chọn: Teams: Publish to Teams
    Chọn environment (dev/staging/prod)
    Đợi publish hoàn tất
    App sẽ được publish lên Teams Admin Center để review và approval.
- 5.2. Approve App trong Teams Admin Center
    Truy cập: https://admin.teams.microsoft.com/policies/manage-apps
    Tìm app của bạn
    Click Approve (nếu cần admin approval)
    App sẽ available trong Teams

## Bước 6: Test Deployment    
- 6.1. Test trong Teams
    Mở Microsoft Teams
    Vào Apps > Built for your org
    Tìm và install app của bạn
    Test:
    Gửi message cho bot
    Test authentication: gõ "auth"
    Test HR query: gõ câu hỏi HR
- 6.2. Monitor Logs
    Vào Azure Portal > App Service > Log stream
    Xem real-time logs
    Kiểm tra errors nếu có
- 6.3. Test Backend Integration
    Test authentication flow
    Test HR query flow
    Verify Backend nhận được requests


## Troubleshooting
- Lỗi: "Deployment failed"
`
    Giải pháp:
    Kiểm tra logs trong Azure Portal > App Service > Deployment Center
    Kiểm tra .webappignore có exclude đúng files không
    Kiểm tra requirements.txt có đúng dependencies không
    Thử deploy lại    
`

- Lỗi: "Bot không phản hồi"
`
    Giải pháp:
    Kiểm tra App Service đang running (Overview > Status)
    Kiểm tra Log stream có errors không
    Kiểm tra Messaging endpoint trong Bot Service có đúng không
    Restart App Service
`

- Lỗi: "Environment variable not found"
`
    Giải pháp:
    Kiểm tra Application settings trong Azure Portal
    Verify tên biến có đúng không (case-sensitive)
    Restart App Service sau khi thêm biến
`
- Lỗi: "Cannot connect to Backend"
`
    Giải pháp:
    Kiểm tra BACKEND_URL có đúng không
    Kiểm tra Backend có đang chạy không
    Kiểm tra CORS settings trong Backend
    Kiểm tra firewall/network rules
`
- Lỗi: "SSO authentication failed"
`
    Giải pháp:
    Kiểm tra Azure AD App Registration có đúng permissions không
    Kiểm tra redirect URI có đúng không
    Kiểm tra webApplicationInfo trong manifest.json
    Grant admin consent cho permissions
`

## Checklist Deployment
- Trước khi Deploy
`
    [ ] Azure subscription đã có
    [ ] Microsoft 365 account đã sign in
    [ ] Backend đã deploy và có URL
    [ ] Environment variables đã chuẩn bị
`
- Provision
`
    [ ] Provision Azure resources thành công
    [ ] Verify env/.env.local có đầy đủ biến
    [ ] Verify Azure resources đã tạo (App Service, Bot Service, etc.)
`
- Configuration
`
    [ ] Set environment variables trong Azure Portal
    [ ] Set BACKEND_URL và BACKEND_AUTH_ENDPOINT
    [ ] Set Azure OpenAI hoặc LiteLLM config
    [ ] Restart App Service
`
- Deploy
`
    [ ] Deploy code thành công
    [ ] Verify deployment trong Deployment Center
    [ ] Check logs không có errors
`
- Publish
`
    [ ] Publish Teams app thành công
    [ ] Approve app trong Teams Admin Center (nếu cần)
    [ ] Install app trong Teams
`
- Testing
`
    [ ] Test bot phản hồi messages
    [ ] Test authentication flow
    [ ] Test HR query flow
    [ ] Test Backend integration
`