
from haive import model, hexes
import random
import pytest

@pytest.fixture(autouse=True)
def m():
	m = model.Model()
	yield m
	m.assert_consistent()

def gen_token():
	loc = hexes.centre
	for _ in range(10):
		loc = hexes.add(loc,random.choice(hexes.offsets))
	colour = random.choice(model.colours)
	kind = random.choice(model.kinds)
	return {loc: model.Token(colour, kind)}

def test_create(m):
	assert m is not None

def test_save_empty(m):
	assert m.save() is not None

def test_save_nonempty(m):
	m.state.update(gen_token())
	assert m.save() is not None

def test_save_multiple(m):
	m.state.update(gen_token())
	m.state.update(gen_token())
	m.state.update(gen_token())
	assert m.save() is not None


