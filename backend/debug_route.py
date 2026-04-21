# debug_routes.py
from app import create_app
import json

app = create_app()

print("=== Flask应用路由调试 ===")
print("已注册的路由：")
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

print("\n=== 测试端点 ===")
with app.test_client() as client:
    endpoints = ['/', '/health', '/api/users', '/api/users/test']
    
    for endpoint in endpoints:
        print(f"\n测试: {endpoint}")
        try:
            response = client.get(endpoint)
            print(f"  状态码: {response.status_code}")
            if response.data:
                data = json.loads(response.data)
                print(f"  响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"  错误: {e}")