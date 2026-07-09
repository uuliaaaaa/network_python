"""
Домашнее задание 4: Asyncio
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor


async def fetch_one_async(url: str) -> str:
    await asyncio.sleep(0.05)
    return f"data:{url}"


async def fetch_all_async(urls: list[str]) -> list[str]:
    tasks = [fetch_one_async(url) for url in urls]
    return await asyncio.gather(*tasks)


async def fetch_with_delay(name: str, delay: float, fail: bool = False) -> str:
    await asyncio.sleep(delay)
    if fail:
        raise ValueError(f"Ошибка загрузки {name}")
    return f"data:{name}"


async def run_task_group(names: list[str]) -> dict[str, str | None]:
    results = {}
    try:
        async with asyncio.TaskGroup() as tg:
            for name in names:
                task = tg.create_task(
                    fetch_with_delay(name, delay=0.1, fail=("bad" in name))
                )
                results[name] = task
    except* ValueError:
        pass
    final = {}
    for name, task in results.items():
        try:
            final[name] = task.result()
        except ValueError:
            final[name] = None
    if all(v is None for v in final.values()):
        return {}
    return final


async def fetch_with_timeout(url: str, delay: float, timeout: float) -> str:
    async def fetch_with_delay():
        await asyncio.sleep(delay)
        return f"data:{url}"
    try:
        return await asyncio.wait_for(fetch_with_delay(), timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Таймаут {timeout}с превышен для {url}")


async def cancellable_worker(name: str, steps: int) -> str:
    try:
        for step in range(1, steps + 1):
            print(f"  {name}: шаг {step}")
            await asyncio.sleep(0.1)
        return f"{name}: готов после {steps} шагов"
    except asyncio.CancelledError:
        print(f"  {name}: очищаю ресурсы...")
        raise


async def run_with_cancel(name: str, steps: int, cancel_after: float) -> str | None:
    task = asyncio.create_task(cancellable_worker(name, steps))
    await asyncio.sleep(cancel_after)
    task.cancel()
    try:
        return await task
    except asyncio.CancelledError:
        return None


async def fast_or_slow(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name}: готов за {delay}с"


async def fetch_as_completed(tasks: list[tuple[str, float]]) -> list[str]:
    coroutines = [fast_or_slow(name, delay) for name, delay in tasks]
    results = []
    for coro in asyncio.as_completed(coroutines):
        result = await coro
        results.append(result)
    return results


def blocking_compute(x: int) -> int:
    import math
    import time
    time.sleep(0.01)
    for i in range(2, int(math.sqrt(x)) + 1):
        if x % i == 0:
            return 0
    return x


async def async_process_numbers(numbers: list[int], max_workers: int = 4) -> list[int]:
    async def process_one(x: int) -> int:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, blocking_compute, x)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = [asyncio.create_task(process_one(n)) for n in numbers]
        results = await asyncio.gather(*tasks)
    return results
