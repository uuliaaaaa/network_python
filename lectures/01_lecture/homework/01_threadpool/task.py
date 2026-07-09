"""
Домашнее задание 1: ThreadPoolExecutor
"""

from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_one(url: str) -> str:
    import time
    time.sleep(0.05)
    return f"data:{url}"


def fetch_one_with_delay(url_delay: tuple[str, float]) -> str:
    url, delay = url_delay
    import time
    time.sleep(delay)
    return f"data:{url}"


def fetch_all(urls: list[str], max_workers: int = 4) -> list[str]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fetch_one, urls))


def fetch_all_with_errors(urls: list[str], max_workers: int = 4) -> list[str | None]:
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_one, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results[url] = None if "bad" in url else result
            except Exception:
                results[url] = None
    return [results.get(url) for url in urls]


def fetch_all_with_progress(
    urls: list[str],
    max_workers: int = 4,
    progress_callback: Callable[[int, int], None] | None = None,
) -> list[str]:
    total = len(urls)
    completed = 0
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(fetch_one, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append((url, result))
            except Exception:
                results.append((url, None))
            completed += 1
            if progress_callback:
                progress_callback(completed, total)
    return [result for _, result in results]
