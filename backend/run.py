"""
Flask 应用启动入口
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db

# 从环境变量获取配置名称，默认为 development
config_name = os.environ.get('FLASK_ENV', 'development')

app = create_app(config_name)

# Flask Shell 上下文
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'app': app}


if __name__ == '__main__':
    # 开发环境启动
    print(f"Starting Flask app in {config_name} mode...")
    print(f"API Docs: http://localhost:5000/apidocs")
    print(f"Health Check: http://localhost:5000/health")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
