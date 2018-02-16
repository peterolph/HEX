
from ponder.tuples import Move, Token
from ponder.model import kinds, black, white, bee, ant, spider, hopper, beetle

def tuple_from_string(string):
    tuple2 = tuple(int(item) for item in string.split(','))
    assert len(tuple2) == 2
    return tuple2 + (0,)

def token_to_short_string(token):
    return token.colour[0] + token.kind[0]

class UI(object):

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

    def choose_move(self, m, active_player):
        print(self.render_model(m))
        while True:
            try:
                unknown_input = input("Pick a token for "+active_player+": ")
                token = source = None
                if unknown_input in kinds:
                    token = Token(colour=active_player, kind=unknown_input)
                    print(self.render_model(m, m.colour_places(active_player)))
                else:
                    source = tuple_from_string(unknown_input)
                    print(self.render_model(m, m.colour_moves(active_player)[source]))

                destination = tuple_from_string(input("Pick a location: "))
                return Move(token=token, source=source, destination=destination)
            except (AssertionError, ValueError):
                print("Try again")

    def render_token(self, token):
        colour_codes = {white: '97', black:'30'}
        kind_codes = {bee: '33', ant: '34', spider: '38;5;94', hopper: '32', beetle: '35'}
        return self.render_text('◖', colour_codes[token.colour]) + self.render_text('◗', kind_codes[token.kind])

    def render_model(self, m, highlight_hexes=set()):
        if len(m.state) > 0:
            minx = min(hex[0] for hex in m.state)
            maxx = max(hex[0] for hex in m.state)
            miny = min(hex[0]+2*hex[1] for hex in m.state)
            maxy = max(hex[0]+2*hex[1] for hex in m.state)
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
                    if hex in m.state:
                        row.append(self.render_token(m.state[hex]))
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
        copy = m.state.copy()
        m.state = {}
        for i,colour in enumerate(colours):
            for j, kind in enumerate(kinds):
                m.add(Token(colour=colour, kind=kind), (j,i,0))
        print(self.render_model(m.colour_moves(black)[(1,1,0)]))
        m.state = copy

if __name__ == '__main__':

    from ponder import ai, game, model

    winner = game.Game(model.Model(), {black:UI(), white:ai.AI()}).play()
    print(winner, "won!")