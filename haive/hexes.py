
# An implementation of a flat-topped axial hexagonal coordinate grid.
# Thanks due to https://www.redblobgames.com
# A single hex is a 3-tuple, a group of hexes is a set
# Also includes the concept of up/down to model stacks of hexes

from haive import ring

centre = (0,0,0)

# All the distance 1 offsets around a hexagon in clockwise order starting from the top.
offsets = ring.Ring(((0,-1,0), (1,-1,0), (1,0,0), (0,1,0), (-1,1,0), (-1,0,0)))

up = (0,0,1)
down = (0,0,-1)

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
def rotate(dir,hex,pivot=centre):
    offset = sub(hex,pivot)
    if offset not in offsets:
        raise ValueError
    if dir == left:
        return add(left_rotations[offset],pivot)
    elif dir == right:
        return add(right_rotations[offset],pivot)
    else:
        raise ValueError

# The opposite is 3 steps around (in either direction).
opposites = {offsets[i]:offsets[i+3] for i in range(6)}
def opposite(offset):
    return opposites[offset]

def neighbours(hex):
    return set(add(hex,offset) for offset in offsets)

def is_active(hex):
    return hex[2] == 0

def merge(sets_of_hexes):
    return set().union(*sets_of_hexes)

def save(hex):
    return "%d,%d,%d" % hex

def load(string):
    return tuple(int(c) for c in string.split(','))
