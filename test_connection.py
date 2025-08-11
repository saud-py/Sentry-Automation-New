#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to verify Sentry API connection
"""

import os
import sys
import requests
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from dotenv import load_dotenv

def test_sentry_connection():
    """Test Sentry API connection."""
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    org_slug = os.getenv('SENTRY_ORG_SLUG')
    api_base_url = os.getenv('SENTRY_API_BASE_URL', 'https://sentry.io/api/0')
    
    print("🔍 Testing Sentry Connection")
    print(f"   Auth Token: {auth_token[:20]}..." if auth_token else "❌ No auth token")
    print(f"   Org Slug: {org_slug}")
    print(f"   API URL: {api_base_url}")
    print()
    
    if not auth_token:
        print("❌ SENTRY_AUTH_TOKEN not found in .env file")
        return False
    
    if not org_slug:
        print("❌ SENTRY_ORG_SLUG not found in .env file")
        return False
    
    # Test the API
    url = f"{api_base_url}/organizations/{org_slug}/"
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'User-Agent': 'SentryAlertAutomation/1.0'
    }
    
    print(f"🌐 Making request to: {url}")
    print()
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"📊 Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success! Organization: {data.get('name', 'Unknown')}")
                return True
            except ValueError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_sentry_connection()
    sys.exit(0 if success else 1) 