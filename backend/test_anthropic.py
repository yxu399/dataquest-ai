#!/usr/bin/env python3
"""Test Anthropic client initialization"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

try:
    from anthropic import Anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"API key found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"API key starts with: {api_key[:10]}...")
        client = Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized successfully")

        # Test a simple call
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print(f"✅ API call successful: {response.content[0].text}")
    else:
        print("❌ ANTHROPIC_API_KEY not found")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()