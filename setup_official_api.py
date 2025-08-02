#!/usr/bin/env python3
"""
TikTok官方API设置助手
帮助用户配置官方API凭证和OAuth认证
"""

import os
import sys
import webbrowser
from config import Config

def print_banner():
    """打印横幅"""
    print("=" * 70)
    print("🏢 TikTok官方API设置助手")
    print("=" * 70)
    print()

def check_current_config():
    """检查当前配置"""
    print("📋 当前官方API配置状态:")
    print(f"   Client Key: {'✅ 已配置' if Config.TIKTOK_CLIENT_KEY else '❌ 未配置'}")
    print(f"   Client Secret: {'✅ 已配置' if Config.TIKTOK_CLIENT_SECRET else '❌ 未配置'}")
    print(f"   回调URL: {Config.TIKTOK_REDIRECT_URI}")
    
    if Config.TIKTOK_CLIENT_KEY:
        masked_key = Config.TIKTOK_CLIENT_KEY[:8] + "..." + Config.TIKTOK_CLIENT_KEY[-4:]
        print(f"   Client Key预览: {masked_key}")
    
    print()
    print(f"🔧 配置状态: {Config.get_api_type()}")
    print()

def show_registration_guide():
    """显示注册指南"""
    print("📚 TikTok官方API注册指南")
    print("-" * 40)
    print()
    print("🔗 访问开发者平台:")
    print("   https://developers.tiktok.com/")
    print()
    print("📝 申请步骤:")
    print("   1. 注册/登录TikTok开发者账号")
    print("   2. 创建新应用")
    print("   3. 填写应用信息:")
    print("      - 应用名称: TikTok Data Analytics Dashboard")
    print("      - 应用类型: Analytics & Data")
    print("      - 回调URL: http://localhost:5000/callback")
    print("   4. 申请以下权限:")
    print("      - user.info.basic")
    print("      - user.info.profile")
    print("      - user.info.stats")
    print("      - video.list")
    print("   5. 等待审核（1-2周）")
    print()
    print("📄 申请材料:")
    print("   - 应用截图和演示")
    print("   - 数据使用说明")
    print("   - 隐私政策")
    print("   - 商业计划概述")
    print()

def open_developer_portal():
    """打开开发者门户"""
    print("🌐 正在打开TikTok开发者平台...")
    try:
        webbrowser.open("https://developers.tiktok.com/")
        print("✅ 已在浏览器中打开开发者平台")
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")
        print("请手动访问: https://developers.tiktok.com/")
    print()

def setup_credentials():
    """设置API凭证"""
    print("🔑 设置TikTok官方API凭证")
    print("请从开发者控制台获取以下信息:")
    print()
    
    # 设置Client Key
    client_key = input("请输入 Client Key: ").strip()
    if not client_key:
        print("❌ Client Key不能为空")
        return False
    
    # 设置Client Secret
    client_secret = input("请输入 Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret不能为空")
        return False
    
    # 设置回调URL（可选）
    redirect_uri = input(f"回调URL (默认: {Config.TIKTOK_REDIRECT_URI}): ").strip()
    if not redirect_uri:
        redirect_uri = Config.TIKTOK_REDIRECT_URI
    
    # 设置环境变量
    os.environ['TIKTOK_CLIENT_KEY'] = client_key
    os.environ['TIKTOK_CLIENT_SECRET'] = client_secret
    os.environ['TIKTOK_REDIRECT_URI'] = redirect_uri
    
    print()
    print("✅ API凭证已设置为环境变量")
    print()
    print("💡 要永久保存凭证，请在系统中设置环境变量：")
    print(f"   set TIKTOK_CLIENT_KEY={client_key}")
    print(f"   set TIKTOK_CLIENT_SECRET={client_secret}")
    print(f"   set TIKTOK_REDIRECT_URI={redirect_uri}")
    print()
    
    return True

def test_oauth_flow():
    """测试OAuth流程"""
    print("🔍 测试OAuth授权流程...")
    
    if not Config.has_official_api_config():
        print("❌ 请先配置API凭证")
        return False
    
    try:
        from oauth_handler import TikTokOAuth
        
        oauth = TikTokOAuth()
        auth_url, state = oauth.get_auth_url()
        
        print("✅ OAuth配置正确")
        print()
        print("🔗 授权URL已生成:")
        print(f"   {auth_url}")
        print()
        print("📋 授权流程:")
        print("   1. 启动应用: python app.py")
        print("   2. 访问应用: http://localhost:5000")
        print("   3. 点击授权按钮或访问: http://localhost:5000/auth")
        print("   4. 完成TikTok授权")
        print("   5. 查看真实数据")
        print()
        
        choice = input("是否在浏览器中打开授权URL? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                webbrowser.open(auth_url)
                print("✅ 已在浏览器中打开授权页面")
            except Exception as e:
                print(f"❌ 无法打开浏览器: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth测试失败: {e}")
        return False

def start_application():
    """启动应用"""
    print("🚀 启动TikTok数据分析面板...")
    print()
    print("请在新的终端窗口中运行:")
    print("   python app.py")
    print()
    print("然后访问: http://localhost:5000")
    print()
    print("🔗 授权流程:")
    print("   1. 在应用中点击授权按钮")
    print("   2. 或直接访问: http://localhost:5000/auth")
    print("   3. 完成TikTok登录和授权")
    print("   4. 返回应用查看真实数据")
    print()

def show_troubleshooting():
    """显示故障排除指南"""
    print("🚨 常见问题和解决方案")
    print("-" * 40)
    print()
    print("❓ 问题1: 应用审核被拒")
    print("   💡 解决方案:")
    print("      - 提供更详细的应用描述")
    print("      - 添加应用截图和演示")
    print("      - 明确数据使用目的")
    print("      - 提供隐私政策文档")
    print()
    print("❓ 问题2: OAuth授权失败")
    print("   💡 解决方案:")
    print("      - 检查回调URL是否正确")
    print("      - 确认Client Key和Secret正确")
    print("      - 检查应用权限设置")
    print("      - 清除浏览器缓存重试")
    print()
    print("❓ 问题3: API调用限制")
    print("   💡 解决方案:")
    print("      - 降低数据更新频率")
    print("      - 检查API配额使用情况")
    print("      - 升级开发者计划")
    print()
    print("❓ 问题4: 访问令牌过期")
    print("   💡 解决方案:")
    print("      - 实现自动令牌刷新")
    print("      - 重新进行OAuth授权")
    print()

def main():
    """主函数"""
    print_banner()
    
    while True:
        check_current_config()
        
        print("请选择操作：")
        print("1. 查看注册指南")
        print("2. 打开开发者平台")
        print("3. 设置API凭证")
        print("4. 测试OAuth流程")
        print("5. 启动应用")
        print("6. 故障排除")
        print("7. 退出")
        print()
        
        choice = input("请输入选择 (1-7): ").strip()
        
        if choice == '1':
            show_registration_guide()
        elif choice == '2':
            open_developer_portal()
        elif choice == '3':
            setup_credentials()
        elif choice == '4':
            test_oauth_flow()
        elif choice == '5':
            start_application()
        elif choice == '6':
            show_troubleshooting()
        elif choice == '7':
            print("👋 退出设置")
            sys.exit(0)
        else:
            print("❌ 无效选择，请重试")
        
        input("按Enter键继续...")
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main() 