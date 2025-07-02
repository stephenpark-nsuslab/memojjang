#!/usr/bin/env python
"""
Production readiness check script for Memojjang
Run this script to verify production settings before deployment
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'DJANGO_SECRET_KEY',
        'DJANGO_DEBUG',
        'DJANGO_ALLOWED_HOSTS'
    ]
    
    recommended_vars = [
        'SECURE_SSL_REDIRECT',
        'USE_X_FORWARDED_PROTO',
        'SECURE_HSTS_SECONDS'
    ]
    
    missing_required = []
    missing_recommended = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"  ✅ {var} is set")
    
    for var in recommended_vars:
        if not os.getenv(var):
            missing_recommended.append(var)
        else:
            print(f"  ✅ {var} is set")
    
    if missing_required:
        print(f"  ❌ Missing required variables: {', '.join(missing_required)}")
        return False
    
    if missing_recommended:
        print(f"  ⚠️  Missing recommended variables: {', '.join(missing_recommended)}")
    
    return True

def check_debug_setting():
    """Check if DEBUG is disabled in production"""
    print("\n🔍 Checking DEBUG setting...")
    
    debug = os.getenv('DJANGO_DEBUG', 'False')
    if debug.lower() == 'false':
        print("  ✅ DEBUG is disabled")
        return True
    else:
        print(f"  ❌ DEBUG is enabled ({debug}). Set DJANGO_DEBUG=False for production")
        return False

def check_secret_key():
    """Check if SECRET_KEY is secure"""
    print("\n🔍 Checking SECRET_KEY...")
    
    secret_key = os.getenv('DJANGO_SECRET_KEY', '')
    
    if not secret_key:
        print("  ❌ SECRET_KEY is not set")
        return False
    
    if secret_key == 'your-default-secret-key' or secret_key == 'your-super-secret-key-here':
        print("  ❌ SECRET_KEY is using default value. Generate a new secure key!")
        return False
    
    if len(secret_key) < 50:
        print("  ⚠️  SECRET_KEY is quite short. Consider using a longer key")
        return True
    
    print("  ✅ SECRET_KEY appears to be secure")
    return True

def check_allowed_hosts():
    """Check if ALLOWED_HOSTS is properly configured"""
    print("\n🔍 Checking ALLOWED_HOSTS...")
    
    allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', '')
    
    if not allowed_hosts:
        print("  ❌ ALLOWED_HOSTS is empty")
        return False
    
    hosts = [host.strip() for host in allowed_hosts.split(',') if host.strip()]
    
    if not hosts:
        print("  ❌ ALLOWED_HOSTS contains no valid hosts")
        return False
    
    # Check for development values in production
    dev_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
    if any(host in dev_hosts for host in hosts):
        print(f"  ⚠️  ALLOWED_HOSTS contains development hosts: {hosts}")
        print("     Make sure to include your production domain")
    
    print(f"  ✅ ALLOWED_HOSTS is configured: {hosts}")
    return True

def check_django_config():
    """Run Django's deployment checklist"""
    print("\n🔍 Running Django deployment checklist...")
    
    try:
        # Create temporary environment with production settings
        env = os.environ.copy()
        env['DJANGO_DEBUG'] = 'False'
        env['PYTHONPATH'] = str(Path.cwd())
        
        result = subprocess.run([
            sys.executable, 'memojjang/manage.py', 'check', '--deploy'
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("  ✅ Django deployment check passed")
            if result.stdout.strip():
                print(f"  📋 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"  ❌ Django deployment check failed:")
            print(f"     {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error running Django check: {e}")
        return False

def check_static_files():
    """Check if static files can be collected"""
    print("\n🔍 Checking static files configuration...")
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            env['DJANGO_STATIC_ROOT'] = temp_dir
            
            result = subprocess.run([
                sys.executable, 'memojjang/manage.py', 'collectstatic', '--noinput', '--dry-run'
            ], capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                print("  ✅ Static files collection test passed")
                return True
            else:
                print(f"  ❌ Static files collection test failed:")
                print(f"     {result.stderr.strip()}")
                return False
                
    except Exception as e:
        print(f"  ❌ Error testing static files: {e}")
        return False

def check_database_config():
    """Check database configuration"""
    print("\n🔍 Checking database configuration...")
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        result = subprocess.run([
            sys.executable, 'memojjang/manage.py', 'migrate', '--run-syncdb', '--dry-run'
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("  ✅ Database configuration appears valid")
            return True
        else:
            print(f"  ❌ Database configuration issue:")
            print(f"     {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
        return False

def generate_secret_key():
    """Generate a new Django secret key"""
    try:
        from django.core.management.utils import get_random_secret_key
        return get_random_secret_key()
    except ImportError:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(alphabet) for _ in range(50))

def main():
    """Run all production readiness checks"""
    print("🚀 Memojjang Production Readiness Check")
    print("=" * 50)
    
    checks = [
        check_environment_variables,
        check_debug_setting,
        check_secret_key,
        check_allowed_hosts,
        check_django_config,
        check_static_files,
        check_database_config
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your application is ready for production.")
    elif passed >= total - 1:
        print("⚠️  Almost ready! Please address the warnings above.")
    else:
        print("❌ Several issues need to be addressed before deployment.")
        
        # Offer to generate a new secret key if needed
        if os.getenv('DJANGO_SECRET_KEY') in ['your-default-secret-key', 'your-super-secret-key-here', None]:
            print("\n💡 Need a new SECRET_KEY? Here's a secure one:")
            print(f"   DJANGO_SECRET_KEY={generate_secret_key()}")
    
    print("\n📚 For more information, see DEPLOYMENT.md")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)