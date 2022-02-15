from model import Model


class Player:
    """
    Class with player data
    """

    def __init__(self, name):
        self.name = name
        self.unitcount = 0
        self.unitdead = 0
        self.units = None
        self.state = 'selection'
        self.models = []
        self.has_charged = False
        self.has_moved = False
        self.has_advanced = False
        self.has_shot = False
        self.points_lost = 0
        return

    def setModels(self, amounts):
        a = 0
        for i in self.units.modelsavailable:
            for x in range(int(amounts[a])):
                model = Model(i[0])
                model.weapons = [[0]] * len(self.units.weapons)
                self.models.append(model)
                a += 1
        self.unitcount = a
        return

    def __str__(self):
        return self.name
