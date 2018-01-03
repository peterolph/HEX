
from haive import model, hexes
import random
import pytest

@pytest.fixture(autouse=True)
def m():
    m = model.Model()
    yield m

lookup_colour = {colour[0]: colour for colour in model.colours}
lookup_kind = {kind[0]: kind for kind in model.kinds}

# Add a number of tokens using a simple language.
# 'wB bb wh' generates a white bee, a black beetle and a white hopper
#   with the white beetle at the centre of the board.
# The output can then be repeated in a circle around the centre
#   with a given step between repetitions.
# '-' can be used to specify an empty space.
def add_tokens(m, string, step=6, clear=True):
    if clear:
        m.state = {}
    tokens = string.split()
    for factor, token in enumerate(tokens):
        if token == '-':
            pass
        else:
            colour = lookup_colour[token[0]]
            kind = lookup_kind[token[1]]
            for offset in hexes.offsets[::factor>0 and step or 6]:
                m.add(hexes.mul(offset, factor), model.Token(colour, kind))

# BASICS

def test_create(m):
    assert m is not None

def test_save_empty(m):
    assert m.save() is not None

def test_save_nonempty(m):
    add_tokens(m, 'wB')
    assert m.save() is not None

def test_save_multiple(m):
    add_tokens(m, 'bb wB bh')
    assert m.save() is not None

def test_occupied_neighbours_none(m):
    assert len(m.occupied_neighbours(hexes.centre)) == 0

def test_occupied_neighbours_some(m):
    add_tokens(m, 'wB wa', step=2)
    assert len(m.occupied_neighbours(hexes.centre)) == 3

def test_unoccupied_neighbours_none(m):
    assert len(m.unoccupied_neighbours(hexes.centre)) == 6

def test_unoccupied_neighbours_some(m):
    add_tokens(m, 'wB wa', step=2)
    assert len(m.occupied_neighbours(hexes.centre)) == 3

def test_unique_unoccupied_neighbours_one(m):
    add_tokens(m, 'wB')
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 6

def test_unique_unoccupied_neighbours_two(m):
    add_tokens(m, 'wB wa')
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 3

def test_unique_unoccupied_neighbours_line(m):
    add_tokens(m, 'wB wa', step=3)
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 0

def test_unique_unoccupied_neighbours_curved_line(m):
    add_tokens(m, 'wB wa', step=4)
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 1

def test_colour_hands(m):
    assert len(m.colour_hand(model.white)) == 5
    add_tokens(m, 'wB wh wh wh ws ws')
    assert len(m.colour_hand(model.white)) == 2
    assert model.ant in m.colour_hand(model.white) and model.beetle in m.colour_hand(model.white)

def test_move(m):
	assert len(m.state) == 0
	assert len(m.active_hexes()) == 0
	m.add(hexes.centre, model.Token(model.white, model.bee))
	assert len(m.state) == 1
	assert len(m.active_hexes()) == 1
	m.add(hexes.offsets[0], model.Token(model.black, model.ant))
	assert len(m.state) == 2
	assert len(m.active_hexes()) == 2
	m.add(hexes.centre, model.Token(model.black, model.beetle))
	assert len(m.state) == 3
	assert len(m.active_hexes()) == 2

	m.remove(hexes.centre)
	assert len(m.state) == 2
	assert len(m.active_hexes()) == 2

	m.move(hexes.offsets[0], hexes.centre)
	assert len(m.state) == 2
	assert len(m.active_hexes()) == 1

# PLACES

def test_colour_places_empty(m):
    assert len(m.colour_places(model.white)) == 1
    assert len(m.colour_places(model.black)) == 1

def test_colour_places_single(m):
    add_tokens(m, 'wB')
    assert len(m.colour_places(model.white)) == 6
    assert len(m.colour_places(model.black)) == 6

def test_colour_places_pair(m):
    add_tokens(m, 'wB bB')
    assert len(m.colour_places(model.white)) == 3
    assert len(m.colour_places(model.black)) == 3

def test_colour_places_line(m):
    add_tokens(m, 'bB wB bB')
    assert len(m.colour_places(model.white)) == 0
    assert len(m.colour_places(model.black)) == 6

