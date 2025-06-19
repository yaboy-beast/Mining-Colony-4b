"""
A script to discover and run all unit tests for the Colony 4B game.

This module provides a convenient way to execute the entire test suite.
It uses Python's ``unittest`` framework to automatically find all test
modules within this directory, run them, and report the results. This
is the primary entry point for verifying the correctness of the game's
logic.
"""
import unittest
import os
import sys

# Add the parent directory to the system path to allow imports of game modules.
# This ensures that when the script is run directly, it can find modules like
# 'player', 'room', etc., which are in the project's root directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_tests():
    """
    Discovers and runs all unit tests in the current directory.

    This function sets up the unittest TestLoader, discovers all files
    matching the pattern 'test_*.py', and runs them using a TextTestRunner.
    It prints a summary of the results upon completion.
    """
    # Create a TestLoader instance to find test cases.
    loader = unittest.TestLoader()
    
    # Define the directory where the tests are located.
    start_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all tests within the specified directory. The pattern
    # 'test_*.py' is the default for the discover method.
    suite = loader.discover(start_dir)
    
    # Create a TextTestRunner to execute the tests and display results.
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the discovered test suite.
    print("="*70)
    print("Running all Colony 4B unit tests...")
    print("="*70)
    result = runner.run(suite)
    print("="*70)
    
    if result.wasSuccessful():
        print("All tests passed successfully!")
    else:
        print("Some tests failed.")
        # Exit with a non-zero status code to indicate failure,
        # which is useful for CI/CD pipelines.
        sys.exit(1)

if __name__ == '__main__':
    run_tests() 
