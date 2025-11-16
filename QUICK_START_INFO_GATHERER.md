# Information Gatherer - Quick Start Guide

## Overview

The Information Gatherer Agent fetches information from multiple web sources, scores them by authority, and returns structured data.

## Quick Test

```bash
# Validate all success criteria
python test_success_criteria.py

# Run unit tests
pytest tests/test_information_gatherer.py -v

# Test with custom query
python test_info_gatherer.py
```

## Basic Usage

### Option 1: Agent-Based (with Google Search)

```python
import asyncio
from agents.information_gatherer_mvp import gather_information

async def main():
    result = await gather_information(
        query="What is quantum computing?",
        classification={
            "query_type": "factual",
            "research_strategy": "quick-answer"
        }
    )

    print(result)

asyncio.run(main())
```

### Option 2: Enhanced Mode (with specific URLs)

```python
import asyncio
from agents.information_gatherer_mvp import gather_information_enhanced

async def main():
    urls = [
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://www.python.org",
        "https://docs.python.org"
    ]

    result = await gather_information_enhanced(
        query="Python programming language",
        urls=urls
    )

    # Access results
    print(f"Success Rate: {result['success_rate']}%")

    for source in result['top_sources']:
        print(f"\n[{source['authority_score']}/10] {source['title']}")
        print(f"Category: {source['authority_category']}")
        print(f"URL: {source['url']}")

asyncio.run(main())
```

## Key Features

### 1. Authority Scoring
Sources are automatically scored 1-10 based on:
- Domain type (.edu, .gov, major news)
- Content quality (citations, dates, author info)
- Security (HTTPS)

### 2. Parallel Fetching
Fetch multiple URLs simultaneously with:
- Concurrency control (max 5 concurrent)
- Automatic retry on failures
- Error handling

### 3. Structured Output
Returns consistent JSON structure:
```json
{
  "sources": [...],
  "top_sources": [...],
  "metrics": {
    "total": 10,
    "successful": 9,
    "failed": 1,
    "success_rate": 90.0
  }
}
```

## Authority Score Reference

| Score | Category | Examples |
|-------|----------|----------|
| 8.5+ | Academic/Government | .edu, .gov |
| 7.5+ | Medical Authority | CDC, NIH, Mayo Clinic |
| 7.0+ | News/Tech | BBC, Reuters, MDN, Stack Overflow |
| 6.5+ | Encyclopedia | Wikipedia |
| 5.0+ | General | Standard websites |
| <5.0 | User-Generated | Blogs, forums |

## Common Use Cases

### Research Query
```python
result = await gather_information_enhanced(
    query="Climate change impacts",
    urls=[
        "https://climate.nasa.gov",
        "https://www.ipcc.ch",
        "https://www.noaa.gov/climate"
    ]
)
```

### Product Comparison
```python
result = await gather_information_enhanced(
    query="Best laptops for programming 2025",
    urls=[
        "https://www.techradar.com/laptops",
        "https://www.pcmag.com/picks/best-laptops",
        "https://www.cnet.com/tech/computing/best-laptops/"
    ]
)
```

### Technical Documentation
```python
result = await gather_information_enhanced(
    query="React hooks tutorial",
    urls=[
        "https://react.dev/reference/react/hooks",
        "https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks/React_getting_started"
    ]
)
```

## Error Handling

The agent handles all common errors gracefully:
- ✓ 404 Not Found
- ✓ 403 Forbidden
- ✓ Timeouts
- ✓ Connection failures
- ✓ Invalid URLs
- ✓ DNS failures

No crashes - all errors are captured and reported in results.

## Performance Tips

1. **Limit URLs:** For best performance, use 3-5 URLs
2. **Use reliable domains:** Avoid sites that block automation
3. **Adjust concurrency:** Modify `max_concurrent` for your needs
4. **Set appropriate timeouts:** Default is 10s, increase for slow sites

## Standalone Tools

### Calculate Authority Score
```python
from tools.source_authority import calculate_authority_score

score_data = calculate_authority_score(
    url="https://mit.edu/article",
    title="MIT Research Article",
    content="Article content..."
)

print(f"Score: {score_data['score']}/10")
print(f"Category: {score_data['category']}")
print(f"Reasons: {score_data['reasons']}")
```

### Parallel Fetch URLs
```python
from tools.parallel_fetcher import fetch_multiple_with_retry
from tools.web_fetcher import fetch_webpage_content

urls = ["url1", "url2", "url3"]

results = await fetch_multiple_with_retry(
    urls=urls,
    fetch_function=fetch_webpage_content,
    max_concurrent=5,
    max_retries=2
)
```

### Rank Sources
```python
from tools.source_authority import rank_sources_by_authority

sources = [
    {"url": "https://example1.com", "title": "Example 1"},
    {"url": "https://mit.edu/research", "title": "MIT Research"},
]

ranked = rank_sources_by_authority(sources)
# Returns sources sorted by authority score
```

## Success Criteria Met ✅

✅ 90% fetch success rate (target: 80%)
✅ Correct authority identification
✅ Zero crashes with error handling
✅ Fully structured data output

## Need Help?

- Check [INFO_GATHERER_COMPLETION.md](INFO_GATHERER_COMPLETION.md) for detailed documentation
- Run `python test_success_criteria.py` to see examples
- See [tests/test_information_gatherer.py](tests/test_information_gatherer.py) for more examples
