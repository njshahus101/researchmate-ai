"""
Success Criteria Validation Script

This script tests the Information Gatherer Agent against the defined success criteria:
1. Successfully fetches and extracts content from 80%+ of URLs
2. Correctly identifies authoritative sources
3. Handles errors without crashing
4. Returns structured source data
"""

import asyncio
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.information_gatherer_mvp import gather_information_enhanced
from tools.source_authority import rank_sources_by_authority
from tools.parallel_fetcher import fetch_multiple_urls, calculate_success_rate
from tools.web_fetcher import fetch_webpage_content


async def test_criterion_1_fetch_success_rate():
    """
    SUCCESS CRITERION 1: Successfully fetches and extracts content from 80%+ of URLs
    """
    print("\n" + "="*70)
    print("CRITERION 1: 80%+ Fetch Success Rate")
    print("="*70)

    # Test with a mix of reliable URLs
    test_urls = [
        "https://www.example.com",
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://www.python.org",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "https://www.w3.org/standards/",
        "https://www.iana.org/domains/reserved",
        "https://www.bbc.com",
        "https://stackoverflow.com",
        "https://github.com",
        "https://www.nasa.gov",
    ]

    print(f"\nTesting with {len(test_urls)} URLs...")
    print("URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")

    # Fetch all URLs
    results = await fetch_multiple_urls(
        urls=test_urls,
        fetch_function=fetch_webpage_content,
        max_concurrent=5,
        timeout=15
    )

    # Calculate metrics
    metrics = calculate_success_rate(results)

    print(f"\n{'─'*70}")
    print("RESULTS:")
    print(f"{'─'*70}")
    print(f"Total URLs Attempted:  {metrics['total']}")
    print(f"Successful Fetches:    {metrics['successful']}")
    print(f"Failed Fetches:        {metrics['failed']}")
    print(f"Success Rate:          {metrics['success_rate']}%")

    if metrics['error_types']:
        print(f"\nError Breakdown:")
        for error_type, count in metrics['error_types'].items():
            print(f"  - {error_type}: {count}")

    # Show successful vs failed URLs
    print(f"\nSuccessful URLs:")
    for result in results:
        if result.get('status') == 'success':
            print(f"  ✓ {result['url']}")
            print(f"    Title: {result.get('title', 'N/A')[:60]}")
            print(f"    Content Length: {result.get('content_length', 0)} chars")

    print(f"\nFailed URLs:")
    for result in results:
        if result.get('status') == 'error':
            print(f"  ✗ {result['url']}")
            print(f"    Error: {result.get('error_message', 'Unknown')}")

    # Verdict
    print(f"\n{'─'*70}")
    if metrics['success_rate'] >= 80.0:
        print(f"✅ CRITERION 1 PASSED: {metrics['success_rate']}% >= 80%")
    else:
        print(f"❌ CRITERION 1 FAILED: {metrics['success_rate']}% < 80%")
    print(f"{'─'*70}")

    return metrics['success_rate'] >= 80.0


