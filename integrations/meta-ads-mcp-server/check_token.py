#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('FACEBOOK_ACCESS_TOKEN')

if token and token != 'your_facebook_access_token_here':
    print(f'✅ Token loaded: {token[:20]}... (length: {len(token)})')
    print('🎯 Ready to test Facebook connection!')
else:
    print('❌ Token not configured properly')
    print(f'Current value: {token}')
    print('Please update the .env file with your actual Facebook access token.')