"""
Домашнее задание 2: Race Condition и Lock
"""

import threading


def increment_with_race(counter: list[int], times: int) -> None:
    import time
    for _ in range(times):
        current = counter[0]
        time.sleep(0.000001)
        counter[0] = current + 1


def increment_safe(counter: list[int], times: int, lock: threading.Lock) -> None:
    for _ in range(times):
        with lock:
            counter[0] = counter[0] + 1


class InsufficientFundsError(Exception):
    pass


class BankAccount:
    def __init__(self, initial_balance: float = 0.0) -> None:
        self.balance = initial_balance
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        with self._lock:
            self.balance += amount

    def withdraw(self, amount: float) -> None:
        with self._lock:
            if self.balance < amount:
                raise InsufficientFundsError("Недостаточно средств")
            self.balance -= amount

    def get_balance(self) -> float:
        with self._lock:
            return self.balance
