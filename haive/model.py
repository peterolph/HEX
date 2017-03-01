
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

    def initialise_tokens(self):
        counter = itertools.count(0)
        return {types.Token(id=next(counter), colour=colour, kind=kind): None
                for colour in self.colours
                for kind in self.starting_kinds}

    def __str__(self):
        return '\n'.join("%s: %s" % (token, self.tokens[token]) for token in sorted(self.tokens,key=lambda token: token.id))

if __name__ == '__main__':
    m = Model()
    print(m)