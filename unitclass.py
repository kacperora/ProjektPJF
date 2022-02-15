class UnitClass:
    def __init__(self, models, weapons=None):
        self.modelsavailable = models
        self.weapons = weapons
        self.amounts = []
        self.models = []

    def __repr__(self):
        output = ''
        for i in self.modelsavailable:
            temp = f'{i}\n'
            temp = temp.translate({ord(c): None for c in '\]\['})
            if temp[0] == '-':
                temp.replace(temp[0], "")
            if temp[-1] == '-':
                temp.replace(temp[-1], "")
            output += temp
        return output

    def printWeapons(self):
        output = ''
        for i in self.weapons:
            output += f'{i}\n'
        return output

    def printUnitsAvailable(self):
        output = []
        for i in self.modelsavailable:
            print(i[0].name + '\n')