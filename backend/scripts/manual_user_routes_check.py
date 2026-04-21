"""
Manual smoke check for user-related HTTP routes.

Usage:
    python backend/scripts/manual_user_routes_check.py

This script expects a development server on http://localhost:5000.
It is intentionally kept outside app/routes and avoids test_* names so pytest
does not collect it as an automated test.
"""

import requests


BASE_URL = "http://localhost:5000"


def check_public_endpoint(path):
    print(f"GET {path}")
    try:
        response = requests.get(BASE_URL + path, timeout=5)
        print(f"  status={response.status_code}")
        print(f"  body={response.text[:200]}")
    except Exception as exc:
        print(f"  error={exc}")


def check_authenticated_profile(username="test", password="123456"):
    print("POST /api/auth/login")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
        timeout=5,
    )
    print(f"  status={response.status_code}")
    response.raise_for_status()

    token = response.json().get("data", {}).get("token")
    if not token:
        raise RuntimeError("Login response did not include a token")

    print("GET /api/users/profile")
    profile = requests.get(
        f"{BASE_URL}/api/users/profile",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    print(f"  status={profile.status_code}")
    print(f"  body={profile.text[:200]}")


def main():
    print("Manual user route check")
    check_public_endpoint("/health")
    check_authenticated_profile()


if __name__ == "__main__":
    main()
