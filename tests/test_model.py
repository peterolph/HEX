
from ponder import model, hexes
from ponder.tuples import Token
import random
import pytest

@pytest.fixture(autouse=True)
def m():
    m = model.Model()
    yield m

lookup_colour = {colour[0]: colour for colour in model.colours}
lookup_kind = {kind[0]: kind for kind in model.kinds}

def token_from_string(string):
    if string == '-':
        return None
    else:
        colour = lookup_colour[string[0]]
        kind = lookup_kind[string[1]]
        return Token(colour, kind)

# Add a number of tokens using a simple language.
# 'wB bb wh' generates a white bee, a black beetle and a white hopper
#   with the white beetle at the centre of the board.
# The output can then be repeated in a circle around the centre
#   with a given step between repetitions.
# '-' can be used to specify an empty space.
def set_state(m, string, step=6):
    strings = string.split()
    for factor, string in enumerate(strings):
        token = token_from_string(string)
        if token is not None:
            for offset in hexes.offsets[::step]:
                m.state[hexes.mul(offset, factor)] = token

def add_token(m, string, hex=hexes.centre):
    m.add(token_from_string(string), hex)

# BASICS

def test_create(m):
    assert m is not None

def test_save_empty(m):
    assert m.save() is not None

def test_save_nonempty(m):
    set_state(m, 'wB')
    assert m.save() is not None

def test_save_multiple(m):
    set_state(m, 'bb wB bh')
    assert m.save() is not None

def test_occupied_neighbours_none(m):
    assert len(m.occupied_neighbours(hexes.centre)) == 0

def test_occupied_neighbours_some(m):
    set_state(m, 'wB wa', step=2)
    assert len(m.occupied_neighbours(hexes.centre)) == 3

def test_unoccupied_neighbours_none(m):
    assert len(m.unoccupied_neighbours(hexes.centre)) == 6

def test_unoccupied_neighbours_some(m):
    set_state(m, 'wB wa', step=2)
    assert len(m.occupied_neighbours(hexes.centre)) == 3

def test_unique_unoccupied_neighbours_one(m):
    set_state(m, 'wB')
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 6

def test_unique_unoccupied_neighbours_two(m):
    set_state(m, 'wB wa')
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 3

def test_unique_unoccupied_neighbours_line(m):
    set_state(m, 'wB wa', step=3)
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 0

def test_unique_unoccupied_neighbours_curved_line(m):
    set_state(m, 'wB wa', step=4)
    assert(len(m.unique_unoccupied_neighbours(hexes.centre))) == 1

def test_colour_hands(m):
    assert len(m.colour_hand(model.white)) == 5
    set_state(m, 'wB wh wh wh ws ws')
    assert len(m.colour_hand(model.white)) == 2
    assert model.ant in m.colour_hand(model.white) and model.beetle in m.colour_hand(model.white)
    set_state(m, 'wh wh wh')
    assert len(m.colour_hand(model.white)) == 1
    assert model.bee in m.colour_hand(model.white)

def test_move(m):
    assert len(m.state) == 0
    assert len(m.active_hexes()) == 0
    add_token(m, 'wB')
    assert len(m.state) == 1
    assert len(m.active_hexes()) == 1
    add_token(m, 'ba', hexes.offsets[0])
    assert len(m.state) == 2
    assert len(m.active_hexes()) == 2
    add_token(m, 'bb')
    assert len(m.state) == 3
    assert len(m.active_hexes()) == 2

    m.remove(hexes.centre)
    assert len(m.state) == 2
    assert len(m.active_hexes()) == 2

    m.move(hexes.offsets[0], hexes.centre)
    assert len(m.state) == 2
    assert len(m.active_hexes()) == 1

def test_colour_bee_placed(m):
    assert m.colour_bee_placed(model.white) == False
    assert m.colour_bee_placed(model.black) == False
    set_state(m, 'wB')
    assert m.colour_bee_placed(model.white) == True
    assert m.colour_bee_placed(model.black) == False

def test_winner(m):
    set_state(m, 'wB ba')
    assert m.winner() is None
    set_state(m, 'wB ba', step=1)
    assert m.winner() is model.black
    set_state(m, 'bB wa', step=1)
    add_token(m, 'bb')
    assert m.winner() is model.white

# PLACES

def test_colour_places_empty(m):
    assert len(m.colour_places(model.white)) == 1
    assert len(m.colour_places(model.black)) == 1
    assert list(m.colour_places(model.white))[0] == hexes.centre
    assert list(m.colour_places(model.black))[0] == hexes.centre

