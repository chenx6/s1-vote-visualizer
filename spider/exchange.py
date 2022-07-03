from collections import defaultdict
from typing import Set, Tuple, Callable


class Exchange:
    """发布，订阅模型交换机"""

    def __init__(self) -> None:
        self._subscribers: Set[Callable] = set()

    def attach(self, task: Callable):
        self._subscribers.add(task)

    def detach(self, task: Callable):
        self._subscribers.remove(task)

    def send(self, msg: Tuple):
        for subscriber in self._subscribers:
            subscriber(*msg)


_exchanges = defaultdict(Exchange)


def get_exchange(name: str):
    return _exchanges[name]
