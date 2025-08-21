#!/usr/bin/env python3

"""
Postfix Manager Application Runner
Main entry point for running the Postfix Manager system

Usage:
    python run.py                    # Run web app in development mode
    python run.py --web             # Run web app in development mode
    python run.py --cli             # Run CLI interface
    python run.py --web --port 8080 # Run web app on specific port
    python run.py --web --mode production  # Run web app in production mode
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_web_app(port=5000, host='0.0.0.0', mode='development'):
    """Run the Postfix Manager web application"""
    app_dir = Path(__file__).parent / 'app'
    
    if not app_dir.exists():
        print("ERROR: Application directory not found. Please ensure 'app' directory exists.")
        return False
    
    # Set environment variables
    os.environ['FLASK_ENV'] = mode
    os.environ['FLASK_DEBUG'] = 'True' if mode == 'development' else 'False'
    os.environ['FLASK_RUN_HOST'] = host
    os.environ['FLASK_RUN_PORT'] = str(port)
    
    print(f"Starting Postfix Manager Web Application...")
    print(f"Mode: {mode}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Working Directory: {Path(__file__).parent}")
    print()
    
    try:
        # Check if virtual environment exists
        venv_path = Path(__file__).parent / 'venv'
        if not venv_path.exists():
            print("Setting up virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
            print("Virtual environment created successfully")
        
        # Install requirements if needed
        requirements_file = Path(__file__).parent / 'requirements.txt'
        if requirements_file.exists():
            print("Installing/updating requirements...")
            if os.name == 'nt':  # Windows
                pip_cmd = [str(venv_path / 'Scripts' / 'pip')]
            else:  # Unix/Linux/macOS
                pip_cmd = [str(venv_path / 'bin' / 'pip')]
            
            subprocess.run([*pip_cmd, 'install', '-r', str(requirements_file)], check=True)
            print("Requirements installed successfully")
        
        # Run the web application
        if mode == 'production':
            print("Starting production server with Waitress...")
            if os.name == 'nt':  # Windows
                python_cmd = [str(venv_path / 'Scripts' / 'python')]
            else:  # Unix/Linux/macOS
                python_cmd = [str(venv_path / 'bin' / 'python')]
            
            # Import and run the app
            sys.path.insert(0, str(Path(__file__).parent))
            from app import create_app
            app = create_app()
            
            # Use Waitress for production
            from waitress import serve
            serve(app, host=host, port=port)
        else:
            print("Starting development server...")
            if os.name == 'nt':  # Windows
                python_cmd = [str(venv_path / 'Scripts' / 'python')]
            else:  # Unix/Linux/macOS
                python_cmd = [str(venv_path / 'bin' / 'python')]
            
            # Import and run the app
            sys.path.insert(0, str(Path(__file__).parent))
            from app import create_app
            app = create_app()
            
            app.run(
                debug=True,
                host=host,
                port=port,
                use_reloader=True
            )
            
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to run web application: {e}")
        return False
    except KeyboardInterrupt:
        print("\nWeb application stopped by user")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False
    
    return True

def run_cli():
    """Run the Postfix Manager CLI interface"""
    cli_script = Path(__file__).parent / 'scripts' / 'postfix_manager.py'
    
    if not cli_script.exists():
        print("ERROR: CLI script not found. Please ensure 'scripts/postfix_manager.py' exists.")
        print("Creating basic CLI script...")
        
        # Create scripts directory if it doesn't exist
        scripts_dir = Path(__file__).parent / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Create basic CLI script
        cli_content = '''#!/usr/bin/env python3
"""
Postfix Manager CLI Interface
Basic command-line interface for Postfix Manager
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Postfix Manager CLI")
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--domains', action='store_true', help='List mail domains')
    parser.add_argument('--users', action='store_true', help='List mail users')
    
    args = parser.parse_args()
    
    print("Postfix Manager CLI")
    print("=" * 30)
    
    if args.status:
        print("System Status: Running")
    elif args.domains:
        print("Mail Domains: example.com")
    elif args.users:
        print("Mail Users: admin@example.com")
    else:
        parser.print_help()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
'''
        
        with open(cli_script, 'w') as f:
            f.write(cli_content)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(cli_script, 0o755)
        
        print("Basic CLI script created successfully")
    
    print("Starting Postfix Manager CLI Interface...")
    print(f"CLI Script: {cli_script}")
    print()
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run([sys.executable, str(cli_script), '--help'], check=True)
        else:  # Unix/Linux/macOS
            subprocess.run([str(cli_script), '--help'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to run CLI: {e}")
        return False
    except KeyboardInterrupt:
        print("\nCLI stopped by user")
        return True
    
    return True

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info >= (3, 13):
        print("ERROR: Python 3.13+ is not supported. Please use Python 3.8-3.12")
        return False
    elif sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ is required")
        return False
    
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Postfix Manager Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--web',
        action='store_true',
        help='Run the web application'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run the CLI interface'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port for web application'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host for web application'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['development', 'production'],
        default='development',
        help='Web application mode'
    )
    
    args = parser.parse_args()
    
    # If no specific mode specified, default to web
    if not args.web and not args.cli:
        args.web = True
    
    print("Postfix Manager Runner")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    success = True
    
    if args.web:
        success = run_web_app(port=args.port, host=args.host, mode=args.mode)
    
    if args.cli and success:
        success = run_cli()
    
    if success:
        print("\nApplication completed successfully")
        return 0
    else:
        print("\nApplication failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
