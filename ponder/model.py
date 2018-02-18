
# A model of a Hive game.
# It stores the current position of tokens in play and supplies available moves for both players.

from contextlib import contextmanager

from ponder import hexes, ring
from ponder.tuples import Token, CrawlMoves

white = 'white'
black = 'black'
colours = (white, black)

bee = 'Bee'
hopper = 'hopper'
ant = 'ant'
beetle = 'beetle'
spider = 'spider'
kinds = (bee, hopper, ant, beetle, spider)
starting_hand = {bee: 1, hopper: 3, ant: 3, beetle:2, spider: 2}

class Model(object):

    def __init__(self):
        self.state = {}

    def save(self):
        return '|'.join(':'.join((hexes.save(loc),*self.state[loc])) for loc in sorted(self.state.keys()))

    def load(self, state):
        for item in state.split('|'):
            loc, colour, kind = item.split(':')
            self.state[hexes.load(loc)] = Token(colour, kind)

    def add(self, token, hex):
        if hex in self.state:
            self.move(hex, hexes.add(hex, hexes.down))
        self.state[hex] = token

    def remove(self, hex):
        remove = self.state[hex]
        del self.state[hex]
        if hexes.add(hex, hexes.down) in self.state:
            self.move(hexes.add(hex, hexes.down), hex)
        return remove

    @contextmanager
    def temporarily_remove(self, hex):
        token = self.remove(hex)
        yield
        self.add(token, hex)

    def move(self, source, destination):
        token = self.remove(source)
        self.add(token, destination)

    # Get the hexes on the top of the hive ie. not covered by another hex.
    def active_hexes(self):
        return set(hex for hex in self.state.keys() if hexes.is_active(hex))

    # Get the occupied hexes which neighbour this one.
    def occupied_neighbours(self, hex):
        return hexes.neighbours(hex) & self.active_hexes()

    # Get the unoccupied hexes which neighbour this one.
    def unoccupied_neighbours(self, hex):
        return hexes.neighbours(hex) - self.active_hexes()

    # Get the unoccupied hexes which neighbour this one but no others
    def unique_unoccupied_neighbours(self, hex):
        assert hex in self.state
        return set(neighbour for neighbour in self.unoccupied_neighbours(hex)
            if len(self.occupied_neighbours(neighbour)) == 1)

    def winner(self):
        for colour in colours:
            colour_bee = self.colour_hexes(colour) & self.kind_hexes(bee)
            if len(colour_bee) > 0:
                active_hex = hexes.make_active(tuple(colour_bee)[0])
                if len(self.occupied_neighbours(active_hex)) == 6:
                    return self.colour_opposite(colour)
        return None

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

    def crawl_moves(self, hex):
        crawl_moves = CrawlMoves(set(), set())
        occupied = self.occupied_neighbours(hex)
        unoccupied = self.unoccupied_neighbours(hex)
        for destination in unoccupied:
            if hexes.rotate(hexes.left, destination, hex) in occupied and hexes.rotate(hexes.right, destination, hex) in unoccupied:
                crawl_moves.left.add(destination)
            if hexes.rotate(hexes.right, destination, hex) in occupied and hexes.rotate(hexes.left, destination, hex) in unoccupied:
                crawl_moves.right.add(destination)
        return crawl_moves

    def crawl_graph(self, crawl_hex):
        graph = {}
        crawl_moves = self.crawl_moves(crawl_hex)
        open_set = crawl_moves.left|crawl_moves.right
        with self.temporarily_remove(crawl_hex):
            while len(open_set) > 0:
                current = open_set.pop()
                graph[current] = self.crawl_moves(current)
                for hex in graph[current].left:
                    if hex not in graph and hex not in open_set:
                        open_set.add(hex)
        return graph

    def bee_moves(self, hex):
        return hexes.merge(self.crawl_moves(hex))

    def spider_moves(self, hex):
        spider_moves = self.crawl_moves(hex)
        graph = self.crawl_graph(hex)
        for _ in range(2):
            spider_moves = CrawlMoves(
                left=hexes.merge(graph[hex].left for hex in spider_moves.left),
                right=hexes.merge(graph[hex].right for hex in spider_moves.right))
        return hexes.merge(spider_moves)

    def ant_moves(self, hex):
        ant_moves = hexes.merge(self.crawl_moves(hex))
        open_set = self.crawl_moves(hex).left
        graph = self.crawl_graph(hex)
        while len(open_set) > 0:
            current = open_set.pop()
            ant_moves.add(current)
            for hex in graph[current].left:
                if hex not in ant_moves and hex not in open_set:
                    open_set.add(hex)
        return ant_moves

    def hopper_moves(self, hex):
        hopper_moves = set()
        for offset in hexes.offsets:
            destination = hexes.add(hex, offset)
            if destination in self.state:
                while destination in self.state:
                    destination = hexes.add(destination, offset)
                hopper_moves.add(destination)
        return hopper_moves

    def beetle_moves(self, hex):
        return hexes.merge(self.crawl_moves(hex)) | self.occupied_neighbours(hex)

    move_lookup = {bee:    bee_moves,
                   spider: spider_moves,
                   ant:    ant_moves,
                   hopper: hopper_moves,
                   beetle: beetle_moves}

    def colour_moves(self, colour):
        if self.colour_bee_placed(colour):
            return {source: self.move_lookup[self.state[source].kind](self,source) for source in self.move_sources() & self.colour_hexes(colour)}
        else:
            return {}

    def moves(self):
        return {colour: self.colour_moves(colour) for colour in colours}

    # Get the opposite colour
    def colour_opposite(self, colour):
        return {white:black, black:white}[colour]

    # Get the hexes occupied by tokens of a given colour.
    def colour_hexes(self, colour):
        return set(hex for hex in self.state if self.state[hex].colour == colour)

    # Get the hexes occupied by tokens of a given kind.
    def kind_hexes(self, *kinds):
        return set(hex for hex in self.state if self.state[hex].kind in kinds)

    # Get hexes neighbouring tokens of a given colour.
    def colour_neighbours(self, colour):
        return hexes.merge(hexes.neighbours(hex) for hex in self.colour_hexes(colour))

    def colour_bee_placed(self, colour):
        return len(self.colour_hexes(colour) & self.kind_hexes(bee)) > 0

    # Find the hexes that are valid for a new token of a given colour.
    # Conditions:
    #   adjacent to a token of the same colour
    #   not adjacent to any tokens of the opposite colour
    #   not already occupied
    # Special cases:
    #   the first token does not need to touch anything
    #   the second token can touch the first, regardless of colour
    def colour_places(self, colour):
        if len(self.state) == 0:
            return set([hexes.centre,])
        elif len(self.state) == 1:
            return hexes.neighbours(hexes.centre)
        else:
            return self.colour_neighbours(colour) - self.colour_neighbours(self.colour_opposite(colour)) - set(self.state)

    def places(self):
        return {colour: self.colour_places(colour) for colour in colours}

    def colour_hand(self, colour):
        if len(self.colour_hexes(colour)) >= 3 and not self.colour_bee_placed(colour):
            return [bee]
        else:
            return [kind for kind in kinds if len(self.colour_hexes(colour) & self.kind_hexes(kind)) < starting_hand[kind]]
