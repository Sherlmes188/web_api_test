#!/usr/bin/env python3
"""
页面可访问性测试脚本
验证服务条款和隐私政策页面是否正常工作
"""

import requests
import time
import sys
from urllib.parse import urljoin

def test_page_accessibility():
    """测试页面可访问性"""
    base_url = "http://localhost:5000"
    
    # 要测试的页面
    pages = {
        "主页": "/",
        "服务条款": "/terms", 
        "隐私政策": "/privacy"
    }
    
    print("🔍 正在测试页面可访问性...")
    print("=" * 50)
    
    all_passed = True
    
    for page_name, path in pages.items():
        url = urljoin(base_url, path)
        
        try:
            print(f"测试 {page_name}: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # 检查页面内容
                content = response.text
                
                if path == "/":
                    if "TikTok数据分析面板" in content:
                        print(f"  ✅ {page_name} - 正常访问")
                    else:
                        print(f"  ❌ {page_name} - 内容异常")
                        all_passed = False
                        
                elif path == "/terms":
                    if "服务条款" in content and "Terms of Service" in content:
                        print(f"  ✅ {page_name} - 正常访问")
                    else:
                        print(f"  ❌ {page_name} - 内容异常") 
                        all_passed = False
                        
                elif path == "/privacy":
                    if "隐私政策" in content and "Privacy Policy" in content:
                        print(f"  ✅ {page_name} - 正常访问")
                    else:
                        print(f"  ❌ {page_name} - 内容异常")
                        all_passed = False
                        
            else:
                print(f"  ❌ {page_name} - HTTP {response.status_code}")
                all_passed = False
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {page_name} - 连接失败 (应用未启动?)")
            all_passed = False
            
        except requests.exceptions.Timeout:
            print(f"  ❌ {page_name} - 请求超时")
            all_passed = False
            
        except Exception as e:
            print(f"  ❌ {page_name} - 错误: {e}")
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 所有页面测试通过！")
        print("\n📋 TikTok申请表单填写信息:")
        print(f"Terms of Service URL: {base_url}/terms")
        print(f"Privacy Policy URL: {base_url}/privacy")
        print("\n✅ 你可以将这些链接填写到TikTok开发者申请表单中")
        return True
    else:
        print("❌ 部分页面测试失败")
        print("\n🚨 请确保:")
        print("1. 应用正在运行 (python app.py)")
        print("2. 端口5000未被占用")
        print("3. 没有防火墙阻止访问")
        return False

def check_app_running():
    """检查应用是否在运行"""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """主函数"""
    print("🎯 TikTok开发者申请 - 页面测试工具")
    print("=" * 50)
    
    # 检查应用是否运行
    if not check_app_running():
        print("❌ 应用未启动!")
        print("\n请先启动应用:")
        print("  python app.py")
        print("\n然后重新运行此测试:")
        print("  python test_pages.py")
        sys.exit(1)
    
    # 等待一下确保应用完全启动
    print("⏳ 等待应用启动...")
    time.sleep(2)
    
    # 运行测试
    success = test_page_accessibility()
    
    if success:
        print("\n🚀 下一步:")
        print("1. 访问 https://developers.tiktok.com/")
        print("2. 创建新应用")
        print("3. 在表单中填写上述链接")
        print("4. 提交申请")
        
        # 自动在浏览器中打开页面供检查
        try:
            import webbrowser
            
            choice = input("\n是否在浏览器中打开页面进行检查? (y/n): ").strip().lower()
            if choice == 'y':
                webbrowser.open("http://localhost:5000")
                time.sleep(1)
                webbrowser.open("http://localhost:5000/terms")
                time.sleep(1) 
                webbrowser.open("http://localhost:5000/privacy")
                print("✅ 页面已在浏览器中打开")
        except:
            pass
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 