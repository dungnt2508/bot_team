"""
Script đơn giản để start bot Teams local
Chạy: python start_bot.py
"""
import sys
from pathlib import Path

# Thêm src vào path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import và chạy app
if __name__ == "__main__":
    import asyncio
    from app import app
    
    print("🚀 Đang khởi động Teams Bot...")
    print("📍 Bot sẽ chạy trên: http://localhost:3978")
    print("💡 Nhấn Ctrl+C để dừng\n")
    
    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        print("\n\n👋 Bot đã dừng")