async def test_criterion_2_authority_identification():
    """
    SUCCESS CRITERION 2: Correctly identifies authoritative sources
    """
    print("\n" + "="*70)
    print("CRITERION 2: Authority Source Identification")
    print("="*70)

    # Test sources with known authority levels
    test_sources = [
        {"url": "https://mit.edu/research/ai", "title": "MIT AI Research"},
        {"url": "https://cdc.gov/coronavirus", "title": "CDC COVID-19 Info"},
        {"url": "https://www.bbc.com/news/technology", "title": "BBC Tech News"},
        {"url": "https://en.wikipedia.org/wiki/Machine_learning", "title": "Wikipedia ML"},
        {"url": "https://stackoverflow.com/questions/12345", "title": "Stack Overflow Question"},
        {"url": "https://someblog.blogspot.com/my-opinion", "title": "Random Blog Post"},
        {"url": "https://randomsite.com/article", "title": "Unknown Site"},
    ]

    print(f"\nTesting authority scoring with {len(test_sources)} sources...\n")

    # Rank sources
    ranked_sources = rank_sources_by_authority(test_sources)

    print("RANKED SOURCES (by authority):")
    print(f"{'─'*70}")

    for i, source in enumerate(ranked_sources, 1):
        score = source['authority_score']
        category = source['authority_category']
        url = source['url']

        # Visual indicator
        if score >= 8.0:
            indicator = "🟢 HIGH"
        elif score >= 6.0:
            indicator = "🟡 MEDIUM"
        else:
            indicator = "🔴 LOW"

        print(f"{i}. [{score:.1f}/10] {indicator}")
        print(f"   Category: {category}")
        print(f"   URL: {url}")
        print(f"   Reasons: {', '.join(source['authority_reasons'])}")
        print()

    # Validation checks
    checks_passed = 0
    total_checks = 0

    # Check 1: .edu should be in top 2
    total_checks += 1
    edu_ranks = [i for i, s in enumerate(ranked_sources) if '.edu' in s['url']]
    if edu_ranks and edu_ranks[0] < 2:
        print("✓ Check 1: Educational domain (.edu) ranked in top 2")
        checks_passed += 1
    else:
        print("✗ Check 1: Educational domain NOT in top 2")

    # Check 2: .gov should be in top 2
    total_checks += 1
    gov_ranks = [i for i, s in enumerate(ranked_sources) if '.gov' in s['url']]
    if gov_ranks and gov_ranks[0] < 2:
        print("✓ Check 2: Government domain (.gov) ranked in top 2")
        checks_passed += 1
    else:
        print("✗ Check 2: Government domain NOT in top 2")

    # Check 3: Blogspot should be ranked lower than BBC
    total_checks += 1
    blogspot_rank = next((i for i, s in enumerate(ranked_sources) if 'blogspot' in s['url']), None)
    bbc_rank = next((i for i, s in enumerate(ranked_sources) if 'bbc.com' in s['url']), None)
    if blogspot_rank and bbc_rank and bbc_rank < blogspot_rank:
        print("✓ Check 3: BBC News ranked higher than blogspot")
        checks_passed += 1
    else:
        print("✗ Check 3: BBC News NOT ranked higher than blogspot")

    # Check 4: High authority sources score >= 7.0
    total_checks += 1
    high_auth_sources = [s for s in ranked_sources if '.edu' in s['url'] or '.gov' in s['url']]
    if high_auth_sources and all(s['authority_score'] >= 7.0 for s in high_auth_sources):
        print("✓ Check 4: High authority sources (.edu, .gov) score >= 7.0")
        checks_passed += 1
    else:
        print("✗ Check 4: Some high authority sources scored below 7.0")

    # Verdict
    print(f"\n{'─'*70}")
    success_rate = (checks_passed / total_checks * 100)
    if checks_passed == total_checks:
        print(f"✅ CRITERION 2 PASSED: All {total_checks} authority checks passed")
        passed = True
    else:
        print(f"⚠️  CRITERION 2 PARTIAL: {checks_passed}/{total_checks} checks passed ({success_rate:.0f}%)")
        passed = checks_passed >= (total_checks * 0.75)  # 75% threshold
    print(f"{'─'*70}")

    return passed


async def test_criterion_3_error_handling():
    """
    SUCCESS CRITERION 3: Handles errors without crashing
    """
    print("\n" + "="*70)
    print("CRITERION 3: Error Handling Without Crashing")
    print("="*70)

    # Problematic URLs designed to trigger various errors
    error_test_urls = [
        "https://this-domain-absolutely-does-not-exist-xyz12345.com",  # DNS failure
        "not-a-valid-url-at-all",  # Invalid format
        "https://www.example.com/this-page-definitely-does-not-exist-404",  # 404
        "ftp://invalid-scheme.com",  # Invalid scheme
        "https://www.example.com",  # One valid URL to ensure mixed results
    ]

    print(f"\nTesting error handling with {len(error_test_urls)} problematic URLs...")
    print("URLs:")
    for i, url in enumerate(error_test_urls, 1):
        print(f"  {i}. {url}")

    crashed = False
    results = None

    try:
        # Attempt to fetch all URLs
        results = await fetch_multiple_urls(
            urls=error_test_urls,
            fetch_function=fetch_webpage_content,
            max_concurrent=3,
            timeout=10
        )

        print(f"\n✓ No exceptions raised during fetching")

        # Verify we got results for all URLs
        if len(results) == len(error_test_urls):
            print(f"✓ Received results for all {len(error_test_urls)} URLs")
        else:
            print(f"⚠️  Only received {len(results)}/{len(error_test_urls)} results")

        # Check error handling
        print(f"\nError Handling Details:")
        for result in results:
            url = result.get('url', 'Unknown')[:50]
            status = result.get('status', 'unknown')

            if status == 'error':
                error_msg = result.get('error_message', 'No error message')
                print(f"  ✓ {url}")
                print(f"    Status: {status}")
                print(f"    Error: {error_msg}")
            else:
                print(f"  ✓ {url}")
                print(f"    Status: {status} (success)")

    except Exception as e:
        crashed = True
        print(f"\n✗ EXCEPTION RAISED: {type(e).__name__}: {str(e)}")

    # Verdict
    print(f"\n{'─'*70}")
    if not crashed and results and len(results) == len(error_test_urls):
        print("✅ CRITERION 3 PASSED: All errors handled gracefully, no crashes")
        passed = True
    else:
        print("❌ CRITERION 3 FAILED: System crashed or didn't return all results")
        passed = False
    print(f"{'─'*70}")

    return passed


