"""
管理员设置脚本
用法：
    python set_admin.py <username>        # 将指定用户设为管理员
    python set_admin.py --create-admin    # 创建默认管理员账号
    python set_admin.py --list            # 列出所有用户及其管理员状态
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.models import User
from app.utils.helpers import hash_password


def set_user_as_admin(username):
    """将指定用户设为管理员"""
    app = create_app('development')
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"❌ 用户 '{username}' 不存在")
            return False
        
        if user.is_admin:
            print(f"✅ 用户 '{username}' 已经是管理员")
        else:
            user.is_admin = 1
            db.session.commit()
            print(f"✅ 已将用户 '{username}' 设为管理员")
        return True


def create_default_admin():
    """创建或更新默认管理员账号 (username: admin, password: admin123)"""
    app = create_app('development')
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # 更新密码和管理员状态
            admin.password = hash_password('admin123')
            admin.is_admin = 1
            admin.status = 1
            db.session.commit()
            print("✅ 管理员账号已更新：")
        else:
            # 创建新管理员
            admin = User(
                username='admin',
                password=hash_password('admin123'),
                phone='13800000000',
                email='admin@example.com',
                is_admin=1,
                status=1
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ 默认管理员账号已创建：")
        
        print(f"   用户名: admin")
        print(f"   密码: admin123")
        print(f"   管理员权限: 已启用")


def list_users():
    """列出所有用户及其管理员状态"""
    app = create_app('development')
    with app.app_context():
        users = User.query.all()
        if not users:
            print("📭 暂无用户")
            return
        
        print("\n用户列表：")
        print("-" * 60)
        print(f"{'ID':<6} {'用户名':<20} {'管理员':<8} {'状态':<8}")
        print("-" * 60)
        for u in users:
            admin_str = "是" if u.is_admin else "否"
            status_str = "正常" if u.status == 1 else "禁用"
            print(f"{u.user_id:<6} {u.username:<20} {admin_str:<8} {status_str:<8}")
        print("-" * 60)


def print_usage():
    print("""
用法:
    python set_admin.py <username>        # 将指定用户设为管理员
    python set_admin.py --create-admin    # 创建默认管理员账号 (admin/admin123)
    python set_admin.py --list            # 列出所有用户及管理员状态
    python set_admin.py --help            # 显示此帮助信息
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print_usage()
        sys.exit(0)
    
    arg = sys.argv[1]
    
    if arg == '--create-admin':
        create_default_admin()
    elif arg == '--list':
        list_users()
    else:
        # 假设参数是用户名
        set_user_as_admin(arg)