
import collections

class Token(collections.namedtuple('Token',['id','colour','kind'])):
    def __str__(self):
        return "%d: %s %s" % (self.id, self.colour, self.kind)

    def short_string(self):
        return "%s%s" % (self.colour[0], self.kind[0])