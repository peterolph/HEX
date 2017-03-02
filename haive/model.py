
import itertools

from haive import hexes, types

class Model(object):

    white = 'white'
    black = 'black'
    colours = (white, black)

    bee = 'Bee'
    hopper = 'hopper'
    ant = 'ant'
    beetle = 'beetle'
    spider = 'spider'
    kinds = (bee, hopper, ant, beetle, spider)
    starting_kinds = (bee, hopper, hopper, hopper, ant, ant, ant, beetle, beetle, spider, spider)

    def __init__(self):
        self.tokens = self.initialise_tokens()

        self.reverse = {}
        self.cut_tokens = set()

    def initialise_tokens(self):
        counter = itertools.count(0)
        return {types.Token(id=next(counter), colour=colour, kind=kind): None
                for colour in self.colours
                for kind in self.starting_kinds}

    def add(self, token, loc):
        self.tokens[token] = loc
        assert loc not in self.reverse
        self.reverse[loc] = token

    def remove(self, token):
        if self.tokens[token] is not None:
            del self.reverse[self.tokens[token]]
        self.tokens[token] = None

    def update(self, token, loc):
        self.remove(token)
        self.add(token, loc)

    def move(self,token, destination):
        source = self.tokens[token]
        self.remove(token)

        if token in self.reverse:
            self.update(self.reverse[token], source)
        if destination in self.reverse:
            self.update(self.reverse[destination], token)

        self.add(token, destination)
        self.update_cut_tokens()

    def occupied_neighbour_hexes(self, hex):
        return set(neighbour for neighbour in hexes.neighbours(hex) if neighbour in self.reverse)

    def update_cut_tokens(self):
        active_hexes = list(self.tokens[token] for token in self.tokens if type(self.tokens[token]) == tuple)

        discovery = {hex:0 for hex in active_hexes}
        low = {hex:1000 for hex in active_hexes}
        visited = {hex:False for hex in active_hexes}
        parent = {hex:None for hex in active_hexes}

        cut_hexes = {hex:False for hex in active_hexes}

        def depth_first_search(hex, depth=0):
            visited[hex] = True
            discovery[hex] = low[hex] = depth
            child_count = 0
            for neighbour in self.occupied_neighbour_hexes(hex):
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

        depth_first_search(active_hexes[0])
        self.cut_tokens = set([self.reverse[hex]
                               for hex in cut_hexes
                               if cut_hexes[hex] == True])

    def trapped(self, token):
        return type(self.tokens[token]) == types.Token or token in self.cut_tokens

    def __str__(self):
        return '\n'.join("%s: %s" % (token, self.tokens[token]) for token in sorted(self.tokens,key=lambda token: token.id))

if __name__ == '__main__':
    m = Model()
    print(m)
