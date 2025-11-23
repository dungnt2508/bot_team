"""
Backend Service
Service để gọi Backend API từ Bot Teams
"""
import httpx
import logging
from typing import Optional, Dict, Any
from config import Config

config = Config()
logger = logging.getLogger(__name__)


class BackendServiceError(Exception):
    """Exception cho Backend Service errors"""
    pass


class AuthenticationError(BackendServiceError):
    """Exception khi authentication fails"""
    pass


async def call_backend_hr_api(
    query: str,
    teams_token: str,
    user_id: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gọi Backend HR API để xử lý query
    
    Args:
        query: Câu hỏi của user
        teams_token: Teams token để authenticate
        user_id: User ID
        conversation_id: Conversation ID (optional)
    
    Returns:
        Response từ Backend với format:
        {
            "answer": "...",
            "conversation_id": "...",
            "sources": [...],
            "metadata": {...}
        }
    
    Raises:
        AuthenticationError: Nếu token invalid (401)
        BackendServiceError: Nếu có lỗi khác
    """
    if not config.BACKEND_URL:
        raise BackendServiceError("BACKEND_URL chưa được cấu hình")
    
    endpoint = f"{config.BACKEND_URL.rstrip('/')}/api/v1/hr/query"
    
    payload = {
        "query": query,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "include_sources": True,
        "include_metadata": True
    }
    
    headers = {
        "X-Teams-Token": teams_token,  # ✅ Gửi Teams token trong header riêng
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:  # 60s timeout cho HR query
            response = await client.post(
                endpoint,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 401:
                # Token invalid → cần re-authenticate
                logger.warning("Backend trả về 401 - Token không hợp lệ")
                raise AuthenticationError("Token không hợp lệ, vui lòng authenticate lại bằng cách gõ 'auth'")
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Backend API error: {e.response.status_code}",
            status_code=e.response.status_code,
            response_text=e.response.text[:200]
        )
        if e.response.status_code == 401:
            raise AuthenticationError("Token không hợp lệ, vui lòng authenticate lại")
        raise BackendServiceError(f"Backend API error: {e.response.status_code}")
    except httpx.TimeoutException:
        logger.error("Backend API timeout")
        raise BackendServiceError("Backend không phản hồi, vui lòng thử lại sau")
    except httpx.RequestError as e:
        logger.error(f"Backend API request error: {e}")
        raise BackendServiceError(f"Không thể kết nối đến Backend: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error khi gọi Backend: {e}", exc_info=True)
        raise BackendServiceError(f"Lỗi không mong đợi: {str(e)}")


async def send_teams_token_to_backend(
    user_id: str,
    token: str,
    tenant_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Gửi Teams token xuống Backend để authenticate
    
    Args:
        user_id: ID của user trong Teams
        token: Access token từ Teams SSO
        tenant_id: Tenant ID (optional)
        additional_data: Dữ liệu bổ sung (optional)
    
    Returns:
        Response từ Backend với format:
        {
            "success": True,
            "message": "...",
            "user": {...}
        }
    
    Raises:
        BackendServiceError: Nếu có lỗi
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
            
            if response.status_code == 401:
                logger.warning("Backend trả về 401 khi gửi Teams token")
                return {"error": "Token không hợp lệ"}
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Lỗi khi gửi token xuống backend: {e.response.status_code}",
            status_code=e.response.status_code,
            response_text=e.response.text[:200]
        )
        return {"error": f"Backend error: {e.response.status_code}"}
    except httpx.TimeoutException:
        logger.error("Backend timeout khi gửi token")
        return {"error": "Backend không phản hồi"}
    except httpx.RequestError as e:
        logger.error(f"Lỗi khi kết nối đến backend: {e}")
        return {"error": f"Không thể kết nối đến Backend: {str(e)}"}
    except Exception as e:
        logger.error(f"Lỗi không mong đợi: {e}", exc_info=True)
        return {"error": str(e)}

