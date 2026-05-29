"""
Test script to verify summary improvements.

Tests:
1. Text processing for mathematical equations
2. PDF generation without transcription
"""

import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from controller import process_text_for_pdf


def test_math_equation_processing():
    """Test mathematical equation processing."""
    print("=" * 60)
    print("Testing Mathematical Equation Processing")
    print("=" * 60)

    test_cases = [
        # LaTeX equations
        ("$E = mc^2$", "E = mc<super>2</super>"),
        ("$\\alpha = \\frac{1}{2}$", "α = (1)/(2)"),
        ("$x^2 + y^2 = z^2$", "x<super>2</super> + y<super>2</super> = z<super>2</super>"),
        ("$\\sum_{i=1}^{n} x_i$", "Σ<sub>i=1</sub><super>n</super> x<sub>i</sub>"),
        ("$\\theta \\leq \\pi$", "θ ≤ π"),
        ("$\\sqrt{2}$", "√{2}"),
        ("$\\infty$", "∞"),
        ("H$_2$O", "H<sub>2</sub>O"),
        ("$\\mu \\pm \\sigma$", "μ ± σ"),
    ]

    passed = 0
    failed = 0

    for input_text, expected in test_cases:
        result = process_text_for_pdf(input_text)
        # Remove <br/> tags added by the function for comparison
        result = result.replace('<br/>', '')

        if result == expected:
            print(f"[OK] PASS: {input_text} -> {result}")
            passed += 1
        else:
            print(f"[FAIL] FAIL: {input_text}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


def test_complex_text():
    """Test complex text with multiple equations."""
    print("\n" + "=" * 60)
    print("Testing Complex Text Processing")
    print("=" * 60)

    complex_text = """
    The equation $E = mc^2$ demonstrates mass-energy equivalence.
    For statistical analysis, we use $\\mu \\pm \\sigma$ where $\\mu$ is the mean.
    The correlation coefficient $\\alpha = 0.87$ shows strong relationship.
    The sum $\\sum_{i=1}^{n} x_i$ converges to $\\infty$ when conditions are met.
    """

    result = process_text_for_pdf(complex_text)
    print("\nInput:")
    print(complex_text)
    print("\nProcessed Output:")
    print(result.replace('<br/>', '\n'))

    # Check for common issues
    issues = []
    if '\\' in result:
        issues.append("Contains backslashes")
    if '$' in result:
        issues.append("Contains dollar signs")

    if not issues:
        print("\n✓ Text processed successfully - no LaTeX artifacts found")
        return True
    else:
        print("\n✗ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False


def test_llm_instructions():
    """Check LLM instruction file for updated requirements."""
    print("\n" + "=" * 60)
    print("Checking LLM Instructions")
    print("=" * 60)

    try:
        with open("llm_instructions/slide_analysis.yaml", "r") as f:
            content = f.read()

        checks = {
            "10-15 sentences": "10-15" in content and "sentences" in content,
            "Comprehensive summary": "comprehensive" in content.lower(),
            "Executive summary": "executive summary" in content.lower() or "EXECUTIVE SUMMARY" in content,
            "250-400 words": "250-400" in content or "400-500" in content,
            "Mathematical equations": "mathematical equations" in content.lower() or "equation" in content.lower(),
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False

        if all_passed:
            print("\n✓ All LLM instruction checks passed")
        else:
            print("\n⚠ Some checks failed - review llm_instructions/slide_analysis.yaml")

        return all_passed

    except FileNotFoundError:
        print("✗ Could not find llm_instructions/slide_analysis.yaml")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PPT Summarizer - Summary Improvements Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Mathematical equation processing
    results.append(("Math Equation Processing", test_math_equation_processing()))

    # Test 2: Complex text processing
    results.append(("Complex Text Processing", test_complex_text()))

    # Test 3: LLM instructions
    results.append(("LLM Instructions", test_llm_instructions()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All tests passed!")
        print("\nNext steps:")
        print("1. Start the API: python api.py")
        print("2. Test with a real presentation")
        print("3. Check the generated PDF summary")
    else:
        print("\n⚠ Some tests failed - review the output above")

    print("=" * 60)


if __name__ == "__main__":
    main()
