# test_user_routes.py
import requests
import json

def test_user_routes():
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("测试用户路由修复")
    print("=" * 60)
    
    # 1. 测试公开端点
    print("\n1. 测试公开端点:")
    endpoints = [
        ("/api/users/public-test", "GET", None),
        ("/api/users/test-no-auth", "GET", None)
    ]
    
    for endpoint, method, data in endpoints:
        print(f"\n测试: {method} {endpoint}")
        try:
            if method == "GET":
                response = requests.get(base_url + endpoint)
            else:
                response = requests.post(base_url + endpoint, json=data)
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功: {data.get('message', '成功')}")
            else:
                print(f"响应: {response.text[:200]}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    # 2. 测试需要认证的端点
    print("\n2. 测试需要认证的端点:")
    
    # 先登录获取token
    print("\n登录获取token...")
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "test", "password": "123456"}
    )
    
    if login_response.status_code == 200:
        token = login_response.json().get('data', {}).get('token')
        if token:
            print(f"✅ 登录成功，获取到token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试获取用户列表
            print("\n测试获取用户列表:")
            users_response = requests.get(f"{base_url}/api/users/", headers=headers)
            print(f"状态码: {users_response.status_code}")
            if users_response.status_code == 200:
                data = users_response.json()
                print(f"✅ 成功获取用户数据")
                if data.get('data'):
                    print(f"用户数量: {len(data.get('data', []))}")
            else:
                print(f"响应: {users_response.text[:200]}")
            
            # 测试获取用户资料
            print("\n测试获取用户资料:")
            profile_response = requests.get(f"{base_url}/api/users/profile", headers=headers)
            print(f"状态码: {profile_response.status_code}")
            if profile_response.status_code == 200:
                data = profile_response.json()
                print(f"✅ 成功获取用户资料")
                print(f"用户名: {data.get('data', {}).get('username')}")
        else:
            print("❌ 登录响应中没有token")
    else:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(f"响应: {login_response.text}")
    
    print("\n" + "=" * 60)
    print("测试完成!")

if __name__ == "__main__":
    test_user_routes()