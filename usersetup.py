#!/usr/bin/env python
"""Create an initial admin user."""

import argparse

from loradb.auth import AuthManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("user", help="username")
    parser.add_argument("password", help="password")
    args = parser.parse_args()

    auth = AuthManager()
    auth.create_user(args.user, args.password, role="admin")
    print(f"Admin user '{args.user}' created")


if __name__ == "__main__":
    main()
