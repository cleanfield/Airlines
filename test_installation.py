"""
Test Script - Verify the Airline Reliability Tracker installation
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import requests
        print("  [OK] requests")
        import pandas
        print("  [OK] pandas")
        import matplotlib
        print("  [OK] matplotlib")
        import seaborn
        print("  [OK] seaborn")
        from dotenv import load_dotenv
        print("  [OK] python-dotenv")
        return True
    except ImportError as e:
        print(f"  [ERROR] Import error: {e}")
        return False

def test_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")
    try:
        import config
        print("  [OK] config")
        from schiphol_api import SchipholAPIClient
        print("  [OK] schiphol_api")
        from data_processor import FlightDataProcessor
        print("  [OK] data_processor")
        from visualizer import ReliabilityVisualizer
        print("  [OK] visualizer")
        return True
    except ImportError as e:
        print(f"  [ERROR] Import error: {e}")
        return False

def test_config():
    """Test if configuration is valid"""
    print("\nTesting configuration...")
    try:
        import config
        
        # Check API credentials
        if config.SCHIPHOL_CONFIG['app_id']:
            print(f"  [OK] Schiphol APP_ID: {config.SCHIPHOL_CONFIG['app_id']}")
        else:
            print("  [ERROR] Schiphol APP_ID not set")
            return False
            
        if config.SCHIPHOL_CONFIG['app_key']:
            print(f"  [OK] Schiphol APP_KEY: {config.SCHIPHOL_CONFIG['app_key'][:8]}...")
        else:
            print("  [ERROR] Schiphol APP_KEY not set")
            return False
        
        # Check directories
        if os.path.exists(config.DATA_DIR):
            print(f"  [OK] Data directory exists: {config.DATA_DIR}")
        else:
            print(f"  [ERROR] Data directory missing: {config.DATA_DIR}")
            return False
            
        return True
    except Exception as e:
        print(f"  [ERROR] Configuration error: {e}")
        return False

def test_api_client():
    """Test if API client can be initialized"""
    print("\nTesting API client...")
    try:
        from schiphol_api import SchipholAPIClient
        client = SchipholAPIClient()
        print(f"  [OK] API client initialized")
        print(f"  [OK] Base URL: {client.base_url}")
        print(f"  [OK] Resource Version: {client.resource_version}")
        return True
    except Exception as e:
        print(f"  [ERROR] API client error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("AIRLINE RELIABILITY TRACKER - INSTALLATION TEST")
    print("=" * 80)
    print()
    
    results = []
    
    # Run tests
    results.append(("Dependencies", test_imports()))
    results.append(("Custom Modules", test_modules()))
    results.append(("Configuration", test_config()))
    results.append(("API Client", test_api_client()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! Your installation is ready to use.")
        print("\nNext steps:")
        print("  1. Run: python main.py analyze")
        print("  2. Or see USAGE.md for more options")
        return 0
    else:
        print("\n[FAILED] Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Check .env file for API credentials")
        print("  3. See README.md for more help")
        return 1

if __name__ == "__main__":
    sys.exit(main())
