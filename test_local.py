"""
Script để test bot Teams local
Chạy script này để kiểm tra cấu hình và kết nối
"""
import asyncio
import sys
import os
from pathlib import Path

# Thêm src vào path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import config trước
from config import Config

# Import app sau khi config đã load
import app as app_module

def test_config():
    """Test cấu hình"""
    print("=" * 50)
    print("KIỂM TRA CẤU HÌNH")
    print("=" * 50)
    
    config = Config()
    
    # Kiểm tra bot config
    print("\n📋 Bot Configuration:")
    print(f"  APP_ID: {config.APP_ID[:20]}..." if config.APP_ID else "  APP_ID: ❌ CHƯA CẤU HÌNH")
    print(f"  APP_PASSWORD: {'✅ Đã cấu hình' if config.APP_PASSWORD else '❌ CHƯA CẤU HÌNH'}")
    print(f"  TENANT_ID: {config.APP_TENANTID[:20]}..." if config.APP_TENANTID else "  TENANT_ID: ❌ CHƯA CẤU HÌNH")
    print(f"  PORT: {config.PORT}")
    
    # Kiểm tra AI model config
    print("\n🤖 AI Model Configuration:")
    if config.USE_LITELLM:
        print("  ✅ Sử dụng LiteLLM Proxy")
        print(f"  LITELLM_BASE_URL: {config.LITELLM_BASE_URL}")
        print(f"  LITELLM_DEFAULT_CHAT_MODEL: {config.LITELLM_DEFAULT_CHAT_MODEL}")
        print(f"  LITELLM_API_KEY: {config.LITELLM_API_KEY[:10]}..." if config.LITELLM_API_KEY else "  LITELLM_API_KEY: ❌")
    else:
        print("  ✅ Sử dụng Azure OpenAI trực tiếp")
        print(f"  AZURE_OPENAI_ENDPOINT: {config.AZURE_OPENAI_ENDPOINT}")
        print(f"  AZURE_OPENAI_MODEL: {config.AZURE_OPENAI_MODEL_DEPLOYMENT_NAME}")
        print(f"  AZURE_OPENAI_API_KEY: {'✅ Đã cấu hình' if config.AZURE_OPENAI_API_KEY else '❌ CHƯA CẤU HÌNH'}")
    
    # Kiểm tra backend config
    print("\n🔗 Backend Configuration:")
    if config.BACKEND_URL:
        print(f"  ✅ BACKEND_URL: {config.BACKEND_URL}")
        print(f"  ✅ BACKEND_AUTH_ENDPOINT: {config.BACKEND_AUTH_ENDPOINT}")
    else:
        print("  ⚠️  BACKEND_URL: Chưa cấu hình (không bắt buộc)")
    
    # Tổng kết
    print("\n" + "=" * 50)
    errors = []
    if not config.APP_ID:
        errors.append("❌ APP_ID chưa được cấu hình")
    if not config.APP_PASSWORD:
        errors.append("❌ APP_PASSWORD chưa được cấu hình")
    if config.USE_LITELLM:
        if not config.LITELLM_API_KEY or not config.LITELLM_BASE_URL:
            errors.append("❌ LiteLLM chưa được cấu hình đầy đủ")
    else:
        if not config.AZURE_OPENAI_API_KEY or not config.AZURE_OPENAI_ENDPOINT:
            errors.append("❌ Azure OpenAI chưa được cấu hình đầy đủ")
    
    if errors:
        print("⚠️  CẢNH BÁO:")
        for error in errors:
            print(f"  {error}")
        print("\n💡 Hướng dẫn:")
        print("  1. Tạo file env/.env.local.user")
        print("  2. Copy từ env/env.local.user.template")
        print("  3. Điền các giá trị cần thiết")
    else:
        print("✅ TẤT CẢ CẤU HÌNH ĐÃ ĐẦY ĐỦ!")
    
    print("=" * 50)
    return len(errors) == 0

async def test_model():
    """Test kết nối với AI model"""
    print("\n" + "=" * 50)
    print("KIỂM TRA KẾT NỐI AI MODEL")
    print("=" * 50)
    
    try:
        config = Config()
        
        if config.USE_LITELLM:
            print(f"\n🔄 Đang test kết nối với LiteLLM: {config.LITELLM_BASE_URL}")
        else:
            print(f"\n🔄 Đang test kết nối với Azure OpenAI: {config.AZURE_OPENAI_ENDPOINT}")
        
        # Test với một prompt đơn giản
        from microsoft.teams.ai import ChatPrompt
        
        # Sử dụng model từ app_module
        chat_prompt = ChatPrompt(app_module.model)
        test_input = "Xin chào, bạn có thể trả lời 'OK' không?"
        
        print(f"📤 Gửi test message: '{test_input}'")
        print("⏳ Đang chờ phản hồi...")
        
        result = await chat_prompt.send(
            input=test_input,
            instructions="Bạn là một trợ lý hữu ích. Hãy trả lời ngắn gọn."
        )
        
        print(f"✅ Kết nối thành công!")
        print(f"📥 Phản hồi: {result.response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ LỖI khi test model: {str(e)}")
        print(f"   Chi tiết: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def test_app_start():
    """Test khởi động app"""
    print("\n" + "=" * 50)
    print("KIỂM TRA KHỞI ĐỘNG APP")
    print("=" * 50)
    
    try:
        print("\n🔄 Đang kiểm tra app configuration...")
        print(f"  ✅ App đã được khởi tạo: {app_module.app is not None}")
        print(f"  ✅ Model đã được khởi tạo: {app_module.model is not None}")
        print(f"  ✅ Port: {Config().PORT}")
        
        print("\n💡 Để chạy bot:")
        print("  1. Chạy: python src/app.py")
        print("  2. Hoặc dùng Teams Toolkit: F5 trong VS Code")
        print("  3. Bot sẽ chạy trên: http://localhost:3978")
        
        return True
    except Exception as e:
        print(f"❌ LỖI: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("\n" + "🚀" * 25)
    print("  TEAMS BOT - LOCAL TEST SCRIPT")
    print("🚀" * 25)
    
    # Test 1: Config
    config_ok = test_config()
    
    if not config_ok:
        print("\n⚠️  Vui lòng cấu hình đầy đủ trước khi tiếp tục!")
        return
    
    # Test 2: Model connection
    model_ok = await test_model()
    
    # Test 3: App start
    app_ok = await test_app_start()
    
    # Tổng kết
    print("\n" + "=" * 50)
    print("KẾT QUẢ TEST")
    print("=" * 50)
    print(f"  Config: {'✅' if config_ok else '❌'}")
    print(f"  Model: {'✅' if model_ok else '❌'}")
    print(f"  App: {'✅' if app_ok else '❌'}")
    
    if config_ok and model_ok and app_ok:
        print("\n🎉 TẤT CẢ TEST ĐỀU THÀNH CÔNG!")
        print("\n📝 Bước tiếp theo:")
        print("  1. Chạy bot: cd src && python app.py")
        print("  2. Hoặc dùng Teams Toolkit để debug")
        print("  3. Test trong Teams bằng cách gửi message")
    else:
        print("\n⚠️  CÓ MỘT SỐ VẤN ĐỀ CẦN KHẮC PHỤC")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())

