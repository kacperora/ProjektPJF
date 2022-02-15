import random


def resolveRoll(input, takeavg=False):
    number = 0
    if isinstance(input, int):
        return input
    if len(input.split('+')) == 2:
        b = int(input.split('+')[1])
    else:
        b = 0
    if len(input.split('D')) == 2:
        if input.split('D')[0] == '':
            a = 1
        else:
            a = int(input.split('D')[0])
        for i in range(a):
            if takeavg:
                number += (1 + int(input.split('D')[1])) / 2
            else:
                number += random.randint(1, int(input.split('D')[1]))
    number += b
    if 'D' not in input:
        number = input
    return int(number)


def meleeStrength(weaponstr, modelstr):
    if 'User' in weaponstr:
        return int(modelstr)
    if '+' in weaponstr:
        return int(modelstr) + int(weaponstr.split('+')[1])
    if 'x' in weaponstr:
        return int(modelstr) * int(weaponstr.split('x')[1])
