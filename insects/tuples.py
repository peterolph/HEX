
from collections import namedtuple

Move = namedtuple('Move', ('token','source','destination'))
Token = namedtuple('Token', ['colour', 'kind'])
CrawlMoves = namedtuple('CrawlMoves', ['left', 'right'])