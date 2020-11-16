from types import FunctionType
from typing import Callable, Sequence
from functools import reduce
import pymem
from pymem import Pymem
import keyboard


class PointerChain:
    def __init__(self, offsets: Sequence[int]):
        self._offsets_ = offsets

    def resolve(self, pm: Pymem, base) -> int:
        try:
            addr = base
            for offset in self._offsets_[:-1]:
                addr = pm.read_int(addr + offset)
            return addr + self._offsets_[-1]
        except:
            return None
        #off = self._offsets_[:-1]
        # return reduce(lambda addr, offset: pm.read_int(addr + offset), off, base) + self._offsets_[-1]


class Hotkeys:
    def __init__(self, key: str, cbDown: Callable = None, cbUp: Callable = None):
        self._signals_ = {}
        self._cbDown_ = cbDown
        self._cbUp_ = cbUp
        keyboard.on_press_key(key, self._cb_)
        keyboard.on_release_key(key, self._cb_)

    def _cb_(self, event):
        if event.event_type == 'down' and self._cbDown_ != None:
            self._cbDown_(event)
        elif event.event_type == 'up' and self._cbUp_ != None:
            self._cbUp_(event)
