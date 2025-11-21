"""
Script test nhanh - chỉ kiểm tra config và model connection
Chạy: python quick_test.py
"""
import asyncio
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config import Config

async def quick_test():
    """Test nhanh config và model"""
    print("🔍 QUICK TEST\n")
    
    config = Config()
    
    # Test config
    print("📋 Config:")
    if config.USE_LITELLM:
        print(f"  ✅ LiteLLM: {config.LITELLM_BASE_URL}")
        print(f"  Model: {config.LITELLM_DEFAULT_CHAT_MODEL}")
    else:
        print(f"  ✅ Azure OpenAI: {config.AZURE_OPENAI_ENDPOINT}")
        print(f"  Model: {config.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME}")
    
    print(f"  Bot ID: {config.APP_ID[:20]}..." if config.APP_ID else "  Bot ID: ❌")
    print(f"  Backend: {config.BACKEND_URL or 'Chưa cấu hình'}")
    
    # Test model connection (không import app để tránh lỗi SSO handlers)
    print("\n🤖 Test Model Connection:")
    try:
        from microsoft.teams.openai import OpenAICompletionsAIModel
        from microsoft.teams.ai import ChatPrompt
        
        # Tạo model trực tiếp để test
        if config.USE_LITELLM:
            test_model = OpenAICompletionsAIModel(
                key=config.LITELLM_API_KEY,
                model=config.LITELLM_DEFAULT_CHAT_MODEL,
                azure_endpoint=config.LITELLM_BASE_URL.rstrip('/'),
                api_version="2024-10-21"
            )
        else:
            test_model = OpenAICompletionsAIModel(
                key=config.AZURE_OPENAI_API_KEY,
                model=config.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME,
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                api_version="2024-10-21"
            )
        
        chat_prompt = ChatPrompt(test_model)
        result = await chat_prompt.send(
            input="Test",
            instructions="Trả lời ngắn: OK"
        )
        print(f"  ✅ Kết nối thành công!")
        print(f"  Response: {result.response.content[:50]}")
    except Exception as e:
        print(f"  ❌ Lỗi: {str(e)[:100]}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test hoàn tất!")

if __name__ == "__main__":
    asyncio.run(quick_test())