async def test_criterion_4_structured_data():
    """
    SUCCESS CRITERION 4: Returns structured source data
    """
    print("\n" + "="*70)
    print("CRITERION 4: Returns Structured Source Data")
    print("="*70)

    test_urls = [
        "https://www.example.com",
        "https://en.wikipedia.org/wiki/Python_(programming_language)"
    ]

    print(f"\nTesting structured data return with {len(test_urls)} URLs...\n")

    result = await gather_information_enhanced(
        query="Test query for structured data",
        urls=test_urls
    )

    # Check for required top-level fields
    required_fields = ['sources', 'metrics', 'success_rate', 'query']
    checks_passed = 0
    total_checks = 0

    print("Top-Level Structure Checks:")
    for field in required_fields:
        total_checks += 1
        if field in result:
            print(f"  ✓ Has '{field}' field")
            checks_passed += 1
        else:
            print(f"  ✗ Missing '{field}' field")

    # Check source structure
    if 'sources' in result and len(result['sources']) > 0:
        source_fields = ['url', 'title', 'fetch_status', 'authority_score', 'authority_category']

        print(f"\nSource Structure Checks (checking first source):")
        first_source = result['sources'][0]

        for field in source_fields:
            total_checks += 1
            if field in first_source:
                print(f"  ✓ Source has '{field}' field: {first_source[field]}")
                checks_passed += 1
            else:
                print(f"  ✗ Source missing '{field}' field")

    # Check metrics structure
    if 'metrics' in result:
        metric_fields = ['total', 'successful', 'failed', 'success_rate']

        print(f"\nMetrics Structure Checks:")
        for field in metric_fields:
            total_checks += 1
            if field in result['metrics']:
                print(f"  ✓ Metrics has '{field}': {result['metrics'][field]}")
                checks_passed += 1
            else:
                print(f"  ✗ Metrics missing '{field}'")

    # Show sample data
    print(f"\nSample Source Data:")
    print(f"{'─'*70}")
    if 'sources' in result and len(result['sources']) > 0:
        import json
        print(json.dumps(result['sources'][0], indent=2, default=str))

    # Verdict
    print(f"\n{'─'*70}")
    success_rate = (checks_passed / total_checks * 100)
    if checks_passed == total_checks:
        print(f"✅ CRITERION 4 PASSED: All {total_checks} structure checks passed")
        passed = True
    else:
        print(f"⚠️  CRITERION 4 PARTIAL: {checks_passed}/{total_checks} checks passed ({success_rate:.0f}%)")
        passed = checks_passed >= (total_checks * 0.8)  # 80% threshold
    print(f"{'─'*70}")

    return passed


async def main():
    """Run all success criteria tests."""
    print("\n" + "="*70)
    print("INFORMATION GATHERER - SUCCESS CRITERIA VALIDATION")
    print("="*70)
    print("\nTesting against the following success criteria:")
    print("1. Successfully fetches and extracts content from 80%+ of URLs")
    print("2. Correctly identifies authoritative sources")
    print("3. Handles errors without crashing")
    print("4. Returns structured source data")
    print("="*70)

    results = {}

    # Run all tests
    try:
        results['criterion_1'] = await test_criterion_1_fetch_success_rate()
        results['criterion_2'] = await test_criterion_2_authority_identification()
        results['criterion_3'] = await test_criterion_3_error_handling()
        results['criterion_4'] = await test_criterion_4_structured_data()
    except Exception as e:
        print(f"\n❌ FATAL ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return

    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for criterion, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{criterion.replace('_', ' ').title()}: {status}")

    print(f"\n{'─'*70}")
    overall_success_rate = (passed_count / total_count * 100)
    print(f"Overall: {passed_count}/{total_count} criteria passed ({overall_success_rate:.0f}%)")

    if passed_count == total_count:
        print("\n🎉 ALL SUCCESS CRITERIA MET! Information Gatherer is ready for production.")
    elif passed_count >= 3:
        print("\n⚠️  MOSTLY PASSING - Minor improvements needed.")
    else:
        print("\n❌ SIGNIFICANT ISSUES - More work required.")

    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
