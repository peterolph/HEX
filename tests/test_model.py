
from haive import model, hexes, types
import random

def assert_consistent(m):
	for token, loc in m.tokens.items():
		if loc is not None:
			print(token, loc)
			assert m.reverse[loc] == token

def test_can_create():
	assert model.Model() is not None

def test_can_str():
	assert str(model.Model()) is not None

def test_move():
	m = model.Model()
	token = random.choice(list(m.tokens))
	m.move(token, hexes.centre)
	assert m.tokens[token] == hexes.centre
	assert_consistent(m)

def test_move_to_cover():
	m = model.Model()
	token1, token2 = random.sample(list(m.tokens), 2)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.centre)
	assert m.tokens[token2] == hexes.centre
	assert m.tokens[token1] == token2
	assert m.trapped(token1) == True
	assert_consistent(m)

def test_cover_then_uncover():
	m = model.Model()
	token1, token2 = random.sample(list(m.tokens), 2)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.centre)
	m.move(token2, hexes.offsets[0])
	assert m.tokens[token2] == hexes.offsets[0]
	assert m.tokens[token1] == hexes.centre
	assert m.trapped(token1) == False
	assert_consistent(m)

def test_cannot_split_hive():
	m = model.Model()
	token1, token2, token3 = random.sample(list(m.tokens), 3)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.offsets[0])
	m.move(token3, hexes.opposite(hexes.offsets[0]))
	assert m.trapped(token1) == True
	assert m.trapped(token2) == False
	assert m.trapped(token3) == False
	assert_consistent(m)