"""
Service để xử lý Teams token và gửi xuống backend
"""
import httpx
import logging
from typing import Optional, Dict, Any
from config import Config

config = Config()
logger = logging.getLogger(__name__)

async def send_token_to_backend(
    user_id: str,
    token: str,
    tenant_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Gửi Teams token xuống backend để xử lý authentication và tích hợp Graph API
    
    Args:
        user_id: ID của user trong Teams
        token: Access token từ Teams SSO
        tenant_id: Tenant ID (optional)
        additional_data: Dữ liệu bổ sung (optional)
    
    Returns:
        Response từ backend
    """
    if not config.BACKEND_URL:
        logger.warning("BACKEND_URL chưa được cấu hình, không thể gửi token xuống backend")
        return {"error": "Backend URL not configured"}
    
    endpoint = f"{config.BACKEND_URL.rstrip('/')}{config.BACKEND_AUTH_ENDPOINT}"
    
    payload = {
        "teams_token": token,
        "user_id": user_id,
        "tenant_id": tenant_id or config.APP_TENANTID,
    }
    
    if additional_data:
        payload.update(additional_data)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Lỗi khi gửi token xuống backend: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Lỗi không mong đợi: {e}")
        return {"error": str(e)}

