class statline:
    def __init__(self, ws, bs, s, t, maxw, minw, a, ld, sv, move):
        self.move = move
        self.ws = int(ws)
        if bs != '-':
            self.bs = int(bs)
        else:
            self.bs = 0
        self.s = int(s)
        self.t = int(t)
        self.maxw = int(maxw)
        self.minw = int(minw)
        self.a = a
        self.ld = int(ld)
        if self.ld > 10: self.ld %= 10
        self.sv = int(sv)

    def __repr__(self):
        return f'{self.move}"\t{self.ws}+' \
               f'\t{self.bs}+\t{self.s}\t{self.t}\t{self.minw}-{self.maxw}\t{self.a}\t{self.ld}\t{self.sv}+'

    def __str__(self):
        return f'{self.move}"\t{self.ws}+' \
               f'\t{self.bs}+\t{self.s}\t{self.t}\t{self.minw}-{self.maxw}\t{self.a}\t{self.ld}\t{self.sv}+'