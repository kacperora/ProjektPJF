class ModelClass:
    def __init__(self, name, maxw, stats, price, statsdrop=False):
        self.name = name
        self.maxw = maxw
        self.price = price
        self.statsdrop = statsdrop
        if self.statsdrop:
            self.statline = []
            for i in stats:
                self.statline.append(i)
        else:
            self.statline = stats
        self.statsnumb = len(stats)

    def __repr__(self):
        output = f"{self.name}\t {self.price}"
        output = output + '\n' + 'move\tWS\tBS\tS\tT\tW\tA\tLd\tSv'
        output += '\n'
        for i in self.statline:
            output += f'\n{i}'
        # print(output)
        return output

    def __str__(self):
        output = f"{self.name}\t {self.price}"
        output = output + '\n' + 'move\tWS\tBS\tS\tT\tW\tA\tLd\tSv'
        output += '\n'
        for i in self.statline:
            output += f'\n{i}'
        return output
