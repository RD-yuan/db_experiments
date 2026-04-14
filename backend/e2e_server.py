"""
Self-contained backend entrypoint for E2E tests.

It boots the Flask app against a local SQLite database, recreates schema,
and seeds the minimum data needed by browser smoke tests.
"""
from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

from app import create_app, db
from app.models.models import Category, Product, User
from app.utils.helpers import hash_password


BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = BACKEND_DIR / "e2e.sqlite3"
PORT = int(os.environ.get("E2E_BACKEND_PORT", "5010"))


def seed_data() -> None:
    """Insert deterministic fixtures used by Playwright smoke tests."""
    admin = User(
        username="admin",
        password=hash_password("admin123"),
        email="admin@example.com",
    )
    existing_user = User(
        username="existinguser",
        password=hash_password("123456"),
        email="existinguser@example.com",
        phone="13900000000",
    )

    category = Category(
        name="E2E 分类",
        parent_id=0,
        level=1,
        sort_order=1,
        status=1,
    )

    db.session.add_all([admin, existing_user, category])
    db.session.flush()

    db.session.add_all(
        [
            Product(
                name="E2E 测试商品",
                description="用于验证注册、商品浏览和加购流程。",
                price=Decimal("199.00"),
                original_price=Decimal("299.00"),
                vip_price=Decimal("189.00"),
                stock=30,
                sold_count=5,
                category_id=category.category_id,
                brand="Codex",
                status=1,
                is_hot=1,
                is_new=1,
                main_image="https://via.placeholder.com/400x400?text=E2E+Product",
            ),
            Product(
                name="E2E 备用商品",
                description="用于补充商品列表数据。",
                price=Decimal("59.00"),
                stock=12,
                sold_count=2,
                category_id=category.category_id,
                brand="Codex",
                status=1,
                main_image="https://via.placeholder.com/400x400?text=Backup+Product",
            ),
        ]
    )
    db.session.commit()


def create_e2e_app():
    """Build an app configured for repeatable local E2E runs."""
    if DB_PATH.exists():
        DB_PATH.unlink()

    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"
    os.environ.setdefault("SECRET_KEY", "e2e-secret-key")
    os.environ.setdefault("JWT_SECRET_KEY", "e2e-jwt-secret-key")

    app = create_app("development")
    app.config.update(
        DEBUG=False,
        TESTING=True,
        SQLALCHEMY_ECHO=False,
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()

    return app


app = create_e2e_app()


if __name__ == "__main__":
    print(f"Starting E2E backend at http://127.0.0.1:{PORT}")
    print(f"Using SQLite database: {DB_PATH}")
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