def test_colour_places_single(m):
    set_state(m, 'wB')
    assert len(m.colour_places(model.white)) == 6
    assert len(m.colour_places(model.black)) == 6

def test_colour_places_pair(m):
    set_state(m, 'wB bB')
    assert len(m.colour_places(model.white)) == 3
    assert len(m.colour_places(model.black)) == 3

def test_colour_places_line(m):
    set_state(m, 'bB wB bB')
    assert len(m.colour_places(model.white)) == 0
    assert len(m.colour_places(model.black)) == 6

def test_colour_places_dont_intersect(m):
    set_state(m, 'bB bB')
    assert len(m.colour_places(model.white)) == 0
    assert len(m.colour_places(model.black)) == 8

def test_places(m):
    set_state(m, 'bB ba bb wh wa wb ba')
    assert m.places() == {model.white:m.colour_places(model.white), model.black:m.colour_places(model.black)}

# MOVES

def test_move_sources_empty(m):
    assert len(m.move_sources()) == 0

def test_move_sources_one(m):
    set_state(m, 'wB')
    assert len(m.move_sources()) == 1

def test_move_sources_two(m):
    set_state(m, 'wB ba')
    assert len(m.move_sources()) == 2

def test_move_sources_line(m):
    set_state(m, 'ba wB ba wh bb ws bs wa')
    assert len(m.state) == 1 + 7
    assert len(m.move_sources()) == 2

def test_move_sources_star(m):
    set_state(m, 'ba wB ba wh bb ws bs wa', step=2)
    assert len(m.state) == 1 + 3*7
    assert len(m.move_sources()) == 3

def test_move_sources_loop(m):
    set_state(m, '- wB', step=1)
    assert len(m.state) == 6
    assert len(m.move_sources()) == 6

def crawl_graph_assertions(graph):
    for hex, node in graph.items():
        assert len(node.left) > 0
        assert len(node.right) > 0
        for dest in node.left | node.right:
            assert dest in graph

def test_crawl_graph(m):
    set_state(m, 'wa wh')
    result = m.crawl_graph(hexes.centre)
    crawl_graph_assertions(result)
    assert len(result) == 6

def test_crawl_graph_disconnected(m):
    set_state(m, 'wa wh - - - - bh bh')
    result = m.crawl_graph(hexes.centre)
    crawl_graph_assertions(result)
    assert len(result) == 6

def test_crawl_graph_forked(m):
    set_state(m, 'wa wh - bh bh')
    result = m.crawl_graph(hexes.centre)
    crawl_graph_assertions(result)
    assert len(result) == 13
    fork_hex = hexes.mul(hexes.offsets[0],2)
    assert len(result[fork_hex].left) == 2
    assert len(result[fork_hex].right) == 2
    assert sum(1 for hex, node in result.items() if fork_hex in node.left | node.right)

def test_crawl_graph_trapped(m):
    set_state(m, 'wa wh', step=1)
    result = m.crawl_graph(hexes.centre)
    crawl_graph_assertions(result)
    assert len(result) == 0

def test_crawl_graph_loop(m):
    set_state(m, '- wa', step=1)
    result = m.crawl_graph(hexes.offsets[0])
    crawl_graph_assertions(result)
    assert len(result) == 12
    assert hexes.centre not in result

def test_bee_moves_end(m):
    set_state(m, 'wB wa wa wa')
    assert len(m.bee_moves(hexes.centre)) == 2

def test_bee_moves_middle(m):
    set_state(m, 'wB wa wa wa', step=3)
    assert len(m.bee_moves(hexes.centre)) == 4

def test_spider_moves_two(m):
    set_state(m, 'ws wa')
    assert len(m.spider_moves(hexes.centre)) == 1
    assert m.spider_moves(hexes.centre).pop() == hexes.mul(hexes.offsets[0],2)

def test_spider_moves_middle(m):
    set_state(m, 'ws wa', step=3)
    assert len(m.spider_moves(hexes.centre)) == 2
    left, right = m.spider_moves(hexes.centre)
    assert hexes.add(left, right) == hexes.centre

def test_spider_moves_cup_shape(m):
    set_state(m, '- ws', step=1)
    m.remove(hexes.offsets[0])
    assert len(m.spider_moves(hexes.offsets[1])) == 2
    assert len(m.spider_moves(hexes.offsets[-1])) == 2

def test_ant_moves_end(m):
    set_state(m, 'wa bh bh bh')
    assert len(m.ant_moves(hexes.centre)) == 9

