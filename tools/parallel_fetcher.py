"""
Parallel Web Fetching Module

Provides async parallel fetching capabilities for multiple URLs.
"""

import asyncio
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor
import functools


async def fetch_url_async(url: str, fetch_function: Callable, timeout: int = 10) -> Dict[str, Any]:
    """
    Asynchronously fetch a single URL using a synchronous fetch function.

    Args:
        url: URL to fetch
        fetch_function: Synchronous function to fetch content (e.g., fetch_webpage_content)
        timeout: Timeout in seconds

    Returns:
        Dictionary with fetch results including URL and status
    """
    loop = asyncio.get_event_loop()

    try:
        # Run the synchronous fetch function in a thread pool
        result = await asyncio.wait_for(
            loop.run_in_executor(None, functools.partial(fetch_function, url, timeout)),
            timeout=timeout + 5  # Add buffer to timeout
        )

        # Ensure URL is in the result
        if 'url' not in result:
            result['url'] = url

        return result

    except asyncio.TimeoutError:
        return {
            "status": "error",
            "error_message": f"Async operation timed out after {timeout + 5} seconds",
            "url": url
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Async fetch error: {str(e)}",
            "url": url
        }


async def fetch_multiple_urls(
    urls: List[str],
    fetch_function: Callable,
    max_concurrent: int = 5,
    timeout: int = 10
) -> List[Dict[str, Any]]:
    """
    Fetch multiple URLs in parallel with concurrency control.

    Args:
        urls: List of URLs to fetch
        fetch_function: Synchronous function to use for fetching
        max_concurrent: Maximum number of concurrent fetches (default: 5)
        timeout: Timeout per URL in seconds

    Returns:
        List of fetch results (successful and failed)
    """
    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore(url: str) -> Dict[str, Any]:
        async with semaphore:
            return await fetch_url_async(url, fetch_function, timeout)

    # Create tasks for all URLs
    tasks = [fetch_with_semaphore(url) for url in urls]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results and handle any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "status": "error",
                "error_message": f"Fetch failed with exception: {str(result)}",
                "url": urls[i]
            })
        else:
            processed_results.append(result)

    return processed_results


def calculate_success_rate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate success rate and statistics from fetch results.

    Args:
        results: List of fetch results

    Returns:
        Dictionary with statistics:
        - total: Total URLs attempted
        - successful: Number of successful fetches
        - failed: Number of failed fetches
        - success_rate: Percentage of successful fetches
        - error_types: Count of different error types
    """
    total = len(results)
    successful = sum(1 for r in results if r.get('status') == 'success')
    failed = total - successful

    # Count error types
    error_types = {}
    for result in results:
        if result.get('status') == 'error':
            error_msg = result.get('error_message', 'Unknown error')
            # Extract error type
            if '404' in error_msg:
                error_type = '404_not_found'
            elif '403' in error_msg:
                error_type = '403_forbidden'
            elif 'timeout' in error_msg.lower():
                error_type = 'timeout'
            elif 'connection' in error_msg.lower():
                error_type = 'connection_error'
            else:
                error_type = 'other_error'

            error_types[error_type] = error_types.get(error_type, 0) + 1

    success_rate = (successful / total * 100) if total > 0 else 0

    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(success_rate, 2),
        "error_types": error_types
    }


async def fetch_with_retry(
    url: str,
    fetch_function: Callable,
    max_retries: int = 2,
    timeout: int = 10,
    backoff_factor: float = 1.5
) -> Dict[str, Any]:
    """
    Fetch a URL with retry logic for transient failures.

    Args:
        url: URL to fetch
        fetch_function: Function to use for fetching
        max_retries: Maximum number of retry attempts (default: 2)
        timeout: Timeout per attempt
        backoff_factor: Multiplier for timeout on each retry

    Returns:
        Fetch result dictionary
    """
    retryable_errors = ['timeout', 'connection', '503', '504', '429']

    for attempt in range(max_retries + 1):
        # Calculate timeout with exponential backoff
        current_timeout = timeout * (backoff_factor ** attempt)

        result = await fetch_url_async(url, fetch_function, int(current_timeout))

        # Check if successful
        if result.get('status') == 'success':
            if attempt > 0:
                result['retry_attempts'] = attempt
            return result

        # Check if error is retryable
        error_msg = result.get('error_message', '').lower()
        is_retryable = any(err in error_msg for err in retryable_errors)

        # If last attempt or not retryable, return the error
        if attempt == max_retries or not is_retryable:
            result['retry_attempts'] = attempt
            return result

        # Wait before retry (exponential backoff)
        await asyncio.sleep(0.5 * (backoff_factor ** attempt))

    return result


async def fetch_multiple_with_retry(
    urls: List[str],
    fetch_function: Callable,
    max_concurrent: int = 5,
    timeout: int = 10,
    max_retries: int = 2
) -> List[Dict[str, Any]]:
    """
    Fetch multiple URLs in parallel with retry logic.

    Args:
        urls: List of URLs to fetch
        fetch_function: Synchronous function to use for fetching
        max_concurrent: Maximum concurrent requests
        timeout: Base timeout per URL
        max_retries: Number of retry attempts for failed requests

    Returns:
        List of fetch results
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_semaphore_and_retry(url: str) -> Dict[str, Any]:
        async with semaphore:
            return await fetch_with_retry(url, fetch_function, max_retries, timeout)

    tasks = [fetch_with_semaphore_and_retry(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "status": "error",
                "error_message": f"Exception: {str(result)}",
                "url": urls[i]
            })
        else:
            processed_results.append(result)

    return processed_results
