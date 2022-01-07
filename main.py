# This is a sample Python script.


from urllib.request import urlopen
import html
import re
import pandas as pd
import random
from bs4 import BeautifulSoup

class statline:
    def __init__(self, ws, bs, s, t, maxw, minw, a, ld, sv, move):
        self.move = move
        self.ws = ws
        self.bs = bs
        self.s = s
        self.t = t
        self.maxw = maxw
        self.minw = minw
        self.a = a
        self.ld = ld
        self.sv = sv
    def __repr__(self):
        return f'{self.move}" {self.ws}+ {self.bs}+ {self.s} {self.t} {self.minw}-{self.maxw} {self.a} {self.ld} {self.sv}+'

class UnitClass:
    def __init__(self, name, maxw, stats,price, statsdrop = False ):
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



    def hitMelee(self, modifier):
        roll = random.randint(1,6)
        target = self.ws[0]
        if roll + modifier >= target | roll == 6:
            return True
        if roll == 1:
            return False
        return False

    def hitRange(self, modifier):
        roll = random.randint(1,6)
        target = self.bs[0]
        if roll + modifier >= target | roll == 6:
            return True
        if roll == 1:
            return False
        return False

    def __repr__(self):
        output = f"{self.name}, {self.price}"
        for i in self.statline:
            output= output + f'\n{i}'
        return output

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
            #if
            #sum = a[0]*random.randint(1,a[1])


def loadUnitTable(table):
    output = []
    table = html.unescape(table)

    index1 = table.find('">')+2
    index2 = table.find('<', index1)

    indexname1 = table.find("</div>", table.find("PriceTag"))+6
    indexname2 = table.find("</span>", indexname1)
    output.append(table[indexname1:indexname2])
    while index1 != -1:
        if table[index1:index2] != '':
            output.append(table[index1:index2])
        index1 = table.find('">', index2)
        if index1 != -1:
            index1 += 2
        index2 = table.find('<', index1)
    return output

def loadUnit(array, cost = 0):
    #print(array)
    price = cost
    name = ''.join([i for i in array[0][1] if not i.isdigit()])
    maxw = array[0][7].split('-')[-1]
    stats = []
    if len(array) == 1:
        statsdrop = False
    else:
        statsdrop = True
    for x in range(0, len(array)):
        ws =  ''.join([i for i in array[x][3] if i.isdigit()])
        bs = ''.join([i for i in array[x][4] if i.isdigit()])
        s = array[x][5]
        t = array[x][6]
        if len(array[x][7].split('-')) == 2 and array[x][7].split('-')[0] != 1:
            minw = array[x][7].split('-')[0]
            maxw = array[x][7].split('-')[1]
        else:
            maxw = array[x][7].split('-')[0]
            minw = 0
        a = array[x][8]
        ld= array[x][9]
        sv = ''.join([i for i in array[x][10] if i.isdigit()])
        move = ''.join([i for i in array[x][2].split('-')[0] if i.isdigit()])
        stats.append(statline(ws,bs,s,t,maxw,minw,a,ld,sv,move))
    LoadedUnits.append(UnitClass(name,maxw,stats,price,statsdrop))


def loadResources():
    global factions, unitlist
    factions = pd.read_csv('http://wahapedia.ru/wh40k9ed/Factions.csv', delimiter='|', index_col='id')
    factions = factions.drop(columns={'Ссылка', 'link'})
    unitlist = pd.read_csv('http://wahapedia.ru/wh40k9ed/Datasheets.csv', delimiter='|', index_col='name')
    unitlist = unitlist.drop(columns = {'id','source_id','role','unit_composition','power_points','transport','priest',
                                        'psyker', 'open_play_only','crusade_only','virtual','Cost','cost_per_unit'})
    factions.drop(factions.columns[factions.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    unitlist.drop(unitlist.columns[unitlist.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    #print(factions)
    #print(unitlist)

def findUnitUrl(name):
    try:
        link = unitlist.loc[name, 'link']
        return link
    except KeyError:
        return 0


def findunit(name):
    if findUnitUrl(name) == 0:
        exit
    page = urlopen(findUnitUrl(name))
    html_bytes = page.read()
    code = BeautifulSoup(html_bytes.decode("utf-8"), 'html.parser')
    code = code.findAll('table')[0]
    code = code.findAll('tr')
    unitStats = []
    temp = code[2].get_text()
    temp = temp.splitlines()
    unitStats.append(temp)
    for x in range(4, len(code), 2):
        temp = code[x].get_text()
        temp = temp.splitlines()
        if temp[1] == '':
            unitStats.append(temp)
        else:
            loadUnit(unitStats)
            unitStats = []
            unitStats.append(temp)
    loadUnit(unitStats)


if __name__ == '__main__':
    loadResources()
    LoadedUnits = []
    findunit('Ares Gunship')
    #findunit('Shield-Captain')
    #seed(0)

    print(LoadedUnits)





