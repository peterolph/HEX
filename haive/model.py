
# This is a model of a Hive game.
# It stores the current position of tokens in play and supplies available moves for both players.

from collections import namedtuple
from haive import hexes, ring

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
    def occupied_neighbours(self, hex):
        return hexes.neighbours(hex) & self.active_hexes()

    # Find the hexes that can have tokens moved out of them without splitting the hive.
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
            for neighbour in self.occupied_neighbours(hex):
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

    # Find the destinations a bee could move to from a given source
    # Conditions:
    #   one step away along a grid axis
    #   not already occupied
    #   two hexes are adjacent to source and destination, exactly one must be occupied
    def bee_destinations(self, hex):
        neighbours = ring.Ring(hexes.add(hex,offset) for offset in hexes.offsets)
        occupied = ring.Ring(neighbour in self.state for neighbour in neighbours)
        valid_directions = [(not occupied[i] and (occupied[i+1] != occupied[i-1])) for i in range(6)]
        return set(neighbours[i] for i in range(6) if valid_directions[i])

    # Get the opposite colour
    def colour_opposite(self, colour):
        return {white:black, black:white}[colour]

    # Get the hexes occupied by tokens of a given colour.
    def colour_hexes(self, colour):
        return set(hex for hex in self.active_hexes() if self.state[hex].colour == colour)

    # Get hexes neighbouring tokens of a given colour.
    def colour_neighbours(self, colour):
        return hexes.merge(hexes.neighbours(hex) for hex in self.colour_hexes(colour))

    # Find the hexes that are valid for a new token of a given colour.
    # Conditions:
    #   adjacent to a token of the same colour
    #   not adjacent to any tokens of the opposite colour
    #   not already occupied
    # Special cases:
    #   the first token does not need to touch anything
    #   the second token can touch the first, regardless of colour
    def places(self, colour):
        if len(self.state) == 0:
            return set(hexes.centre,)
        elif len(self.state) == 1:
            return hexes.neighbours(hexes.centre)
        else:
            return self.colour_neighbours(colour) - self.colour_neighbours(self.colour_opposite(colour)) - set(self.state)
