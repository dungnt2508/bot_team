import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env files theo thứ tự ưu tiên
# 1. Load .env ở root (nếu có)
load_dotenv()

# 2. Load env/.env.local (tự động tạo bởi Teams Toolkit)
env_folder = Path(__file__).parent.parent / "env"
if env_folder.exists():
    load_dotenv(env_folder / ".env.local", override=False)
    # 3. Load env/.env.local.user (user settings - ưu tiên cao nhất)
    load_dotenv(env_folder / ".env.local.user", override=True)

class Config:
    """Bot Configuration"""

    # Port cho bot Teams (mặc định 3978)
    # Lưu ý: Port 8386 là port của backend API, không phải port của bot
    _port_env = os.environ.get("PORT", "3978")
    PORT = int(_port_env)
    
    # Cảnh báo nếu port được set là 8386 (port của backend)
    if PORT == 8386:
        import warnings
        warnings.warn(
            "⚠️ PORT=8386 là port của backend API, không phải port của bot Teams! "
            "Bot Teams nên chạy trên port 3978. "
            "Nếu bạn muốn thay đổi port của bot, hãy set PORT environment variable sang port khác (ví dụ: 3978)."
        )
        # Tự động sửa về 3978 nếu phát hiện port 8386
        PORT = 3978
    APP_ID = os.environ.get("CLIENT_ID", "")
    APP_PASSWORD = os.environ.get("CLIENT_SECRET", "")
    APP_TYPE = os.environ.get("BOT_TYPE", "")
    APP_TENANTID = os.environ.get("TENANT_ID", "")
    
    # Azure OpenAI Configuration (Fallback)
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "") # Azure OpenAI API key
    AZURE_OPENAI_MODEL_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_MODEL_DEPLOYMENT_NAME", "") # Azure OpenAI model deployment name
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "") # Azure OpenAI endpoint
    
    # LiteLLM Proxy Configuration (Primary - nếu có)
    LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY", "")
    LITELLM_BASE_URL = os.environ.get("LITELLM_BASE_URL", "")
    LITELLM_DEFAULT_CHAT_MODEL = os.environ.get("LITELLM_DEFAULT_CHAT_MODEL", "")
    LITELLM_DEFAULT_EMBEDDING_MODEL = os.environ.get("LITELLM_DEFAULT_EMBEDDING_MODEL", "")
    
    # Xác định sử dụng LiteLLM hay Azure OpenAI
    USE_LITELLM = bool(LITELLM_API_KEY and LITELLM_BASE_URL and LITELLM_DEFAULT_CHAT_MODEL)
    
    # Backend configuration for token forwarding
    BACKEND_URL = os.environ.get("BACKEND_URL", "") # Backend API URL để gửi token
    BACKEND_AUTH_ENDPOINT = os.environ.get("BACKEND_AUTH_ENDPOINT", "/api/auth/teams-token") # Endpoint để gửi token
