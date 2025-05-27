#!/usr/bin/env python3
"""Test runner script for Composer Kit MCP."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run tests for Composer Kit MCP")
    parser.add_argument(
        "--unit", action="store_true", help="Run only unit tests (fast)"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests (slow, requires network)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all tests including integration tests"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--file", type=str, help="Run specific test file")
    parser.add_argument("--function", type=str, help="Run specific test function")

    args = parser.parse_args()

    # Change to project directory
    project_dir = Path(__file__).parent
    print(f"📁 Working directory: {project_dir}")

    # Base pytest command
    base_cmd = [sys.executable, "-m", "pytest"]

    if args.verbose:
        base_cmd.extend(["-v", "-s"])

    # Determine what tests to run
    if args.unit:
        print("🧪 Running unit tests only...")
        cmd = base_cmd + ["-m", "not integration"]

    elif args.integration:
        print("🌐 Running integration tests only...")
        cmd = base_cmd + ["-m", "integration", "--integration"]

    elif args.all:
        print("🚀 Running all tests (unit + integration)...")
        cmd = base_cmd + ["--integration"]

    elif args.file:
        print(f"📄 Running tests from file: {args.file}")
        cmd = base_cmd + [f"tests/{args.file}"]
        if args.function:
            cmd.append(f"-k {args.function}")

    elif args.function:
        print(f"🎯 Running specific test function: {args.function}")
        cmd = base_cmd + ["-k", args.function]

    else:
        print("🧪 Running unit tests only (default)...")
        cmd = base_cmd + ["-m", "not integration"]

    # Add coverage if requested
    if args.coverage:
        cmd.extend(
            [
                "--cov=src/composer_kit_mcp",
                "--cov-report=html",
                "--cov-report=term-missing",
            ]
        )

    # Run the tests
    success = run_command(cmd, "Running tests")

    if args.coverage and success:
        print("\n📊 Coverage report generated in htmlcov/index.html")

    # Summary
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
