import sys
from collections import OrderedDict


class LRU(OrderedDict):
    'Limit size, evicting the least recently looked-up key when full'

    def __init__(self, maxsize=128, /, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __len__(self):
        return sum(
            map(
                lambda args: sys.getsizeof(args[1]),
                filter(
                    lambda args: args[0]!="maxsize",
                    self.items()
                )
            )
        )

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]

if __name__ == "__main__":
    cache = LRU(90, name='Sekou Oumar KONE')
    cache.items()
