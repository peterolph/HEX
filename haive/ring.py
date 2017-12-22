
# An extension of `list` that loops indices.

class Ring(tuple):
    def _getsuper(self, key):
        return super().__getitem__(key)

    def __getitem__(self, key):
        length = len(self)
        if isinstance(key, slice):
            start, stop = key.start, key.stop
            if start is None:
                start = 0
            if stop is None:
                stop = length
            if stop - start > length:
                raise IndexError
            start %= length
            stop %= length
            if start >= stop:
                return (self+self)[slice(start,stop+length,key.step)]
            else:
                return self._getsuper(slice(start,stop,key.step))
        else:
            key %= length
            return self._getsuper(key)