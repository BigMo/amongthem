import struct
import time
from types import FunctionType
from typing import Callable, Generic, List, Sequence, TypeVar
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


class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Map):
            return False
        for k, v in self.items():
            if k.startswith('_'):
                continue
            _o = o.get(k)
            if _o != v:
                return False

        return True

    def __setattr__(self, key, value):
        _current = self.get(key)
        self.__setitem__(key, value)
        if isinstance(value, dict):
            return

        if _current == value:
            return

        _pm: Pymem = self.get('_pm')
        _type = self.get('_type')
        _addr = self.get('_addr')
        _bytes = struct.pack(_type[key]['unpack'], value)
        _pm.write_bytes(_addr + _type[key]['offset'], _bytes, len(_bytes))

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


T = TypeVar('T')


class ItemHistory(Generic[T]):
    def __init__(self, maxCount: int = -1, maxAge: float = -1.0, updateInterval=-1.0, redundant=True):
        self._items_: List[T] = []
        self._redundant_: bool = redundant
        self._updateInterval_: float = updateInterval
        self._lastUpdate_: float = time.time()
        if maxCount < 0 and maxAge < 0:
            raise Exception('Requires at least one constraint!')
        self._maxCount_ = maxCount
        self._maxAge_ = maxAge

    @property
    def items(self) -> Sequence[T]:
        return self._items_

    def append(self, item: T):
        if self._updateInterval_ > 0 and (time.time() - self._lastUpdate_) < self._updateInterval_:
            return
        if not self._redundant_ and len(self._items_) > 0 and self._items_[-1] == item:
            return
        self._items_.append(item)
        self._lastUpdate_ = time.time()
        while self._maxCount_ > 0 and len(self._items_) > self._maxCount_:
            self._items_.pop(0)

    def update(self):
        now = time.time()
        while self._maxAge_ > 0 and len(self._items_) > 0 and (now - self._items_[0]._time) > self._maxAge_:
            self._items_.pop(0)
