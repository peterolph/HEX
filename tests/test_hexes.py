
import functools
from haive import hexes

def rotate_n_times(dir,offset,n):
    for _ in range(n):
        offset = hexes.rotate(dir, offset)
    return offset

def sum(set_of_hexes):
	return functools.reduce(hexes.add, set_of_hexes)

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
        assert rotate_n_times(hexes.left,offset,6) == offset
        assert rotate_n_times(hexes.right,offset,6) == offset
        for n in range(6):
            assert rotate_n_times(hexes.left,offset,n) == rotate_n_times(hexes.right,offset,6-n)

def test_rotate_to_opposite():
    for offset in hexes.offsets:
        assert rotate_n_times(hexes.left,offset,3) == hexes.opposite(offset)
        assert rotate_n_times(hexes.right,offset,3) == hexes.opposite(offset)

def test_all_offsets():
    assert sum(hexes.offsets) == hexes.centre

def test_neighbours():
	assert hexes.neighbours(hexes.centre) == set(hexes.offsets)
	test_hex = (2,5,7)
	assert sum(hexes.neighbours(test_hex)) == hexes.mul(test_hex, 6)

def test_merge():
	some_hexes = hexes.neighbours((9,2,4))
	assert hexes.merge(()) == set()
	assert hexes.merge((some_hexes,)) == some_hexes
	assert hexes.merge((some_hexes, some_hexes)) == some_hexes