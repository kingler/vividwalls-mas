#!/usr/bin/env python3
"""
Test runner for VividWalls Color Palette Agent MCP Server.

This script facilitates TDD workflow by running tests and reporting results.
Following TDD principles, tests should be written first and should fail
before implementation.
"""

import sys
import subprocess
import argparse
from pathlib import Path

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str, color: str = Colors.BLUE):
    """Print a colored header message."""
    print(f"\n{color}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{color}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{color}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def run_tests(test_type: str = "all", verbose: bool = True, coverage: bool = True):
    """
    Run tests based on the specified type.
    
    Args:
        test_type: Type of tests to run ('all', 'unit', 'integration', 'tdd')
        verbose: Whether to show verbose output
        coverage: Whether to generate coverage report
    """
    # Base pytest command
    cmd = ["pytest"]
    
    # Add test type specific flags
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
        print_header("Running Unit Tests", Colors.BLUE)
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
        print_header("Running Integration Tests", Colors.BLUE)
    elif test_type == "tdd":
        # For TDD, we expect tests to fail initially
        cmd.extend(["--tb=short", "-x"])  # Stop on first failure
        print_header("Running TDD Tests (Expected to Fail)", Colors.YELLOW)
    else:
        print_header("Running All Tests", Colors.BLUE)
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Skip coverage for TDD mode (since code isn't implemented yet)
    if coverage and test_type != "tdd":
        cmd.extend(["--cov=.", "--cov-report=term-missing"])
    
    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print_header("All Tests Passed! ✅", Colors.GREEN)
            if test_type == "tdd":
                print(f"{Colors.YELLOW}Warning: In TDD, tests should fail before implementation!{Colors.ENDC}")
                print(f"{Colors.YELLOW}If tests are passing, the implementation might already exist.{Colors.ENDC}")
        else:
            if test_type == "tdd":
                print_header("Tests Failed (Expected in TDD) ❌", Colors.YELLOW)
                print(f"{Colors.BLUE}Now implement the code to make these tests pass!{Colors.ENDC}")
            else:
                print_header("Tests Failed ❌", Colors.RED)
                
        return result.returncode
        
    except FileNotFoundError:
        print(f"{Colors.RED}Error: pytest not found. Please install it with: pip install pytest pytest-cov{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"{Colors.RED}Error running tests: {e}{Colors.ENDC}")
        return 1


def check_test_files():
    """Check if all test files exist."""
    test_files = [
        "tests/unit/test_logger.py",
        "tests/unit/test_server.py",
        "tests/unit/test_image_processing.py",
        "tests/unit/test_recommendation.py"
    ]
    
    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"{Colors.YELLOW}Warning: The following test files are missing:{Colors.ENDC}")
        for file in missing_files:
            print(f"  - {file}")
        print()


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test runner for VividWalls Color Palette Agent MCP Server"
    )
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "tdd"],
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage report generation"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    args = parser.parse_args()
    
    # Print TDD workflow reminder
    if args.type == "tdd":
        print(f"{Colors.BOLD}TDD Workflow Reminder:{Colors.ENDC}")
        print("1. Write tests first (already done)")
        print("2. Run tests and see them fail (current step)")
        print("3. Implement minimal code to pass tests")
        print("4. Run tests again to verify they pass")
        print("5. Refactor if needed")
        print("6. Repeat for next feature\n")
    
    # Check for missing test files
    check_test_files()
    
    # Run the tests
    exit_code = run_tests(
        test_type=args.type,
        verbose=not args.quiet,
        coverage=not args.no_coverage
    )
    
    # Additional TDD guidance
    if args.type == "tdd" and exit_code != 0:
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print("1. Look at the failing test output above")
        print("2. Implement the missing functionality in the corresponding module")
        print("3. Run 'python run_tests.py unit' to test your implementation")
        print("4. Once tests pass, run 'python run_tests.py all' for full validation")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 