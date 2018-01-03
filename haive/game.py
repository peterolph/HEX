
# An interactive wrapper for the model

from haive import model
from collections import namedtuple

def tuple_from_string(string):
    tuple2 = tuple(int(item) for item in string.split(','))
    assert len(tuple2) == 2
    return tuple2 + (0,)

def token_to_short_string(token):
    return token.colour[0] + token.kind[0]

human = 'human'
ai = 'ai'
player_types = (human, ai)

Move = namedtuple('Move', ('token','source','destination'))

class Game(object):
    def __init__(self, m, players, ai=None):
        self.m = m
        self.ai = ai
        self.active_player = model.black
        self.players = players

    def make_move(self, move):
        if move.token is not None:
            self.m.add(move.token, move.destination)
        elif move.source is not None:
            self.m.move(move.source, move.destination)
        else:
            raise ValueError

    def human_move(self):
        print(self.render_model())
        while True:
            try:
                source, destination = input("Enter a move for "+self.active_player+": ").split(" ")
                if source in model.kinds:
                    human_move = Move(token=model.Token(colour=self.active_player, kind=source), source=None, destination=tuple_from_string(destination))
                else:
                    human_move = Move(token=None, source=tuple_from_string(source), destination=tuple_from_string(destination))
                break
            except (AssertionError, ValueError):
                print("Try again")
        self.make_move(human_move)

    def ai_move(self):
        self.make_move(self.ai.choose_move(self.m, self.active_player))

    def play(self):
        while self.m.winner() is None:
            if self.players[self.active_player] == human:
                self.human_move()
            elif self.players[self.active_player] == ai:
                self.ai_move()
            else:
                raise ValueError
            self.active_player = self.m.colour_opposite(self.active_player)
        return self.m.winner()

    def render_model(self):
        if len(self.m.state) > 0:
            minx = min(hex[0] for hex in self.m.state)
            maxx = max(hex[0] for hex in self.m.state)
            miny = min(hex[0]+2*hex[1] for hex in self.m.state)
            maxy = max(hex[0]+2*hex[1] for hex in self.m.state)
        else:
            minx = maxx = miny = maxy = 0
        padding = 1
        minx -= padding
        maxx += padding
        miny -= padding
        maxy += padding

        # don't touch the magic indices
        i_range = ['%2d'%x for x in range(minx, maxx+1)]
        j_range = [y%2==0 and '%2d'%(y/2) or '  ' for y in range(miny-maxx-1, maxy-minx+2)]

        header = ' '.join(i_range)
        sider = j_range[:maxy-miny+1]
        footer = ' '.join(reversed(j_range[maxy-miny+1:]))

        rows = []
        for y in range(miny,maxy+1):
            row = []
            for x in range(minx,maxx+1):
                if (y-x)%2==0:
                    hex = (x,(y-x)/2,0)
                    if hex in self.m.state:
                        row.append(token_to_short_string(self.m.state[hex]))
                    else:
                        row.append('--')
                else:
                    row.append('  ')
            row.append(sider[y-miny])
            rows.append(' '.join(row))
        body = '\n'.join(rows)

        return '\n' + header + '\n' + body + '\n' + footer + '\n'

if __name__ == '__main__':
    game = Game(model.Model(), {model.black:human, model.white:human})
    winner = game.play()
    print(winner, "won!")