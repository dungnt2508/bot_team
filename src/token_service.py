"""
Service để xử lý Teams token và gửi xuống backend
DEPRECATED: Sử dụng backend_service.send_teams_token_to_backend() thay thế
Giữ lại để backward compatibility
"""
import logging
from typing import Optional, Dict, Any
from backend_service import send_teams_token_to_backend

logger = logging.getLogger(__name__)

async def send_token_to_backend(
    user_id: str,
    token: str,
    tenant_id: Optional[str] = None,
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Gửi Teams token xuống backend để xử lý authentication và tích hợp Graph API
    
    DEPRECATED: Sử dụng backend_service.send_teams_token_to_backend() thay thế
    
    Args:
        user_id: ID của user trong Teams
        token: Access token từ Teams SSO
        tenant_id: Tenant ID (optional)
        additional_data: Dữ liệu bổ sung (optional)
    
    Returns:
        Response từ backend
    """
    logger.warning("send_token_to_backend() is deprecated, use backend_service.send_teams_token_to_backend() instead")
    return await send_teams_token_to_backend(
        user_id=user_id,
        token=token,
        tenant_id=tenant_id,
        additional_data=additional_data
    )

