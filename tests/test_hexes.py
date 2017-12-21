
import functools
from haive import hexes

def rotate_n_times(offset,dir,n):
    for _ in range(n):
        offset = hexes.rotate(offset,dir)
    return offset

def test_add():
    assert hexes.add((1,2,3),(4,5,6)) == (5,7,9)

def test_sub():
    assert hexes.sub((1,2,3),(4,5,6)) == (-3,-3,-3)

def test_mul():
    assert hexes.mul((1,2,3),4) == (4,8,12)

def test_opposite():
    for offset in hexes.offsets:
        assert hexes.opposite(hexes.opposite(offset)) == offset
        assert hexes.add(hexes.opposite(offset), offset) == hexes.centre

def test_rotate():
    for offset in hexes.offsets:
        assert rotate_n_times(offset,hexes.left,6) == offset
        assert rotate_n_times(offset,hexes.right,6) == offset
        for n in range(6):
            assert rotate_n_times(offset,hexes.left,n) == rotate_n_times(offset,hexes.right,6-n)

def test_rotate_to_opposite():
    for offset in hexes.offsets:
        assert rotate_n_times(offset,hexes.left,3) == hexes.opposite(offset)
        assert rotate_n_times(offset,hexes.right,3) == hexes.opposite(offset)

def test_all_offsets():
    assert functools.reduce(hexes.add, hexes.offsets) == hexes.centre