def test_ant_moves_middle(m):
    set_state(m, 'wa bh bh', step=3)
    assert len(m.ant_moves(hexes.centre)) == 14

def test_ant_moves_loop(m):
    set_state(m, '- bh', step=1)
    set_state(m, '- wa')
    assert len(m.ant_moves(hexes.offsets[0])) == 11

def test_ant_moves_cup_shape(m):
    set_state(m, '- wa', step=1)
    m.remove(hexes.offsets[0])
    assert len(m.ant_moves(hexes.offsets[1])) == 11
    assert len(m.ant_moves(hexes.offsets[-1])) == 11

def test_hopper_moves_end(m):
    set_state(m, 'wh ba ba ba')
    assert len(m.hopper_moves(hexes.centre)) == 1

def test_hopper_moves_middle(m):
    set_state(m, 'wh ba ba ba', step=3)
    assert len(m.hopper_moves(hexes.centre)) == 2

def test_hopper_spider_moves(m):
    set_state(m, 'wh ba', step=3)
    assert m.hopper_moves(hexes.centre) == m.spider_moves(hexes.centre)

def test_beetle_moves_end(m):
    set_state(m, 'wb ba ba ba')
    assert len(m.beetle_moves(hexes.centre)) == 3

def test_beetle_moves_middle(m):
    set_state(m, 'wb ba ba ba', step=3)
    assert len(m.beetle_moves(hexes.centre)) == 6

def test_beetle_above(m):
    set_state(m, 'wa')
    add_token(m, 'bb')
    assert len(m.beetle_moves(hexes.centre)) == 6

def test_trapped_moves(m):
    set_state(m, 'wB wa', step=1)
    assert len(m.bee_moves(hexes.centre)) == 0
    assert len(m.spider_moves(hexes.centre)) == 0
    assert len(m.ant_moves(hexes.centre)) == 0
    assert len(m.hopper_moves(hexes.centre)) == 6
    assert len(m.beetle_moves(hexes.centre)) == 6

def test_trapped_star_moves(m):
    set_state(m, 'wB wa wa wa', step=2)
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
    set_state(m, 'wB')
    assert moves_helper(m.moves()) == (1,0)

def test_moves_blocked_by_bee(m):
    set_state(m, '- wa')
    assert moves_helper(m.moves()) == (0,0)
    set_state(m, 'bB wa')
    assert moves_helper(m.moves()) == (1,2)
    set_state(m, 'wB wa')
    assert moves_helper(m.moves()) == (2,5)

def test_moves_pairs(m):
    m.colour_bee_placed = lambda x: True
    set_state(m, 'wB bB')
    assert moves_helper(m.moves()) == (2,2)
    set_state(m, 'wB bs')
    assert moves_helper(m.moves()) == (2,3)
    set_state(m, 'wB ba')
    assert moves_helper(m.moves()) == (2,5)
    set_state(m, 'wB bh')
    assert moves_helper(m.moves()) == (2,3)
    set_state(m, 'wB bb')
    assert moves_helper(m.moves()) == (2,3)

    set_state(m, 'ws bs')
    assert moves_helper(m.moves()) == (2,2)
    set_state(m, 'wa ba')
    assert moves_helper(m.moves()) == (2,8)
    set_state(m, 'wh bh')
    assert moves_helper(m.moves()) == (2,2)
    set_state(m, 'wb bb')
    assert moves_helper(m.moves()) == (2,4)

def test_moves_lines(m):
    m.colour_bee_placed = lambda x: True
    set_state(m, 'wB ba ba ba ba bB')
    assert moves_helper(m.moves()) == (2,4)
    set_state(m, 'ws ba ba ba ba bs')
    assert moves_helper(m.moves()) == (2,2)
    set_state(m, 'wa ba ba ba ba ba')
    assert moves_helper(m.moves()) == (2,16)
    set_state(m, 'wh ba ba ba ba bh')
    assert moves_helper(m.moves()) == (2,2)
    set_state(m, 'wb ba ba ba ba bb')
    assert moves_helper(m.moves()) == (2,6)

def test_moves_loops(m):
    m.colour_bee_placed = lambda x: True
    set_state(m, '- wB', step=1)
    assert moves_helper(m.moves()) == (6,6)
    set_state(m, '- ws', step=1)
    assert moves_helper(m.moves()) == (6,6)
    set_state(m, '- wa', step=1)
    assert moves_helper(m.moves()) == (6,12)
    set_state(m, '- wh', step=1)
    assert moves_helper(m.moves()) == (6,6)
    set_state(m, '- wb', step=1)
    assert moves_helper(m.moves()) == (6,12)
