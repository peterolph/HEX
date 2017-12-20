
# all the distance 1 offsets around a hexagon
# in clockwise order starting from the top
centre = (0,0,0)
offsets = ((0,-1,0), (1,-1,0), (1,0,0), (0,1,0), (-1,1,0), (-1,0,0))

def add(hex1,hex2):
    return (hex1[0]+hex2[0], hex1[1]+hex2[1], hex1[2]+hex2[2])

def sub(hex1,hex2):
    return (hex1[0]-hex2[0], hex1[1]-hex2[1], hex1[2]-hex2[2])

# rotate left is anti-clockwise, right is clockwise

left_rotations  = {offsets[i]:offsets[(i-1)%6] for i in range(6)}
right_rotations = {offsets[i]:offsets[(i+1)%6] for i in range(6)}
opposites       = {offsets[i]:offsets[(i+3)%6] for i in range(6)}

def rotate(offset,dir):
    if dir == 'left':
        return left_rotations[offset]
    elif dir == 'right':
        return right_rotations[offset]
    else:
        raise ValueError

def opposite(offset):
    return opposites[offset]

def neighbours(hex):
    return set(add(hex,offset) for offset in offsets)