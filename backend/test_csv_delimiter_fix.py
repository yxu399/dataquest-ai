#!/usr/bin/env python3
"""
Test script to verify the improved CSV delimiter detection functionality.
This script tests various CSV formats to ensure the delimiter detection works properly.
"""

import os
import sys
from io import BytesIO
from fastapi import UploadFile

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.api.v1.files import validate_csv_file


def create_mock_upload_file(content: str, filename: str = "test.csv") -> UploadFile:
    """Create a mock UploadFile object for testing"""
    file_like = BytesIO(content.encode("utf-8"))
    return UploadFile(file=file_like, filename=filename)


def test_csv_formats():
    """Test various CSV formats"""

    print("🧪 Testing CSV Delimiter Detection Fix")
    print("=" * 50)

    test_cases = [
        {
            "name": "Standard Comma-Separated CSV",
            "content": """employee_id,name,department,salary
E001,John Smith,Engineering,75000
E002,Sarah Johnson,Marketing,68000
E003,Mike Davis,Sales,82000""",
            "expected_delimiter": ",",
        },
        {
            "name": "Semicolon-Separated CSV",
            "content": """employee_id;name;department;salary
E001;John Smith;Engineering;75000
E002;Sarah Johnson;Marketing;68000
E003;Mike Davis;Sales;82000""",
            "expected_delimiter": ";",
        },
        {
            "name": "Tab-Separated CSV",
            "content": """employee_id\tname\tdepartment\tsalary
E001\tJohn Smith\tEngineering\t75000
E002\tSarah Johnson\tMarketing\t68000
E003\tMike Davis\tSales\t82000""",
            "expected_delimiter": "\t",
        },
        {
            "name": "Pipe-Separated CSV",
            "content": """employee_id|name|department|salary
E001|John Smith|Engineering|75000
E002|Sarah Johnson|Marketing|68000
E003|Mike Davis|Sales|82000""",
            "expected_delimiter": "|",
        },
        {
            "name": "CSV with Quoted Fields",
            "content": """employee_id,name,department,salary
E001,"John Smith, Jr.",Engineering,75000
E002,"Sarah Johnson",Marketing,68000
E003,"Mike Davis",Sales,82000""",
            "expected_delimiter": ",",
        },
        {
            "name": "CSV with Mixed Data Types",
            "content": """id,name,active,score,date
1,Alice,true,95.5,2023-01-01
2,Bob,false,87.2,2023-01-02
3,Charlie,true,91.8,2023-01-03""",
            "expected_delimiter": ",",
        },
    ]

    failed_tests = []
    passed_tests = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)

        try:
            # Create mock upload file
            upload_file = create_mock_upload_file(test_case["content"])

            # Test validation
            is_valid, message, file_info = validate_csv_file(upload_file)

            if is_valid:
                detected_delimiter = file_info.get("delimiter")
                expected_delimiter = test_case["expected_delimiter"]

                print("✅ Status: Valid CSV")
                print(f"📊 Columns: {len(file_info.get('columns', []))}")
                print(f"📝 Sample rows: {file_info.get('rows_sample', 0)}")
                print(f"🔍 Detected delimiter: '{detected_delimiter}'")
                print(f"🎯 Expected delimiter: '{expected_delimiter}'")
                print(f"📏 File size: {file_info.get('file_size_bytes', 0)} bytes")
                print(f"🔤 Encoding: {file_info.get('encoding', 'unknown')}")

                if detected_delimiter == expected_delimiter:
                    print("✅ SUCCESS: Delimiter detection correct!")
                    passed_tests.append(test_case["name"])
                else:
                    print("❌ FAILED: Delimiter mismatch!")
                    failed_tests.append(test_case["name"])
            else:
                print(f"❌ FAILED: {message}")
                failed_tests.append(test_case["name"])

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed_tests.append(test_case["name"])

    # Test invalid cases
    print(f"\n{len(test_cases) + 1}. Invalid CSV Cases")
    print("-" * 40)

    invalid_cases = [
        {"name": "Empty file", "content": "", "should_fail": True},
        {
            "name": "No delimiter detected",
            "content": """singlecolumnheader
value1
value2
value3""",
            "should_fail": True,
        },
        {
            "name": "Inconsistent delimiters",
            "content": """col1,col2,col3
val1;val2;val3
val4,val5,val6""",
            "should_fail": False,  # Our improved logic should handle this by picking the most consistent one
        },
    ]

    for case in invalid_cases:
        try:
            upload_file = create_mock_upload_file(case["content"])
            is_valid, message, file_info = validate_csv_file(upload_file)

            if case["should_fail"] and not is_valid:
                print(f"✅ '{case['name']}': Correctly rejected - {message}")
                passed_tests.append(f"Invalid case: {case['name']}")
            elif not case["should_fail"] and is_valid:
                print(f"✅ '{case['name']}': Correctly accepted")
                passed_tests.append(f"Invalid case: {case['name']}")
            else:
                print(
                    f"❌ '{case['name']}': Unexpected result - Valid: {is_valid}, Message: {message}"
                )
                failed_tests.append(f"Invalid case: {case['name']}")
        except Exception as e:
            print(f"❌ '{case['name']}': Error - {str(e)}")
            failed_tests.append(f"Invalid case: {case['name']}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {len(passed_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")

    if passed_tests:
        print("\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test}")

    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   • {test}")
        return False
    else:
        print("\n🎉 ALL TESTS PASSED! CSV delimiter detection is working correctly.")
        return True


if __name__ == "__main__":
    success = test_csv_formats()
    sys.exit(0 if success else 1)
