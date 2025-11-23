"""
Script helper để hiểu về JWT token cho Bot Teams
LƯU Ý: Bot Framework SDK yêu cầu JWT token thực từ Microsoft Teams service.
Token này KHÔNG THỂ được generate đơn giản vì cần được verify với Microsoft's OpenID metadata.
"""
import sys
from pathlib import Path

# Thêm src vào path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from config import Config

def explain_authentication():
    """
    Giải thích về authentication trong Bot Teams
    """
    config = Config()
    
    print("=" * 80)
    print("🔐 Microsoft Teams Bot Authentication")
    print("=" * 80)
    print()
    
    print("❓ Tại sao cần JWT token?")
    print("   Bot Teams sử dụng JWT token từ Microsoft Teams service để xác thực.")
    print("   Đây là cơ chế bảo mật bắt buộc của Bot Framework.")
    print()
    
    print("❓ JWT token đến từ đâu?")
    print("   JWT token được generate bởi Microsoft Teams service khi:")
    print("   - User gửi message trong Teams")
    print("   - Teams gửi request đến bot với token trong header 'Authorization'")
    print("   - Bot Framework SDK tự động verify token này")
    print()
    
    print("❓ Có thể generate token thủ công không?")
    print("   ❌ KHÔNG - Token phải được sign và verify với Microsoft's OpenID metadata")
    print("   ❌ Không thể fake token vì SDK sẽ verify với Microsoft servers")
    print()
    
    print("✅ Cách test bot đúng:")
    print()
    print("   1. Sử dụng Microsoft 365 Agents Toolkit (Khuyến nghị)")
    print("      - Press F5 trong VS Code")
    print("      - Chọn 'Debug in Teams'")
    print("      - Teams tự động xử lý authentication")
    print()
    print("   2. Sử dụng Bot Framework Emulator")
    print("      - Download: https://github.com/Microsoft/BotFramework-Emulator/releases")
    print("      - Connect đến http://localhost:3978/api/messages")
    print("      - Emulator tự động generate token hợp lệ")
    print()
    print("   3. Test qua Teams thực tế (Production-like)")
    print("      - Deploy bot lên Azure")
    print("      - Register bot trong Bot Framework")
    print("      - Test qua Teams app")
    print()
    
    if not config.APP_ID or not config.APP_PASSWORD:
        print("⚠️  Cấu hình hiện tại:")
        print(f"   CLIENT_ID: {'✅ Đã config' if config.APP_ID else '❌ Chưa config'}")
        print(f"   CLIENT_SECRET: {'✅ Đã config' if config.APP_PASSWORD else '❌ Chưa config'}")
        print()
        print("💡 Cách lấy credentials:")
        print("   1. Vào Azure Portal > App Registrations > Your Bot App")
        print("   2. Lấy Application (client) ID → CLIENT_ID")
        print("   3. Tạo Client Secret → CLIENT_SECRET")
        print("   4. Lưu vào env/.env.local hoặc env/.env.local.user")
    else:
        print("✅ Cấu hình đã đầy đủ:")
        print(f"   CLIENT_ID: {config.APP_ID[:20]}...")
        print(f"   CLIENT_SECRET: {'✅ Đã config' if config.APP_PASSWORD else '❌ Chưa config'}")
        print()
        print("💡 Bây giờ bạn có thể:")
        print("   - Press F5 trong VS Code để test qua Teams Toolkit")
        print("   - Hoặc sử dụng Bot Framework Emulator")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    explain_authentication()

