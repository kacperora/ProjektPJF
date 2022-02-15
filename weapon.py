import re


class Weapon:
    d = 0

    def __init__(self, name, range, shots, type, s, ap, D):
        self.name = name
        self.range = range
        self.type = type
        self.shots = shots
        self.s = s
        self.ap = ap
        self.d = D

    def getDmg(self):
        if isinstance(self.d, int):
            return self.d
        else:
            a = map(int, re.findall(r'\d+', self.d))
            # if
            # sum = a[0]*random.randint(1,a[1])

    def __repr__(self):
        return f'{self.name}\t{self.range}\t{self.type}\t{self.shots}\t{self.s}\t{self.ap}\t{self.d}'

    def __str__(self):
        return f'{self.name}\t{self.range}\t{self.type}\t{self.shots}\t{self.s}\t{self.ap}\t{self.d}'
    
    def summary(self):
        return f'{self.name} {self.range} {self.type} {self.shots} {self.s} {self.ap} {self.d}'