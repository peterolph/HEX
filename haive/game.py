
# An interactive wrapper for the model

from haive import model
from collections import namedtuple

def tuple_from_string(string):
    return tuple(int(item) for item in string.split(','))

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
        source, destination = input("Please enter a move for "+self.active_player+": ").split(" ")
        if source in model.kinds:
            human_move = Move(token=model.Token(colour=self.active_player, kind=source), source=None, destination=tuple_from_string(destination))
        else:
            human_move = Move(token=None, source=tuple_from_string(source), destination=tuple_from_string(destination))
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
        print(self.m.state)

if __name__ == '__main__':
    game = Game(model.Model(), {model.black:human, model.white:human})
    winner = game.play()
    print(winner, "won!")