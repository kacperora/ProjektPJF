import random


class Model:
    def __init__(self, type):
        self.type = type
        self.weapons = []
        self.wounds = int(type.maxw)
        self.destroyed = False
        self.statsnumb = 0
        self.currentstats = type.statline[self.statsnumb]

    def takeDMG(self, amount):
        self.wounds -= amount
        if self.wounds <= 0:
            self.destroyed = True
            self.wounds = 0
        elif self.wounds < int(self.currentstats.minw):
            self.statsnumb += 1
            self.currentstats = self.type.statline[self.statsnumb]

    def restoreDMG(self, amount):
        self.wounds += amount
        if self.wounds > self.type.maxw:
            self.wounds = self.type.maxw
        while self.wounds >= self.currentstats.maxw:
            self.statsnumb += 1
            self.currentstats = self.type.statline[self.statsnumb]

    def tryWound(self, S, modifiers, reroll='none'):
        T = self.currentstats.t
        if 2 * T < S:
            target = 2
        elif T < S:
            target = 3
        elif T == S:
            target = 4
        elif T > S:
            target = 5
        elif T > 2 * S:
            target = 6
        else:
            target = 6
        roll = random.randrange(1, 7)
        if roll == 1 and reroll == '1s':
            roll = random.randrange(1, 7)
            if roll + modifiers >= target:
                return True
            else:
                return False
        if roll + modifiers >= target:
            return True
        else:
            roll = random.randrange(1, 7)
            if roll + modifiers >= target:
                return True
            return False

    def tryShoot(self, modifiers, reroll='none'):
        roll = random.randrange(1, 7)
        if roll == 1 and reroll == '1s':
            roll = random.randrange(1, 7)
            if roll + modifiers >= int(self.currentstats.bs) or roll == 6 and roll != 1:
                return True
            else:
                return False
        if roll + modifiers >= int(self.currentstats.bs) or roll == 6 and roll != 1:
            return True
        else:
            roll = random.randrange(1, 7)
            if roll + modifiers >= int(self.currentstats.bs) or roll == 6 and roll != 1:
                return True
            return False

    def tryMelee(self, modifiers, reroll='none'):
        roll = random.randrange(1, 7)
        if roll == 1 and reroll == '1s':
            roll = random.randrange(1, 7)
            if roll + modifiers >= int(self.currentstats.ws) or roll == 6 and roll != 1:
                return True
            else:
                return False
        if roll + modifiers >= int(self.currentstats.ws) or roll == 6 and roll != 1:
            return True
        else:
            roll = random.randrange(1, 7)
            if roll + modifiers >= int(self.currentstats.ws) or roll == 6 and roll != 1:
                return True
            return False

    def tryArmor(self, ap, reroll='none'):
        roll = random.randrange(1, 7)
        if roll == 1 and reroll == '1s':
            roll = random.randrange(1, 7)
            if roll >= int(self.currentstats.bs) + ap or roll == 6 and roll != 1:
                return False
            else:
                return True
        if roll >= int(self.currentstats.bs) + ap or roll == 6 and roll != 1:
            return False
        else:
            roll = random.randrange(1, 7)
            if roll >= int(self.currentstats.bs) + ap or roll == 6 and roll != 1:
                return False
            return True

    def summary(self):
        # return f'{self.move}"\t{self.ws}+' \
        # f'\t{self.bs}+\t{self.s}\t{self.t}\t{self.wounds}/{self.maxw}\t{self.a}\t{self.ld}\t{self.sv}+'
        pass
