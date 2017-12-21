
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
