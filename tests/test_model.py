
from haive import model, hexes
import random
import pytest

@pytest.fixture(autouse=True)
def m():
	m = model.Model()
	yield m
	m.assert_consistent()

def add_token(m,loc, colour=None, kind=None):
	if not colour:
		colour = random.choice(model.colours)
	if not kind:
		kind = random.choice(model.kinds)
	m.state[loc] = model.Token(colour, kind)

def test_create(m):
	assert m is not None

def test_save_empty(m):
	assert m.save() is not None

def test_save_nonempty(m):
	add_token(m, hexes.centre)
	assert m.save() is not None

def test_save_multiple(m):
	add_token(m, hexes.centre)
	add_token(m, hexes.offsets[0])
	add_token(m, hexes.offsets[1])
	assert m.save() is not None

def test_neighbours_none(m):
	assert len(m.neighbours(hexes.centre)) == 0

def test_neighbours_some(m):
	for offset in random.sample(hexes.offsets, 4):
		add_token(m, offset)
	assert len(m.neighbours(hexes.centre)) == 4

def test_move_sources_empty(m):
	assert len(m.move_sources()) == 0

def test_move_sources_one(m):
	add_token(m, hexes.centre)
	assert len(m.move_sources()) == 1

def test_move_sources_two(m):
	add_token(m, hexes.centre)
	add_token(m, hexes.offsets[0])
	assert len(m.move_sources()) == 2

def test_move_sources_line(m):
	add_token(m, hexes.centre)
	for i in range(1,8):
		add_token(m, hexes.mul(hexes.offsets[0], i))
	assert len(m.state) == 1 + 7
	assert len(m.move_sources()) == 2

def test_move_sources_star(m):
	add_token(m, hexes.centre)
	for i in range(1,8):
		for offset in hexes.offsets[::2]:
			add_token(m, hexes.mul(offset, i))
	assert len(m.state) == 1 + 3*7
	assert len(m.move_sources()) == 3

def test_move_sources_loop(m):
	for offset in hexes.offsets:
		add_token(m, offset)
	assert len(m.state) == 6
	assert len(m.move_sources()) == 6

def test_places_empty(m):
	assert len(m.places(model.white)) == 1
	assert len(m.places(model.black)) == 1

def test_places_single(m):
	add_token(m, hexes.centre, model.white)
	assert len(m.places(model.white)) == 6
	assert len(m.places(model.black)) == 6

def test_places_pair(m):
	add_token(m, hexes.centre, model.white)
	add_token(m, hexes.offsets[0], model.black)
	assert len(m.places(model.white)) == 3
	assert len(m.places(model.black)) == 3

def test_places_line(m):
	add_token(m, hexes.centre, model.white)
	add_token(m, hexes.offsets[0], model.black)
	add_token(m, hexes.opposite(hexes.offsets[0]), model.black)
	assert len(m.places(model.white)) == 0
	assert len(m.places(model.black)) == 6

def test_places_dont_intersect(m):
	add_token(m, hexes.centre, model.black)
	add_token(m, hexes.offsets[0], model.black)
	assert len(m.places(model.white)) == 0
	assert len(m.places(model.black)) == 8
