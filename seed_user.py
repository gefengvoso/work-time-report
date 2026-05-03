#!/usr/bin/env python3
"""Run once to create the initial admin user.

Before running:
  1. In Supabase dashboard → Authentication → Providers → Email
     disable "Confirm email" so login works immediately.
  2. pip install -r requirements.txt

Usage:
  python seed_user.py
"""
import os
import getpass
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

email = input('Email: ').strip()
password = getpass.getpass('Password: ')

try:
    res = client.auth.sign_up({'email': email, 'password': password})
    print(f'User created: {res.user.email}')
    print('You can now log in at http://localhost:5001/login')
except Exception as e:
    print(f'Error: {e}')
