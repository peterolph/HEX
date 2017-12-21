
from haive import model, hexes
import random
import pytest

test_state = '0,0,0:white:Bee|0,0,1:black:beetle'

@pytest.fixture(autouse=True)
def m():
	m = model.Model()
	yield m
	m.assert_consistent()

def test_create(m):
	assert m is not None

def test_load_then_save(m):
	expected_state = test_state
	m.load(test_state)
	assert m.save() == expected_state