def test_colour_places_dont_intersect(m):
    add_tokens(m, 'bB bB')
    assert len(m.colour_places(model.white)) == 0
    assert len(m.colour_places(model.black)) == 8

def test_places(m):
    add_tokens(m, 'bB ba bb wh wa wb ba')
    assert m.places() == {model.white:m.colour_places(model.white), model.black:m.colour_places(model.black)}

# MOVES

def test_move_sources_empty(m):
    assert len(m.move_sources()) == 0

def test_move_sources_one(m):
    add_tokens(m, 'wB')
    assert len(m.move_sources()) == 1

def test_move_sources_two(m):
    add_tokens(m, 'wB ba')
    assert len(m.move_sources()) == 2

def test_move_sources_line(m):
    add_tokens(m, 'ba wB ba wh bb ws bs wa')
    assert len(m.state) == 1 + 7
    assert len(m.move_sources()) == 2

def test_move_sources_star(m):
    add_tokens(m, 'ba wB ba wh bb ws bs wa', step=2)
    assert len(m.state) == 1 + 3*7
    assert len(m.move_sources()) == 3

def test_move_sources_loop(m):
    add_tokens(m, '- wB', step=1)
    assert len(m.state) == 6
    assert len(m.move_sources()) == 6

def crawl_graph_assertions(graph):
    for hex, node in graph.items():
        assert len(node.left) > 0
        assert len(node.right) > 0
        for dest in node.left | node.right:
            assert dest in graph

def crawl_graph_loop(graph, start, length):
    lpos = rpos = start
    for i in range(length):
        if i != 0:
            assert lpos != start
            assert rpos != start
        if length%2 == 0 and i == length / 2:
            assert lpos == rpos
        lpos = list(graph[lpos].left)[0]
        rpos = list(graph[rpos].right)[0]
    assert lpos == start
    assert rpos == start

def test_crawl_graph(m):
    add_tokens(m, 'wB wa')
    result = m.crawl_graph()
    crawl_graph_assertions(result)
    assert len(result) == 8
    crawl_graph_loop(result, list(result)[0], 8)

def test_crawl_graph_disconnected(m):
    add_tokens(m, 'wB wa - - - - bB ba')
    result = m.crawl_graph()
    crawl_graph_assertions(result)
    assert len(result) == 16
    crawl_graph_loop(result, list(result)[0], 8)

def test_crawl_graph_forked(m):
    add_tokens(m, 'wB wa - bB ba')
    result = m.crawl_graph()
    crawl_graph_assertions(result)
    assert len(result) == 15
    fork_hex = hexes.mul(hexes.offsets[0],2)
    assert len(result[fork_hex].left) == 2
    assert len(result[fork_hex].right) == 2
    assert sum(1 for hex, node in result.items() if fork_hex in node.left | node.right)

def test_crawl_graph_trapped(m):
    add_tokens(m, 'wB wh', step=1)
    result = m.crawl_graph()
    crawl_graph_assertions(result)
    assert len(result) == 0

def test_crawl_graph_loop(m):
    add_tokens(m, '- wB', step=1)
    result = m.crawl_graph()
    crawl_graph_assertions(result)
    assert len(result) == 12
    assert hexes.centre not in result

def test_bee_moves_end(m):
    add_tokens(m, 'wB wa wa wa')
    assert len(m.bee_moves(hexes.centre)) == 2

def test_bee_moves_middle(m):
    add_tokens(m, 'wB wa wa wa', step=3)
    assert len(m.bee_moves(hexes.centre)) == 4

def test_spider_moves_two(m):
    add_tokens(m, 'ws wa')
    assert len(m.spider_moves(hexes.centre)) == 1
    assert m.spider_moves(hexes.centre).pop() == hexes.mul(hexes.offsets[0],2)

def test_spider_moves_middle(m):
    add_tokens(m, 'ws wa', step=3)
    assert len(m.spider_moves(hexes.centre)) == 2
    left, right = m.spider_moves(hexes.centre)
    assert hexes.add(left, right) == hexes.centre

def test_ant_moves_end(m):
    add_tokens(m, 'wa bh bh bh')
    assert len(m.ant_moves(hexes.centre)) == 9

def test_ant_moves_middle(m):
    add_tokens(m, 'wa bh bh', step=3)
    assert len(m.ant_moves(hexes.centre)) == 14

