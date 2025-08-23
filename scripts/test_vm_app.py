#!/usr/bin/env python3
"""
Test VM App Script for Postfix Manager

This script tests if the Flask app can import and run on the VM.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_app():
    """Test if the app can import and run."""
    try:
        print("🧪 Testing VM App...")
        print("=" * 30)
        
        # Set database path
        db_path = "/opt/postfix-manager/instance/postfix_manager.db"
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        
        print("📦 Importing application...")
        from app import create_app
        
        print("🔧 Creating Flask app...")
        app = create_app()
        
        print("✅ App created successfully!")
        print(f"📁 App instance path: {app.instance_path}")
        print(f"🔧 Debug mode: {app.debug}")
        print(f"🌐 Environment: {getattr(app, 'env', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_app()
    sys.exit(0 if success else 1)
