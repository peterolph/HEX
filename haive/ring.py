
# An extension of `list` that loops indices.

class Ring(list):
    def _getsuper(self, key):
        return super().__getitem__(key)

    def __getitem__(self, key):
        length = len(self)
        if isinstance(key, slice):
            if key.stop - key.start > length:
                raise IndexError
            start = key.start % length
            stop = key.stop % length
            if start >= stop:
                return (self+self)[slice(start,stop+length,key.step)]
            else:
                return self._getsuper(slice(start,stop,key.step))
        else:
            key %= length
            return self._getsuper(key)