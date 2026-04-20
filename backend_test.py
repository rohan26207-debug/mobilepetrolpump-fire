#!/usr/bin/env python3
"""
Backend API Smoke Tests for Petrol Pump Manager Application
Tests all backend endpoints with real data
"""

import requests
import json
from datetime import datetime, timezone
import time
import sys

# Base URL from frontend/.env
BASE_URL = "https://data-management-hub-3.preview.emergentagent.com/api"

# Test results storage
test_results = []

def log_test(test_name, passed, details="", response_snippet=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({
        "test": test_name,
        "status": status,
        "passed": passed,
        "details": details,
        "response": response_snippet
    })
    print(f"{status} - {test_name}")
    if details:
        print(f"  Details: {details}")
    if response_snippet:
        print(f"  Response: {response_snippet}")
    print()

def test_health_check():
    """Test 1: Health Check"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        
        # Check CORS headers
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'Not present')
        
        if response.status_code == 200:
            data = response.json()
            if data.get("message") == "Hello World":
                log_test(
                    "Health Check",
                    True,
                    f"Status: {response.status_code}, CORS: {cors_header}",
                    json.dumps(data, indent=2)
                )
                return True, cors_header
            else:
                log_test(
                    "Health Check",
                    False,
                    f"Unexpected response: {data}",
                    json.dumps(data, indent=2)
                )
                return False, cors_header
        else:
            log_test(
                "Health Check",
                False,
                f"Status: {response.status_code}",
                response.text[:200]
            )
            return False, cors_header
    except Exception as e:
        log_test("Health Check", False, f"Exception: {str(e)}")
        return False, "N/A"

def test_auth_flow():
    """Test 2: Auth Flow - Register, Login, /auth/me"""
    print("=" * 60)
    print("TEST 2: Auth Flow")
    print("=" * 60)
    
    # Generate unique username with epoch milliseconds
    epoch_ms = int(time.time() * 1000)
    username = f"test_user_{epoch_ms}"
    password = "TestPass123!"
    full_name = "Test User"
    
    token = None
    user_id = None
    
    # Step 1: Register
    print(f"\nStep 1: Register user '{username}'")
    try:
        register_data = {
            "username": username,
            "password": password,
            "full_name": full_name
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            if all(key in data for key in ["access_token", "token_type", "user_id", "username"]):
                token = data["access_token"]
                user_id = data["user_id"]
                log_test(
                    "Auth - Register",
                    True,
                    f"User created: {username}, user_id: {user_id}",
                    json.dumps(data, indent=2)
                )
            else:
                log_test(
                    "Auth - Register",
                    False,
                    f"Missing required fields in response",
                    json.dumps(data, indent=2)
                )
                return None
        elif response.status_code == 400 and "already registered" in response.text.lower():
            log_test(
                "Auth - Register",
                True,
                f"Username already exists (expected), proceeding to login",
                response.text[:200]
            )
        else:
            log_test(
                "Auth - Register",
                False,
                f"Status: {response.status_code}",
                response.text[:200]
            )
            return None
    except Exception as e:
        log_test("Auth - Register", False, f"Exception: {str(e)}")
        return None
    
    # Step 2: Login
    print(f"\nStep 2: Login with '{username}'")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                token = data["access_token"]
                user_id = data.get("user_id")
                log_test(
                    "Auth - Login",
                    True,
                    f"Login successful, token received",
                    json.dumps(data, indent=2)
                )
            else:
                log_test(
                    "Auth - Login",
                    False,
                    f"Missing access_token in response",
                    json.dumps(data, indent=2)
                )
                return None
        else:
            log_test(
                "Auth - Login",
                False,
                f"Status: {response.status_code}",
                response.text[:200]
            )
            return None
    except Exception as e:
        log_test("Auth - Login", False, f"Exception: {str(e)}")
        return None
    
    # Step 3: Get current user info
    print(f"\nStep 3: Get /auth/me")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if all(key in data for key in ["id", "username", "created_at"]):
                log_test(
                    "Auth - /auth/me",
                    True,
                    f"User info retrieved: {data.get('username')}",
                    json.dumps(data, indent=2)
                )
                return token
            else:
                log_test(
                    "Auth - /auth/me",
                    False,
                    f"Missing required fields",
                    json.dumps(data, indent=2)
                )
                return None
        else:
            log_test(
                "Auth - /auth/me",
                False,
                f"Status: {response.status_code}",
                response.text[:200]
            )
            return None
    except Exception as e:
        log_test("Auth - /auth/me", False, f"Exception: {str(e)}")
        return None

def test_protected_crud(token):
    """Test 3: Protected CRUD operations"""
    print("=" * 60)
    print("TEST 3: Protected CRUD Operations")
    print("=" * 60)
    
    if not token:
        log_test("Protected CRUD", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    today = datetime.now().strftime("%Y-%m-%d")
    
    all_passed = True
    
    # Test 3.1: Fuel Sales
    print("\n--- Fuel Sales ---")
    try:
        # Create fuel sale
        fuel_sale_data = {
            "date": today,
            "fuel_type": "diesel",
            "nozzle_id": "N1",
            "opening_reading": 1000,
            "closing_reading": 1100,
            "liters": 100,
            "rate": 95.5,
            "amount": 9550
        }
        response = requests.post(f"{BASE_URL}/fuel-sales", json=fuel_sale_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fuel_sale_id = data.get("id")
            log_test(
                "Fuel Sales - Create",
                True,
                f"Created fuel sale with id: {fuel_sale_id}",
                json.dumps(data, indent=2)
            )
            
            # Get fuel sales
            response = requests.get(f"{BASE_URL}/fuel-sales?date={today}", headers=headers, timeout=10)
            if response.status_code == 200:
                sales = response.json()
                found = any(sale.get("id") == fuel_sale_id for sale in sales)
                has_mongo_id = any("_id" in sale for sale in sales)
                
                if found and not has_mongo_id:
                    log_test(
                        "Fuel Sales - Get",
                        True,
                        f"Retrieved {len(sales)} sales, found created record, no _id field",
                        json.dumps(sales[:2], indent=2) if sales else "[]"
                    )
                else:
                    log_test(
                        "Fuel Sales - Get",
                        False,
                        f"Found: {found}, Has _id: {has_mongo_id}",
                        json.dumps(sales[:2], indent=2) if sales else "[]"
                    )
                    all_passed = False
            else:
                log_test("Fuel Sales - Get", False, f"Status: {response.status_code}", response.text[:200])
                all_passed = False
        else:
            log_test("Fuel Sales - Create", False, f"Status: {response.status_code}", response.text[:200])
            all_passed = False
    except Exception as e:
        log_test("Fuel Sales", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3.2: Credit Sales
    print("\n--- Credit Sales ---")
    try:
        credit_sale_data = {
            "date": today,
            "customer_name": "Test Customer",
            "amount": 1234.5,
            "description": "backend test"
        }
        response = requests.post(f"{BASE_URL}/credit-sales", json=credit_sale_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            credit_sale_id = data.get("id")
            log_test(
                "Credit Sales - Create",
                True,
                f"Created credit sale with id: {credit_sale_id}",
                json.dumps(data, indent=2)
            )
            
            # Get credit sales
            response = requests.get(f"{BASE_URL}/credit-sales?date={today}", headers=headers, timeout=10)
            if response.status_code == 200:
                sales = response.json()
                found = any(sale.get("id") == credit_sale_id for sale in sales)
                has_mongo_id = any("_id" in sale for sale in sales)
                
                if found and not has_mongo_id:
                    log_test(
                        "Credit Sales - Get",
                        True,
                        f"Retrieved {len(sales)} sales, found created record, no _id field",
                        json.dumps(sales[:2], indent=2) if sales else "[]"
                    )
                else:
                    log_test(
                        "Credit Sales - Get",
                        False,
                        f"Found: {found}, Has _id: {has_mongo_id}",
                        json.dumps(sales[:2], indent=2) if sales else "[]"
                    )
                    all_passed = False
            else:
                log_test("Credit Sales - Get", False, f"Status: {response.status_code}", response.text[:200])
                all_passed = False
        else:
            log_test("Credit Sales - Create", False, f"Status: {response.status_code}", response.text[:200])
            all_passed = False
    except Exception as e:
        log_test("Credit Sales", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3.3: Income/Expenses
    print("\n--- Income/Expenses ---")
    try:
        income_data = {
            "date": today,
            "type": "income",
            "category": "test",
            "amount": 500,
            "description": "income smoke"
        }
        response = requests.post(f"{BASE_URL}/income-expenses", json=income_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            income_id = data.get("id")
            log_test(
                "Income/Expenses - Create",
                True,
                f"Created income record with id: {income_id}",
                json.dumps(data, indent=2)
            )
            
            # Get income/expenses
            response = requests.get(f"{BASE_URL}/income-expenses?date={today}", headers=headers, timeout=10)
            if response.status_code == 200:
                records = response.json()
                found = any(record.get("id") == income_id for record in records)
                has_mongo_id = any("_id" in record for record in records)
                
                if found and not has_mongo_id:
                    log_test(
                        "Income/Expenses - Get",
                        True,
                        f"Retrieved {len(records)} records, found created record, no _id field",
                        json.dumps(records[:2], indent=2) if records else "[]"
                    )
                else:
                    log_test(
                        "Income/Expenses - Get",
                        False,
                        f"Found: {found}, Has _id: {has_mongo_id}",
                        json.dumps(records[:2], indent=2) if records else "[]"
                    )
                    all_passed = False
            else:
                log_test("Income/Expenses - Get", False, f"Status: {response.status_code}", response.text[:200])
                all_passed = False
        else:
            log_test("Income/Expenses - Create", False, f"Status: {response.status_code}", response.text[:200])
            all_passed = False
    except Exception as e:
        log_test("Income/Expenses", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 3.4: Fuel Rates
    print("\n--- Fuel Rates ---")
    try:
        fuel_rate_data = {
            "date": today,
            "fuel_type": "diesel",
            "rate": 96.0
        }
        response = requests.post(f"{BASE_URL}/fuel-rates", json=fuel_rate_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            rate_id = data.get("id")
            log_test(
                "Fuel Rates - Create",
                True,
                f"Created fuel rate with id: {rate_id}",
                json.dumps(data, indent=2)
            )
            
            # Get fuel rates
            response = requests.get(f"{BASE_URL}/fuel-rates?date={today}", headers=headers, timeout=10)
            if response.status_code == 200:
                rates = response.json()
                found = any(rate.get("id") == rate_id for rate in rates)
                has_mongo_id = any("_id" in rate for rate in rates)
                
                if found and not has_mongo_id:
                    log_test(
                        "Fuel Rates - Get",
                        True,
                        f"Retrieved {len(rates)} rates, found created record, no _id field",
                        json.dumps(rates[:2], indent=2) if rates else "[]"
                    )
                else:
                    log_test(
                        "Fuel Rates - Get",
                        False,
                        f"Found: {found}, Has _id: {has_mongo_id}",
                        json.dumps(rates[:2], indent=2) if rates else "[]"
                    )
                    all_passed = False
            else:
                log_test("Fuel Rates - Get", False, f"Status: {response.status_code}", response.text[:200])
                all_passed = False
        else:
            log_test("Fuel Rates - Create", False, f"Status: {response.status_code}", response.text[:200])
            all_passed = False
    except Exception as e:
        log_test("Fuel Rates", False, f"Exception: {str(e)}")
        all_passed = False
    
    return all_passed

def test_sync_endpoints(token):
    """Test 4: Sync Endpoints"""
    print("=" * 60)
    print("TEST 4: Sync Endpoints")
    print("=" * 60)
    
    if not token:
        log_test("Sync Endpoints", False, "No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    all_passed = True
    
    # Test 4.1: Upload sync data
    print("\n--- Sync Upload ---")
    try:
        sync_data = {
            "customers": [],
            "credit_records": [],
            "payments": [],
            "sales": [],
            "income_records": [],
            "expense_records": [],
            "fuel_settings": {},
            "stock_records": [],
            "notes": [],
            "contact_info": {},
            "app_preferences": {}
        }
        response = requests.post(f"{BASE_URL}/sync/upload", json=sync_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "message" in data:
                log_test(
                    "Sync - Upload",
                    True,
                    f"Upload successful: {data.get('message')}",
                    json.dumps(data, indent=2)
                )
            else:
                log_test(
                    "Sync - Upload",
                    False,
                    f"Missing success or message field",
                    json.dumps(data, indent=2)
                )
                all_passed = False
        else:
            log_test("Sync - Upload", False, f"Status: {response.status_code}", response.text[:200])
            all_passed = False
    except Exception as e:
        log_test("Sync - Upload", False, f"Exception: {str(e)}")
        all_passed = False
    
    # Test 4.2: Download sync data
    print("\n--- Sync Download ---")
    try:
        response = requests.get(f"{BASE_URL}/sync/download", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "last_sync" in data:
                log_test(
                    "Sync - Download",
                    True,
                    f"Download successful, has data: {'data' in data}",
                    json.dumps(data, indent=2)[:500]
                )
            else:
                log_test(
                    "Sync - Download",
                    False,
                    f"Missing success or last_sync field",
                    json.dumps(data, indent=2)
                )
                all_passed = False
        else:
            log_test("Sync - Download", False, f"Status: {response.status_code}", response.text[:200])
            all_passed = False
    except Exception as e:
        log_test("Sync - Download", False, f"Exception: {str(e)}")
        all_passed = False
    
    return all_passed

def generate_summary():
    """Generate test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in test_results if result["passed"])
    failed = len(test_results) - passed
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%\n")
    
    if failed > 0:
        print("Failed Tests:")
        for result in test_results:
            if not result["passed"]:
                print(f"  ❌ {result['test']}")
                if result['details']:
                    print(f"     {result['details']}")
        print()
    
    return passed, failed

def main():
    """Main test execution"""
    print("\n" + "=" * 60)
    print("BACKEND API SMOKE TESTS")
    print("Petrol Pump Manager Application")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    # Test 1: Health Check
    health_passed, cors_header = test_health_check()
    
    # Test 2: Auth Flow
    token = test_auth_flow()
    
    # Test 3: Protected CRUD
    if token:
        test_protected_crud(token)
    else:
        log_test("Protected CRUD", False, "Skipped - No auth token")
    
    # Test 4: Sync Endpoints
    if token:
        test_sync_endpoints(token)
    else:
        log_test("Sync Endpoints", False, "Skipped - No auth token")
    
    # Generate summary
    passed, failed = generate_summary()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "cors_header": cors_header,
            "total_tests": len(test_results),
            "passed": passed,
            "failed": failed,
            "results": test_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/backend_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
