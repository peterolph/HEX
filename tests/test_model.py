
from haive import model, hexes, types
import random

def assert_consistent(m):
	for token, loc in m.tokens.items():
		if type(loc) == types.Token:
			assert token in m.tokens_covering().values()
		elif type(loc) == tuple:
			assert loc in m.hexes_occupied()
			assert m.token_at(loc) == token

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
	assert_consistent(m)

def test_cover_then_uncover():
	m = model.Model()
	token1, token2 = random.sample(list(m.tokens), 2)
	m.move(token1, hexes.centre)
	m.move(token2, hexes.centre)
	m.move(token2, hexes.offsets[0])
	assert m.tokens[token2] == hexes.offsets[0]
	assert m.tokens[token1] == hexes.centre
	assert_consistent(m)