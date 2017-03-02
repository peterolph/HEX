
from haive import model, hexes, types
import random
import pytest

@pytest.fixture(autouse=True)
def m():
	m = model.Model()
	yield m
	m.assert_consistent()

def test_can_create():
	assert model.Model() is not None

def test_can_str():
	assert str(model.Model()) is not None

def test_move(m):
	token = random.choice(list(m.tokens))
	m.move(token, hexes.centre)
	assert m.tokens[token] == hexes.centre

def test_move_to_cover(m):
	token1, token2 = random.sample(list(m.tokens), 2)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.centre)
	assert m.tokens[token2] == hexes.centre
	assert m.tokens[token1] == token2
	assert m.trapped(token1) == True

def test_cover_then_uncover(m):
	token1, token2 = random.sample(list(m.tokens), 2)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.centre)
	m.move(token2, hexes.offsets[0])
	assert m.tokens[token2] == hexes.offsets[0]
	assert m.tokens[token1] == hexes.centre
	assert m.trapped(token1) == False

def test_cannot_split_hive(m):
	token1, token2, token3 = random.sample(list(m.tokens), 3)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.offsets[0])
	m.move(token3, hexes.opposite(hexes.offsets[0]))
	assert m.trapped(token1) == True
	assert m.trapped(token2) == False
	assert m.trapped(token3) == False

def test_places(m):
	token_black = random.choice(list(m.player_tokens[m.black]))
	token_white1, token_white2 = random.sample(list(m.player_tokens[m.white]), 2)
	assert m.places(m.white) == m.places(m.black) == set()
	m.move(token_black, hexes.centre)
	assert m.places(m.white) == set()
	assert m.places(m.black) == set(hexes.offsets)
	m.move(token_white1, hexes.offsets[0])
	m.move(token_white2, hexes.opposite(hexes.offsets[0]))
	assert m.places(m.black) == set()
