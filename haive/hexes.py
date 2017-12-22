
# This is an implementation of a flat-topped axial hexagonal coordinate grid.
# Thanks due to https://www.redblobgames.com
# A single hex is a 3-tuple, a group of hexes is a set

from haive import ring

centre = (0,0,0)

# All the distance 1 offsets around a hexagon in clockwise order starting from the top.
offsets = ring.Ring(((0,-1,0), (1,-1,0), (1,0,0), (0,1,0), (-1,1,0), (-1,0,0)))

def add(hex1,hex2):
    return (hex1[0]+hex2[0], hex1[1]+hex2[1], hex1[2]+hex2[2])

def sub(hex1,hex2):
    return (hex1[0]-hex2[0], hex1[1]-hex2[1], hex1[2]-hex2[2])

def mul(hex, f):
    return (hex[0]*f, hex[1]*f, hex[2]*f)

# Left rotation is anti-clockwise, right is clockwise. Like a screwdriver: righty tighty, lefty loosey.
left_rotations  = {offsets[i]:offsets[i-1] for i in range(6)}
right_rotations = {offsets[i]:offsets[i+1] for i in range(6)}
left = 'LEFT'
right = 'RIGHT'
def rotate(offset,dir):
    if dir == left:
        return left_rotations[offset]
    elif dir == right:
        return right_rotations[offset]
    else:
        raise ValueError

# The opposite is 3 steps around (in either direction).
opposites = {offsets[i]:offsets[i+3] for i in range(6)}
def opposite(offset):
    return opposites[offset]

def neighbours(hex):
    return set(add(hex,offset) for offset in offsets)

def merge(sets_of_hexes):
    return set().union(*sets_of_hexes)

def save(hex):
    return "%d,%d,%d" % hex

def load(string):
    return tuple(int(c) for c in string.split(','))
