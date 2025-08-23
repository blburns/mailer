#!/usr/bin/env python3
"""
Test VM Environment Script for Postfix Manager

This script tests if the Flask app can read environment variables on the VM.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test environment variable loading."""
    try:
        print("🧪 Testing VM Environment...")
        print("=" * 40)
        
        # Check current environment
        print("📋 Current environment variables:")
        print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
        print(f"   FLASK_APP: {os.environ.get('FLASK_APP', 'NOT SET')}")
        print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV', 'NOT SET')}")
        
        # Try to load .env file
        print("\n📁 Trying to load .env file...")
        try:
            from dotenv import load_dotenv
            env_path = project_root / '.env'
            if env_path.exists():
                print(f"   .env file found at: {env_path}")
                load_dotenv(env_path)
                print("   ✅ .env file loaded")
                
                # Check environment after loading
                print("\n📋 Environment after loading .env:")
                print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
                print(f"   FLASK_APP: {os.environ.get('FLASK_APP', 'NOT SET')}")
                print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV', 'NOT SET')}")
            else:
                print(f"   ❌ .env file not found at: {env_path}")
        except Exception as e:
            print(f"   ❌ Error loading .env: {e}")
        
        # Try to create Flask app
        print("\n🔧 Testing Flask app creation...")
        try:
            from app import create_app
            app = create_app()
            print("   ✅ Flask app created successfully")
            print(f"   📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
            print(f"   🔧 Secret Key: {app.config.get('SECRET_KEY', 'NOT SET')[:10]}...")
        except Exception as e:
            print(f"   ❌ Error creating Flask app: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing environment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_environment()
    sys.exit(0 if success else 1)
