
# An extension of `list` that loops indices.

class Ring(tuple):
    def __getitem__(self, key):
        length = len(self)

        # For slices, one index must still be in the usual range
        # To trigger the special behaviour, the indices must be different and one must be outside the usual range
        # To get the looping effect, modulo the start and stop and index into two copies of the original tuple
        if isinstance(key, slice):
            start, stop = key.start, key.stop
            if start is None:
                start = 0
            if stop is None:
                stop = length
            if start > length or stop < 0 or stop-start > length:
                raise IndexError
            if start != stop and (start < 0 or stop > length):
                start %= length
                stop %= length
                if start >= stop:
                    return (self+self)[slice(start,stop+length,key.step)]

        # For int key, just modulo the index
        elif isinstance(key, int):
            key %= length

        # Fall-through: if no special case has been triggered, call the super() version
        return super().__getitem__(key)
