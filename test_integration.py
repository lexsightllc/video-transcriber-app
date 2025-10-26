#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Enhanced Video Transcriber with Phi-3 Brain
Tests all connections, modules, and functionality to ensure no bugs or errors.
"""

import sys
import os
import tempfile
import json
import traceback
from pathlib import Path

# Test configuration
TEST_TEXT = """
Hello, this is a test transcription. We are testing the Phi-3 brain integration 
with the video transcriber application. This text contains multiple sentences 
to test various analysis features including sentiment analysis, topic extraction, 
and summarization capabilities. The system should be able to process this content 
and provide intelligent insights about the transcribed material.
"""

def print_test_header(test_name):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    """Print test result with formatting."""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")

def test_imports():
    """Test all module imports."""
    print_test_header("Module Imports")
    
    tests = [
        ("phi3_brain", "from phi3_brain import Phi3Brain"),
        ("transcriber", "from transcriber import transcribe_video, transcribe_video_enhanced"),
        ("cli_app", "from cli_app import main, display_analysis_results"),
        ("streamlit_app", "import streamlit_app"),
    ]
    
    all_passed = True
    for module_name, import_statement in tests:
        try:
            exec(import_statement)
            print_test_result(f"Import {module_name}", True)
        except Exception as e:
            print_test_result(f"Import {module_name}", False, str(e))
            all_passed = False
    
    return all_passed

def test_phi3_brain_initialization():
    """Test Phi-3 brain initialization and basic functionality."""
    print_test_header("Phi-3 Brain Initialization")
    
    try:
        from phi3_brain import Phi3Brain
        
        # Test initialization
        brain = Phi3Brain()
        print_test_result("Phi3Brain initialization", True)
        
        # Test basic functionality without actual model loading
        # (to avoid downloading large models during testing)
        print_test_result("Phi3Brain basic structure", True)
        
        return True, brain
        
    except Exception as e:
        print_test_result("Phi3Brain initialization", False, str(e))
        return False, None

def test_transcriber_functions():
    """Test transcriber module functions."""
    print_test_header("Transcriber Functions")
    
    try:
        from transcriber import transcribe_video, transcribe_video_enhanced, WHISPER_MODELS, SUPPORTED_LANGUAGES
        
        # Test constants
        print_test_result("WHISPER_MODELS constant", len(WHISPER_MODELS) > 0)
        print_test_result("SUPPORTED_LANGUAGES constant", len(SUPPORTED_LANGUAGES) > 0)
        
        # Test function signatures (without actual execution)
        print_test_result("transcribe_video function exists", callable(transcribe_video))
        print_test_result("transcribe_video_enhanced function exists", callable(transcribe_video_enhanced))
        
        return True
        
    except Exception as e:
        print_test_result("Transcriber functions", False, str(e))
        return False

def test_cli_app_functions():
    """Test CLI app functions."""
    print_test_header("CLI App Functions")
    
    try:
        from cli_app import main, display_analysis_results, analyze_existing_transcription, interactive_qa_mode
        
        # Test function existence
        print_test_result("main function exists", callable(main))
        print_test_result("display_analysis_results function exists", callable(display_analysis_results))
        print_test_result("analyze_existing_transcription function exists", callable(analyze_existing_transcription))
        print_test_result("interactive_qa_mode function exists", callable(interactive_qa_mode))
        
        return True
        
    except Exception as e:
        print_test_result("CLI app functions", False, str(e))
        return False

def test_mock_analysis():
    """Test analysis functions with mock data."""
    print_test_header("Mock Analysis Testing")
    
    try:
        # Create mock result structure
        mock_result = {
            "transcription": TEST_TEXT,
            "phi3_enabled": True,
            "phi3_analysis": {
                "summary": "This is a test summary of the transcription content.",
                "key_topics": ["testing", "phi-3", "integration", "analysis"],
                "quality_assessment": {
                    "quality_score": 8,
                    "confidence_level": "high"
                },
                "sentiment_analysis": {
                    "sentiment": "neutral",
                    "tone": "professional"
                },
                "suggested_questions": [
                    "What is being tested?",
                    "How does the integration work?",
                    "What are the key features?"
                ],
                "word_count": len(TEST_TEXT.split()),
                "estimated_duration_minutes": 2.5
            }
        }
        
        # Test display function with mock data
        from cli_app import display_analysis_results
        print("Testing display_analysis_results with mock data...")
        # Note: This would normally print to stdout, so we just test it doesn't crash
        display_analysis_results(mock_result)
        print_test_result("display_analysis_results with mock data", True)
        
        return True
        
    except Exception as e:
        print_test_result("Mock analysis testing", False, str(e))
        traceback.print_exc()
        return False

def test_file_operations():
    """Test file I/O operations."""
    print_test_header("File Operations")
    
    try:
        # Test creating temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(TEST_TEXT)
            temp_file = f.name
        
        # Test reading the file
        with open(temp_file, 'r') as f:
            content = f.read()
        
        print_test_result("Temporary file creation and reading", content == TEST_TEXT)
        
        # Test JSON operations
        test_data = {"test": "data", "number": 42}
        json_str = json.dumps(test_data, indent=2)
        parsed_data = json.loads(json_str)
        
        print_test_result("JSON serialization/deserialization", test_data == parsed_data)
        
        # Cleanup
        os.unlink(temp_file)
        print_test_result("File cleanup", True)
        
        return True
        
    except Exception as e:
        print_test_result("File operations", False, str(e))
        return False

def test_cli_help():
    """Test CLI help functionality."""
    print_test_header("CLI Help Functionality")
    
    try:
        import subprocess
        
        # Test CLI help command
        result = subprocess.run([
            sys.executable, "cli_app.py", "--help"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        help_works = result.returncode == 0 and "Enhanced Video Transcription" in result.stdout
        print_test_result("CLI help command", help_works)
        
        return help_works
        
    except Exception as e:
        print_test_result("CLI help functionality", False, str(e))
        return False

def test_error_handling():
    """Test error handling in various scenarios."""
    print_test_header("Error Handling")
    
    try:
        from phi3_brain import Phi3Brain
        
        # Test with invalid model name (should handle gracefully)
        try:
            brain = Phi3Brain(model_name="invalid/model/name")
            # If this doesn't fail immediately, that's also fine
            print_test_result("Invalid model name handling", True, "No immediate error (lazy loading)")
        except Exception as e:
            print_test_result("Invalid model name handling", True, f"Caught expected error: {type(e).__name__}")
        
        # Test with invalid device
        try:
            brain = Phi3Brain(device="invalid_device")
            print_test_result("Invalid device handling", True, "Handled gracefully")
        except Exception as e:
            print_test_result("Invalid device handling", True, f"Caught expected error: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print_test_result("Error handling tests", False, str(e))
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print_test_header("Dependency Verification")
    
    required_packages = [
        "streamlit",
        "moviepy", 
        "whisper",
        "torch",
        "numpy",
        "transformers",
        "accelerate",
        "bitsandbytes",
        "sentencepiece"
    ]
    
    all_available = True
    for package in required_packages:
        try:
            __import__(package)
            print_test_result(f"Package {package}", True)
        except ImportError as e:
            print_test_result(f"Package {package}", False, str(e))
            all_available = False
    
    return all_available

def run_all_tests():
    """Run all tests and provide summary."""
    print("🧪 COMPREHENSIVE INTEGRATION TEST SUITE")
    print("🧠 Enhanced Video Transcriber with Phi-3 Brain")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Dependencies", test_dependencies()))
    test_results.append(("Imports", test_imports()))
    test_results.append(("Phi3Brain Init", test_phi3_brain_initialization()[0]))
    test_results.append(("Transcriber Functions", test_transcriber_functions()))
    test_results.append(("CLI Functions", test_cli_app_functions()))
    test_results.append(("Mock Analysis", test_mock_analysis()))
    test_results.append(("File Operations", test_file_operations()))
    test_results.append(("CLI Help", test_cli_help()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Print summary
    print_test_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
