# -*- coding: UTF-8 -*-

# An interactive wrapper for the model

from ponder import model, ai
from ponder.tuples import Move

def tuple_from_string(string):
    tuple2 = tuple(int(item) for item in string.split(','))
    assert len(tuple2) == 2
    return tuple2 + (0,)

def token_to_short_string(token):
    return token.colour[0] + token.kind[0]

humanplayer = 'human'
aiplayer = 'ai'
player_types = (humanplayer, aiplayer)

class Game(object):
    def __init__(self, m, players, ai=None):
        self.m = m
        self.ai = ai
        self.active_player = model.black
        self.players = players

    def make_move(self, move):
        if (
            move.token is not None and
            move.source is None and
            move.token.colour == self.active_player and
            move.token.kind in self.m.colour_hand(self.active_player) and
            move.destination in self.m.colour_places(self.active_player)):
            self.m.add(move.token, move.destination)
        elif (
            move.token is None and
            move.source is not None and
            move.source in self.m.colour_hexes(self.active_player) & self.m.move_sources() and
            move.destination in self.m.colour_moves(self.active_player)[move.source]):
            self.m.move(move.source, move.destination)
        else:
            raise ValueError
        print(self.active_player,'played',move)

    def human_move(self):
        print(self.render_model())
        while True:
            try:
                unknown_input = input("Pick a token for "+self.active_player+": ")
                token = source = None
                if unknown_input in model.kinds:
                    token = model.Token(colour=self.active_player, kind=unknown_input)
                    print(self.render_model(self.m.colour_places(self.active_player)))
                else:
                    source = tuple_from_string(unknown_input)
                    print(self.render_model(self.m.colour_moves(self.active_player)[source]))

                destination = tuple_from_string(input("Pick a location: "))
                self.make_move(Move(token=token, source=source, destination=destination))
                break
            except (AssertionError, ValueError):
                print("Try again")

    def ai_move(self):
        print(self.render_model())
        self.make_move(self.ai.choose_move(self.m, self.active_player))

    def play(self):
        while self.m.winner() is None:
            if self.players[self.active_player] == humanplayer:
                self.human_move()
            elif self.players[self.active_player] == aiplayer:
                self.ai_move()
            else:
                raise ValueError
            self.active_player = self.m.colour_opposite(self.active_player)
        return self.m.winner()

    def render_text(self, text, *codes, bold=False, dim=False):
        reset_code = '0'
        bold_code = '1'
        dim_code = '2'
        code_template = '\033[%sm'

        codes = list(codes)
        if bold:
            codes.append(bold_code)
        if dim:
            codes.append(dim_code)
        code_string = ';'.join(codes)

        return (code_template%code_string) + text + (code_template%reset_code)

    def render_token(self, token):
        colour_codes = {model.white: '97', model.black:'30'}
        kind_codes = {model.bee: '33', model.ant: '34', model.spider: '38;5;94', model.hopper: '32', model.beetle: '35'}
        return self.render_text('◖', colour_codes[token.colour]) + self.render_text('◗', kind_codes[token.kind])

    def render_model(self, highlight_hexes=set()):
        if len(self.m.state) > 0:
            minx = min(hex[0] for hex in self.m.state)
            maxx = max(hex[0] for hex in self.m.state)
            miny = min(hex[0]+2*hex[1] for hex in self.m.state)
            maxy = max(hex[0]+2*hex[1] for hex in self.m.state)
        else:
            minx = maxx = miny = maxy = 0
        padding = 2
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
                        row.append(self.render_token(self.m.state[hex]))
                    elif hex in highlight_hexes:
                        row.append(self.render_text('><', '96'))
                    else:
                        row.append(self.render_text('--', dim=True))
                else:
                    row.append('  ')
            row.append(sider[y-miny])
            rows.append(' '.join(row))
        body = '\n'.join(rows)

        return '\n' + header + '\n' + body + '\n' + footer + '\n'

    def render_test(self):
        copy = self.m.state.copy()
        self.m.state = {}
        for i,colour in enumerate(model.colours):
            for j, kind in enumerate(model.kinds):
                self.m.add(model.Token(colour=colour, kind=kind), (j,i,0))
        print(self.render_model(self.m.colour_moves(model.black)[(1,1,0)]))
        self.m.state = copy

if __name__ == '__main__':
    game = Game(model.Model(), {model.black:humanplayer, model.white:aiplayer}, ai = ai.AI())
    winner = game.play()
    print(winner, "won!")