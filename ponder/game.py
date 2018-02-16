# -*- coding: UTF-8 -*-

# An interactive wrapper for the model

from ponder.model import black

class Game(object):
    def __init__(self, model, players):
        self.model = model
        self.active_player = black
        self.players = players

    def make_move(self, move):
        if move is None:
            pass
        elif (
            move.token is not None and
            move.source is None and
            move.token.colour == self.active_player and
            move.token.kind in self.model.colour_hand(self.active_player) and
            move.destination in self.model.colour_places(self.active_player)):
            self.model.add(move.token, move.destination)
        elif (
            move.token is None and
            move.source is not None and
            move.source in self.model.colour_hexes(self.active_player) & self.model.move_sources() and
            move.destination in self.model.colour_moves(self.active_player)[move.source]):
            self.model.move(move.source, move.destination)
        else:
            raise ValueError

    def play(self):
        while self.model.winner() is None:
            self.make_move(self.players[self.active_player].choose_move(self.model, self.active_player))
            self.active_player = self.model.colour_opposite(self.active_player)
        return self.model.winner()

    

