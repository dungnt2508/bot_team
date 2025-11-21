# Hướng dẫn Quản lý Environment Files

## 📁 Cấu trúc Environment Files trong Teams Toolkit

Microsoft Teams Toolkit sử dụng cấu trúc env files như sau:

```
Operation/
├── env/                          # Thư mục chứa các file env (theo m365agents.yml)
│   ├── .env.local                # Local development (tự động tạo)
│   ├── .env.local.user           # Local user settings (BẠN TẠO FILE NÀY)
│   ├── .env.dev                  # Development environment
│   ├── .env.dev.user             # Dev user overrides
│   ├── .env.staging              # Staging environment
│   └── .env.prod                 # Production environment
└── .env                          # File env ở root (tự động tạo khi deploy local)
```

## 🎯 Nơi lưu Settings

### **Cho Local Development (Khuyến nghị)**

**File: `env/.env.local.user`** ✅

Đây là file **QUAN TRỌNG NHẤT** cho local development. File này:
- ✅ Không bị ghi đè bởi Teams Toolkit
- ✅ Không commit lên Git (nên thêm vào .gitignore)
- ✅ Chứa các secrets và settings cá nhân của bạn

**Tạo file này:**
```bash
# Tạo file env/.env.local.user
cd Operation/env
# Tạo file .env.local.user với nội dung:
```

```env
# Azure OpenAI Settings
SECRET_AZURE_OPENAI_API_KEY=your-openai-key-here
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=your-model-name
AZURE_OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/

# Backend Integration (NEW - cho Teams Token)
BACKEND_URL=https://your-backend-api.com
BACKEND_AUTH_ENDPOINT=/api/auth/teams-token
```

### **Cho các môi trường khác**

| Môi trường | File | Mục đích |
|-----------|------|----------|
| **Local** | `env/.env.local.user` | ⭐ **Dùng file này cho local dev** |
| Development | `env/.env.dev` | Dev environment (tự động tạo bởi Teams Toolkit) |
| Staging | `env/.env.staging` | Staging environment |
| Production | `env/.env.prod` | Production (thường dùng Azure App Service Config) |

## 📝 Các biến môi trường cần thiết

### **Biến có sẵn (tự động tạo bởi Teams Toolkit)**

Các biến này được Teams Toolkit tự động tạo khi bạn chạy `teamsfx provision`:

```env
# Tự động tạo trong env/.env.{envName}
TEAMS_APP_ID=...
BOT_ID=...
SECRET_BOT_PASSWORD=...
TENANT_ID=...
BOT_ENDPOINT=...
```

### **Biến bạn cần thêm vào `env/.env.local.user`**

```env
# Azure OpenAI (BẮT BUỘC)
SECRET_AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=your-model-name
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

# Backend Integration (CHO TEAMS TOKEN)
BACKEND_URL=https://your-backend-api.com
BACKEND_AUTH_ENDPOINT=/api/auth/teams-token
```

## 🔧 Cách sử dụng

### **1. Local Development**

1. Tạo file `env/.env.local.user`:
```bash
cd Operation/env
touch .env.local.user
```

2. Thêm các biến môi trường vào file:
```env
SECRET_AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
BACKEND_URL=http://localhost:8000
BACKEND_AUTH_ENDPOINT=/api/auth/teams-token
```

3. Khi chạy local, Teams Toolkit sẽ tự động load:
   - `env/.env.local` (tự động tạo)
   - `env/.env.local.user` (file của bạn) - **Ưu tiên cao hơn**

### **2. Production/Deployment**

Khi deploy lên Azure App Service:
- **Không dùng file env** trong production
- Thay vào đó, set environment variables trong **Azure App Service Configuration**
- Hoặc dùng Azure Key Vault cho secrets

## ⚠️ Lưu ý quan trọng

### **1. File Priority (thứ tự ưu tiên)**

Khi chạy local, thứ tự load env files:
1. `env/.env.local.user` ⭐ **Ưu tiên cao nhất** (file của bạn)
2. `env/.env.local` (tự động tạo bởi Teams Toolkit)
3. `.env` ở root (nếu có)

### **2. Git Ignore**

**QUAN TRỌNG**: Thêm vào `.gitignore`:

```gitignore
# Environment files
.env
.env.local
.env.local.user
.env.*.user
env/.env.local.user
env/.env.*.user
```

### **3. File nào được commit?**

✅ **Commit được:**
- `env/.env.local` (không chứa secrets, chỉ có IDs)
- `env/.env.dev` (nếu không chứa secrets)

❌ **KHÔNG commit:**
- `env/.env.local.user` (chứa secrets)
- `env/.env.*.user` (tất cả file .user)
- `.env` ở root

## 🚀 Quick Start

### **Bước 1: Tạo file env cho local**

```bash
cd Operation/env
# Tạo file .env.local.user
```

### **Bước 2: Thêm settings**

Mở `env/.env.local.user` và thêm:

```env
# Azure OpenAI
SECRET_AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_MODEL_DEPLOYMENT_NAME=your-model
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/

# Backend (cho Teams Token)
BACKEND_URL=https://your-backend.com
BACKEND_AUTH_ENDPOINT=/api/auth/teams-token
```

### **Bước 3: Verify**

Code trong `src/config.py` sẽ tự động load từ:
- Environment variables (ưu tiên)
- `.env` file (nếu có)
- `env/.env.local.user` (khi chạy local)

## 📋 Checklist

- [ ] Tạo file `env/.env.local.user`
- [ ] Thêm `SECRET_AZURE_OPENAI_API_KEY`
- [ ] Thêm `AZURE_OPENAI_MODEL_DEPLOYMENT_NAME`
- [ ] Thêm `AZURE_OPENAI_ENDPOINT`
- [ ] Thêm `BACKEND_URL` (nếu dùng Teams Token)
- [ ] Thêm `BACKEND_AUTH_ENDPOINT` (nếu dùng Teams Token)
- [ ] Thêm `env/.env.local.user` vào `.gitignore`
- [ ] Test chạy local để verify

## 🔍 Troubleshooting

### **Lỗi: "Environment variable not found"**

1. Kiểm tra file `env/.env.local.user` có tồn tại không
2. Kiểm tra tên biến có đúng không (case-sensitive)
3. Kiểm tra file có được load không (thêm print trong config.py)

### **Lỗi: "File .env.local.user không được load"**

- Đảm bảo file nằm trong thư mục `env/`
- Đảm bảo tên file chính xác: `.env.local.user`
- Restart application sau khi thay đổi env file

## 📚 Tài liệu tham khảo

- [Teams Toolkit Environment Files](https://aka.ms/teamsfx-v5.0-guide)
- [Python dotenv Documentation](https://pypi.org/project/python-dotenv/)

