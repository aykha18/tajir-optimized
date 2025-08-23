#!/usr/bin/env python3
"""
Tajir POS - Test Runner
Pre-PostgreSQL Migration Testing

This script provides various ways to run tests and generate reports
for the Tajir POS application.
"""

import os
import sys
import argparse
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    print("🧪 Running Unit Tests...")
    
    cmd = [sys.executable, "-m", "pytest", "tests/test_suite.py"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_integration_tests(verbose=False):
    """Run integration tests"""
    print("🔗 Running Integration Tests...")
    
    cmd = [sys.executable, "tests/test_suite.py"]
    if verbose:
        cmd.append("-v")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_api_tests(verbose=False):
    """Run API endpoint tests"""
    print("🌐 Running API Tests...")
    
    # Start the Flask app in background
    app_process = subprocess.Popen([
        sys.executable, "app.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for app to start
        time.sleep(3)
        
        # Run API tests
        cmd = [sys.executable, "tests/api_tests.py"]
        if verbose:
            cmd.append("-v")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    
    finally:
        # Clean up
        app_process.terminate()
        app_process.wait()

def run_performance_tests():
    """Run performance tests"""
    print("⚡ Running Performance Tests...")
    
    cmd = [sys.executable, "tests/performance_tests.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def run_security_tests():
    """Run security tests"""
    print("🔒 Running Security Tests...")
    
    cmd = [sys.executable, "tests/security_tests.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def generate_test_report(results):
    """Generate a comprehensive test report"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = f"test_report_{timestamp}.json"
    
    report = {
        "timestamp": timestamp,
        "application": "Tajir POS",
        "version": "Pre-PostgreSQL Migration",
        "test_results": results,
        "summary": {
            "total_tests": sum(len(r.get("tests", [])) for r in results.values()),
            "passed": sum(len([t for t in r.get("tests", []) if t.get("status") == "passed"]) for r in results.values()),
            "failed": sum(len([t for t in r.get("tests", []) if t.get("status") == "failed"]) for r in results.values()),
            "errors": sum(len([t for t in r.get("tests", []) if t.get("status") == "error"]) for r in results.values())
        }
    }
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Test Report Generated: {report_file}")
    
    # Print summary
    summary = report["summary"]
    total = summary["total_tests"]
    passed = summary["passed"]
    failed = summary["failed"]
    errors = summary["errors"]
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"Errors: {errors} ({errors/total*100:.1f}%)")
    print(f"{'='*60}")
    
    return report_file

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites...")
    
    # Check if required files exist
    required_files = [
        "app.py",
        "database_schema.sql",
        "requirements.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Check if required packages are installed
    try:
        import flask
        import sqlite3
        import bcrypt
        print("✅ All required packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        return False
    
    print("✅ Prerequisites check passed")
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Tajir POS Test Runner")
    parser.add_argument("--type", choices=["unit", "integration", "api", "performance", "security", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--check-prereq", action="store_true", help="Check prerequisites only")
    
    args = parser.parse_args()
    
    print("🚀 Tajir POS Test Runner")
    print("=" * 60)
    
    # Check prerequisites
    if args.check_prereq:
        return 0 if check_prerequisites() else 1
    
    if not check_prerequisites():
        return 1
    
    results = {}
    
    try:
        if args.type in ["unit", "all"]:
            results["unit"] = {
                "status": "passed" if run_unit_tests(args.verbose, args.coverage) else "failed",
                "tests": []
            }
        
        if args.type in ["integration", "all"]:
            results["integration"] = {
                "status": "passed" if run_integration_tests(args.verbose) else "failed",
                "tests": []
            }
        
        if args.type in ["api", "all"]:
            results["api"] = {
                "status": "passed" if run_api_tests(args.verbose) else "failed",
                "tests": []
            }
        
        if args.type in ["performance", "all"]:
            results["performance"] = {
                "status": "passed" if run_performance_tests() else "failed",
                "tests": []
            }
        
        if args.type in ["security", "all"]:
            results["security"] = {
                "status": "passed" if run_security_tests() else "failed",
                "tests": []
            }
        
        # Generate report if requested
        if args.report:
            generate_test_report(results)
        
        # Determine overall success
        all_passed = all(r["status"] == "passed" for r in results.values())
        
        if all_passed:
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
