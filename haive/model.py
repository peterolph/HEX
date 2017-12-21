
# This is a model of a Hive game.
# It stores the current position of tokens in play and supplies available moves for both players.

from collections import namedtuple
from haive import hexes

Token = namedtuple('Token', ['colour', 'kind'])

white = 'white'
black = 'black'
colours = (white, black)

bee = 'Bee'
hopper = 'hopper'
ant = 'ant'
beetle = 'beetle'
spider = 'spider'
kinds = (bee, hopper, ant, beetle, spider)
hand = (bee, hopper, hopper, hopper, ant, ant, ant, beetle, beetle, spider, spider)

class Model(object):

    def __init__(self):
        self.state = {}

    def assert_consistent(self):
        return True

    def save(self):
        return '|'.join(':'.join((hexes.save(loc),*self.state[loc])) for loc in sorted(self.state.keys()))

    def load(self, state):
        for item in state.split('|'):
            loc, colour, kind = item.split(':')
            self.state[hexes.load(loc)] = Token(colour, kind)

    # Get the hexes on the top of the hive ie. not covered by another hex.
    def active_hexes(self):
        return set(hex for hex in self.state.keys() if hex[2] == 0)

    # Get the occupied hexes which neighbour this one.
    def neighbours(self, hex):
        return hexes.neighbours(hex) & self.active_hexes()

    # Find which hexes can have tokens moved out of them without splitting the hive.
    # Imagine the board as a graph and use Tarjan's algorithm to find the hexes that are NOT cut vertices.
    # https://en.wikipedia.org/wiki/Biconnected_component
    def move_sources(self):
        active_hexes = list(self.active_hexes())

        discovery = {hex:0 for hex in active_hexes}
        low = {hex:9999 for hex in active_hexes}
        visited = {hex:False for hex in active_hexes}
        parent = {hex:None for hex in active_hexes}

        cut_hexes = {hex:False for hex in active_hexes}

        def depth_first_search(hex, depth=0):
            visited[hex] = True
            discovery[hex] = low[hex] = depth
            child_count = 0
            for neighbour in self.neighbours(hex):
                if visited[neighbour] == False:
                    child_count += 1
                    parent[neighbour] = hex
                    depth_first_search(neighbour, depth+1)
                    low[hex] = min(low[hex], low[neighbour])
                    if parent[hex] is None and child_count > 1:
                        cut_hexes[hex] = True
                    if parent[hex] is not None and low[neighbour] >= discovery[hex]:
                        cut_hexes[hex] = True
                elif parent[hex] != neighbour:
                    low[hex] = min(low[hex], discovery[neighbour])

        if len(active_hexes) > 0:
            depth_first_search(active_hexes[0])
        return set(hex for hex in cut_hexes if cut_hexes[hex] == False)