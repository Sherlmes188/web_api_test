#!/usr/bin/env python3
"""
TikTok API 设置助手脚本
用于快速配置API密钥和用户名
"""

import os
import sys
from config import Config

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🎵 TikTok数据分析面板 - API设置助手")
    print("=" * 60)
    print()

def check_current_config():
    """检查当前配置"""
    print("📋 当前配置状态:")
    print(f"   API密钥: {'✅ 已配置' if Config.has_api_key() else '❌ 未配置'}")
    print(f"   用户名: {'✅ 已配置' if Config.TIKTOK_USERNAME else '❌ 未配置'}")
    
    if Config.has_api_key():
        api_key = Config.get_api_key()
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"   API密钥预览: {masked_key}")
    
    if Config.TIKTOK_USERNAME:
        print(f"   配置用户名: {Config.TIKTOK_USERNAME}")
    
    print()

def setup_api_key():
    """设置API密钥"""
    print("🔑 API密钥设置")
    print("推荐使用TikAPI服务：https://tikapi.io/")
    print()
    
    api_key = input("请输入你的API密钥: ").strip()
    
    if not api_key:
        print("❌ API密钥不能为空")
        return False
    
    # 设置环境变量
    os.environ['TIKAPI_KEY'] = api_key
    
    print("✅ API密钥已设置为环境变量")
    print("💡 要永久保存，请在系统中设置环境变量：")
    print(f"   set TIKAPI_KEY={api_key}")
    print()
    
    return True

def setup_username():
    """设置TikTok用户名"""
    print("👤 TikTok用户名设置")
    print("请输入你想要分析的TikTok用户名（不包含@符号）")
    print()
    
    username = input("TikTok用户名: ").strip().replace('@', '')
    
    if not username:
        print("❌ 用户名不能为空")
        return False
    
    # 设置环境变量
    os.environ['TIKTOK_USERNAME'] = username
    
    print(f"✅ 用户名已设置为: {username}")
    print("💡 要永久保存，请在系统中设置环境变量：")
    print(f"   set TIKTOK_USERNAME={username}")
    print()
    
    return True

def test_api_connection():
    """测试API连接"""
    print("🔍 测试API连接...")
    
    try:
        from tiktok_api import TikTokDataFetcher
        
        fetcher = TikTokDataFetcher(api_key=Config.get_api_key())
        
        if Config.TIKTOK_USERNAME:
            print(f"正在测试用户: {Config.TIKTOK_USERNAME}")
            user_info = fetcher.get_user_info(Config.TIKTOK_USERNAME)
            
            if user_info and 'userInfo' in user_info:
                user_data = user_info['userInfo']['user']
                print(f"✅ 连接成功！")
                print(f"   用户昵称: {user_data.get('nickname', 'N/A')}")
                print(f"   粉丝数: {user_data.get('followerCount', 0):,}")
                print(f"   视频数: {user_data.get('videoCount', 0):,}")
                return True
            else:
                print("❌ 获取用户信息失败")
                return False
        else:
            print("❌ 未设置用户名，无法测试")
            return False
            
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    while True:
        check_current_config()
        
        print("请选择操作：")
        print("1. 设置API密钥")
        print("2. 设置TikTok用户名")
        print("3. 测试API连接")
        print("4. 完成设置并启动应用")
        print("5. 退出")
        print()
        
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == '1':
            setup_api_key()
        elif choice == '2':
            setup_username()
        elif choice == '3':
            test_api_connection()
        elif choice == '4':
            if Config.has_api_key() and Config.TIKTOK_USERNAME:
                print("🚀 配置完成！正在启动应用...")
                print("请运行: python app.py")
                break
            else:
                print("❌ 请先完成API密钥和用户名的设置")
        elif choice == '5':
            print("👋 退出设置")
            sys.exit(0)
        else:
            print("❌ 无效选择，请重试")
        
        print()

if __name__ == "__main__":
    main() 