def test_ant_moves_loop(m):
    add_tokens(m, '- bh', step=1)
    add_tokens(m, '- wa', clear=False)
    assert len(m.ant_moves(hexes.offsets[0])) == 11

def test_hopper_moves_end(m):
    add_tokens(m, 'wh ba ba ba')
    assert len(m.hopper_moves(hexes.centre)) == 1

def test_hopper_moves_middle(m):
    add_tokens(m, 'wh ba ba ba', step=3)
    assert len(m.hopper_moves(hexes.centre)) == 2

def test_hopper_spider_moves(m):
    add_tokens(m, 'wh ba', step=3)
    assert m.hopper_moves(hexes.centre) == m.spider_moves(hexes.centre)

def test_beetle_moves_end(m):
    add_tokens(m, 'wb ba ba ba')
    assert len(m.beetle_moves(hexes.centre)) == 3

def test_beetle_moves_middle(m):
    add_tokens(m, 'wb ba ba ba', step=3)
    assert len(m.beetle_moves(hexes.centre)) == 6

def test_trapped_moves(m):
    add_tokens(m, 'wB wa', step=1)
    assert len(m.bee_moves(hexes.centre)) == 0
    assert len(m.spider_moves(hexes.centre)) == 0
    assert len(m.ant_moves(hexes.centre)) == 0
    assert len(m.hopper_moves(hexes.centre)) == 6
    assert len(m.beetle_moves(hexes.centre)) == 6

def test_trapped_star_moves(m):
    add_tokens(m, 'wB wa wa wa', step=2)
    assert len(m.bee_moves(hexes.centre)) == 0
    assert len(m.spider_moves(hexes.centre)) == 0
    assert len(m.ant_moves(hexes.centre)) == 0
    assert len(m.hopper_moves(hexes.centre)) == 3
    assert len(m.beetle_moves(hexes.centre)) == 3

def moves_helper(moves):
    joined = {**moves[model.black], **moves[model.white]}
    return len(joined), len(hexes.merge(joined.values()))

def test_moves_none(m):
    assert moves_helper(m.moves()) == (0,0)

def test_moves_one(m):
    assert moves_helper(m.moves()) == (0,0)

def test_moves_pairs(m):
    add_tokens(m, 'wB bB')
    assert moves_helper(m.moves()) == (2,2)
    add_tokens(m, 'wB bs')
    assert moves_helper(m.moves()) == (2,3)
    add_tokens(m, 'wB ba')
    assert moves_helper(m.moves()) == (2,5)
    add_tokens(m, 'wB bh')
    assert moves_helper(m.moves()) == (2,3)
    add_tokens(m, 'wB bb')
    assert moves_helper(m.moves()) == (2,3)

    add_tokens(m, 'ws bs')
    assert moves_helper(m.moves()) == (2,2)
    add_tokens(m, 'wa ba')
    assert moves_helper(m.moves()) == (2,8)
    add_tokens(m, 'wh bh')
    assert moves_helper(m.moves()) == (2,2)
    add_tokens(m, 'wb bb')
    assert moves_helper(m.moves()) == (2,4)

def test_moves_lines(m):
    add_tokens(m, 'wB ba ba ba ba bB')
    assert moves_helper(m.moves()) == (2,4)
    add_tokens(m, 'ws ba ba ba ba bs')
    assert moves_helper(m.moves()) == (2,2)
    add_tokens(m, 'wa ba ba ba ba ba')
    assert moves_helper(m.moves()) == (2,16)
    add_tokens(m, 'wh ba ba ba ba bh')
    assert moves_helper(m.moves()) == (2,2)
    add_tokens(m, 'wb ba ba ba ba bb')
    assert moves_helper(m.moves()) == (2,6)

def test_moves_loops(m):
    add_tokens(m, '- wB', step=1)
    assert moves_helper(m.moves()) == (6,6)
    add_tokens(m, '- ws', step=1)
    assert moves_helper(m.moves()) == (6,6)
    add_tokens(m, '- wa', step=1)
    assert moves_helper(m.moves()) == (6,12)
    add_tokens(m, '- wh', step=1)
    assert moves_helper(m.moves()) == (6,6)
    add_tokens(m, '- wb', step=1)
    assert moves_helper(m.moves()) == (6,12)
