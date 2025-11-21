import asyncio
import os
import logging

from azure.identity import ManagedIdentityCredential
from microsoft.teams.ai import ChatPrompt, ListMemory
from microsoft.teams.ai.ai_model import AIModel
from microsoft.teams.apps import App, ActivityContext
from microsoft.teams.openai import OpenAICompletionsAIModel
from microsoft.teams.api import MessageActivity, MessageActivityInput, MessageSubmitActionInvokeActivity, InvokeActivity

from config import Config
from token_service import send_token_to_backend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config()

# Load instructions from file
def load_instructions() -> str:
    """Load instructions from instructions.txt file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), "instructions.txt"), "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful assistant."

INSTRUCTIONS = load_instructions()

def create_token_factory():
    def get_token(scopes, tenant_id=None):
        credential = ManagedIdentityCredential(client_id=config.APP_ID)
        if isinstance(scopes, str):
            scopes_list = [scopes]
        else:
            scopes_list = scopes
        token = credential.get_token(*scopes_list)
        return token.token
    return get_token

app = App(
    token=create_token_factory() if config.APP_TYPE == "UserAssignedMsi" else None
)

# Khởi tạo model - ưu tiên LiteLLM nếu được cấu hình
if config.USE_LITELLM:
    # Sử dụng LiteLLM Proxy (OpenAI-compatible)
    # LiteLLM proxy hoạt động như OpenAI API, có thể sử dụng azure_endpoint với custom URL
    logger.info(f"Sử dụng LiteLLM Proxy: {config.LITELLM_BASE_URL}")
    model = OpenAICompletionsAIModel(
        key=config.LITELLM_API_KEY,
        model=config.LITELLM_DEFAULT_CHAT_MODEL,
        azure_endpoint=config.LITELLM_BASE_URL.rstrip('/'),  # LiteLLM base URL
        api_version="2024-10-21"  # LiteLLM thường hỗ trợ Azure API format
    )
else:
    # Fallback về Azure OpenAI trực tiếp
    if not config.AZURE_OPENAI_API_KEY or not config.AZURE_OPENAI_ENDPOINT:
        raise ValueError(
            "Cần cấu hình AZURE_OPENAI_API_KEY và AZURE_OPENAI_ENDPOINT "
            "hoặc LITELLM_API_KEY, LITELLM_BASE_URL, và LITELLM_DEFAULT_CHAT_MODEL"
        )
    logger.info(f"Sử dụng Azure OpenAI trực tiếp: {config.AZURE_OPENAI_ENDPOINT}")
    model = OpenAICompletionsAIModel(
        key=config.AZURE_OPENAI_API_KEY,
        model=config.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_version="2024-10-21"
    )
 

conversation_store: dict[str, ListMemory] = {}

def get_or_create_conversation_memory(conversation_id: str) -> ListMemory:
    """Get or create conversation memory for a specific conversation"""
    if conversation_id not in conversation_store:
        conversation_store[conversation_id] = ListMemory()
    return conversation_store[conversation_id]

async def handle_stateful_conversation(model: AIModel, ctx: ActivityContext[MessageActivity]) -> None:
    """Example of stateful conversation handler that maintains conversation history"""
    # Retrieve existing conversation memory or initialize new one
    memory = get_or_create_conversation_memory(ctx.activity.conversation.id)

    # Get existing messages for logging
    existing_messages = await memory.get_all()
    print(f"Existing messages before sending to prompt: {len(existing_messages)} messages")

    # Create ChatPrompt with conversation-specific memory
    chat_prompt = ChatPrompt(model)

    chat_result = await chat_prompt.send(
        input=ctx.activity.text, 
        memory=memory,
        instructions=INSTRUCTIONS,
        on_chunk=lambda chunk: ctx.stream.emit(chunk)
    )

    if ctx.activity.conversation.is_group:
        # If the conversation is a group chat, we need to send the final response
        # back to the group chat
        await ctx.send(MessageActivityInput(text=chat_result.response.content).add_ai_generated().add_feedback())
    else:
        ctx.stream.emit(MessageActivityInput().add_ai_generated().add_feedback())

@app.on_message_submit_feedback
async def handle_message_feedback(ctx: ActivityContext[MessageSubmitActionInvokeActivity]):
    """Handle feedback submission events"""
    activity = ctx.activity

    print(f"your feedback is {activity.value.action_value}")

# TODO: Sửa cách đăng ký SSO handlers - tạm thời comment để test
# @app.on_invoke("signin/verifyState")
async def handle_sso_verify_state(ctx: ActivityContext[InvokeActivity]):
    """
    Handler cho SSO signin verify state
    Lấy token từ Teams và gửi xuống backend
    """
    try:
        # Lấy user ID từ activity
        user_id = ctx.activity.from_property.id if ctx.activity.from_property else None
        
        if not user_id:
            logger.error("Không thể lấy user ID từ activity")
            return {"type": "message", "text": "Lỗi: Không thể xác định user"}
        
        # Lấy token từ Teams SSO
        # Microsoft Teams SDK sẽ tự động xử lý SSO flow
        # Token sẽ được lấy thông qua OAuth flow
        token_result = await app.get_user_token(
            ctx,
            config.APP_ID,
            "User.Read"  # Scope cần thiết cho Graph API
        )
        
        if token_result and token_result.token:
            logger.info(f"Đã lấy token thành công cho user: {user_id}")
            
            # Gửi token xuống backend
            backend_response = await send_token_to_backend(
                user_id=user_id,
                token=token_result.token,
                tenant_id=config.APP_TENANTID,
                additional_data={
                    "conversation_id": ctx.activity.conversation.id if ctx.activity.conversation else None,
                    "channel_id": ctx.activity.channel_id if hasattr(ctx.activity, 'channel_id') else None
                }
            )
            
            if "error" not in backend_response:
                logger.info(f"Đã gửi token xuống backend thành công: {backend_response}")
                return {
                    "type": "message",
                    "text": "✅ Đã xác thực thành công và gửi token xuống backend!"
                }
            else:
                logger.error(f"Lỗi từ backend: {backend_response.get('error')}")
                return {
                    "type": "message",
                    "text": f"⚠️ Đã lấy token nhưng có lỗi khi gửi xuống backend: {backend_response.get('error')}"
                }
        else:
            # Nếu chưa có token, cần initiate SSO flow
            logger.info("Chưa có token, cần initiate SSO flow")
            # Teams SDK sẽ tự động xử lý SSO flow
            return {
                "type": "message",
                "text": "Đang xử lý xác thực..."
            }
            
    except Exception as e:
        logger.error(f"Lỗi khi xử lý SSO: {e}", exc_info=True)
        return {
            "type": "message",
            "text": f"❌ Lỗi khi xử lý xác thực: {str(e)}"
        }

# TODO: Sửa cách đăng ký SSO handlers - tạm thời comment để test
# @app.on_invoke("signin/tokenExchange")
async def handle_sso_token_exchange(ctx: ActivityContext[InvokeActivity]):
    """
    Handler cho SSO token exchange
    Được gọi khi Teams trả về token sau khi user đồng ý
    """
    try:
        user_id = ctx.activity.from_property.id if ctx.activity.from_property else None
        
        if not user_id:
            logger.error("Không thể lấy user ID từ activity")
            return {"type": "message", "text": "Lỗi: Không thể xác định user"}
        
        # Lấy token từ token exchange response
        # Token sẽ có trong ctx.activity.value hoặc có thể lấy lại
        token_result = await app.get_user_token(
            ctx,
            config.APP_ID,
            "User.Read"
        )
        
        if token_result and token_result.token:
            logger.info(f"Token exchange thành công cho user: {user_id}")
            
            # Gửi token xuống backend
            backend_response = await send_token_to_backend(
                user_id=user_id,
                token=token_result.token,
                tenant_id=config.APP_TENANTID,
                additional_data={
                    "conversation_id": ctx.activity.conversation.id if ctx.activity.conversation else None,
                    "channel_id": ctx.activity.channel_id if hasattr(ctx.activity, 'channel_id') else None
                }
            )
            
            if "error" not in backend_response:
                logger.info(f"Đã gửi token xuống backend thành công: {backend_response}")
                return {
                    "type": "message",
                    "text": "✅ Đã xác thực thành công và gửi token xuống backend!"
                }
            else:
                logger.error(f"Lỗi từ backend: {backend_response.get('error')}")
                return {
                    "type": "message",
                    "text": f"⚠️ Đã lấy token nhưng có lỗi khi gửi xuống backend: {backend_response.get('error')}"
                }
        else:
            logger.error("Không thể lấy token từ token exchange")
            return {
                "type": "message",
                "text": "❌ Không thể lấy token từ xác thực"
            }
            
    except Exception as e:
        logger.error(f"Lỗi khi xử lý token exchange: {e}", exc_info=True)
        return {
            "type": "message",
            "text": f"❌ Lỗi khi xử lý token exchange: {str(e)}"
        }

# Thêm command để user có thể trigger SSO manually
@app.on_message
async def handle_message(ctx: ActivityContext[MessageActivity]):
    """Handle messages using stateful conversation"""
    # Kiểm tra nếu user muốn authenticate
    if ctx.activity.text and ctx.activity.text.lower().strip() in ["auth", "authenticate", "login", "đăng nhập", "xác thực"]:
        try:
            user_id = ctx.activity.from_property.id if ctx.activity.from_property else None
            if user_id:
                # Thử lấy token
                token_result = await app.get_user_token(
                    ctx,
                    config.APP_ID,
                    "User.Read"
                )
                
                if token_result and token_result.token:
                    # Gửi token xuống backend
                    backend_response = await send_token_to_backend(
                        user_id=user_id,
                        token=token_result.token,
                        tenant_id=config.APP_TENANTID,
                        additional_data={
                            "conversation_id": ctx.activity.conversation.id if ctx.activity.conversation else None,
                        }
                    )
                    
                    if "error" not in backend_response:
                        await ctx.send(MessageActivityInput(
                            text="✅ Đã xác thực thành công và gửi token xuống backend!"
                        ))
                    else:
                        await ctx.send(MessageActivityInput(
                            text=f"⚠️ Đã lấy token nhưng có lỗi khi gửi xuống backend: {backend_response.get('error')}"
                        ))
                else:
                    # Initiate SSO flow
                    await ctx.send(MessageActivityInput(
                        text="Đang khởi tạo quá trình xác thực..."
                    ))
            else:
                await ctx.send(MessageActivityInput(
                    text="❌ Không thể xác định user"
                ))
        except Exception as e:
            logger.error(f"Lỗi khi xử lý authentication command: {e}", exc_info=True)
            await ctx.send(MessageActivityInput(
                text=f"❌ Lỗi: {str(e)}"
            ))
    else:
        # Xử lý message bình thường
        await handle_stateful_conversation(model, ctx)

if __name__ == "__main__":
    asyncio.run(app.start())
