
from haive import ring
import pytest

@pytest.fixture(autouse=True)
def r():
    r = ring.Ring([0,1,2,3,4,5])
    yield r

def test_keys(r):
    for i in range(-len(r),2*len(r)):
        assert r[i] == i % len(r)

def test_ranges(r):
    for i in range(-len(r),len(r)):
        for j in range(max(0,i),i+len(r)+1):
            result = r[i:j]
            assert len(result) == j-i
            if len(result) > 0:
                assert result[0] == i % len(r)
                assert result[-1] == (j-1) % len(r)

def test_ranges_with_steps(r):
    for i in range(-len(r),len(r)):
        for j in range(max(0,i),i+len(r)+1):
            for step in range(1,len(r)):
                result = r[i:j:step]
                assert len(result) == ((j-i-1) // step) + 1
