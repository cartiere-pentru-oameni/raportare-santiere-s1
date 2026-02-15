#!/usr/bin/env python3
"""Create first admin user"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

username = input("Admin username [admin]: ").strip() or "admin"
password = input("Admin password [admin123]: ").strip() or "admin123"

password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    with psycopg.connect(os.getenv('DATABASE_URL')) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO official_users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password_hash, 'admin')
            )
            conn.commit()

    print(f'\n✅ Admin created successfully!')
    print(f'   Username: {username}')
    print(f'   Password: {password}')
    print(f'\nLogin at: http://127.0.0.1:5000/login')
except Exception as e:
    print(f'\n❌ Error: {e}')
