# This is a sample Python script.


from urllib.request import urlopen
import html
import re
import pandas as pd
import random

class UnitClass:
    def __init__(self, name, price, ws, bs, s, t, maxw, a, ld, sv, mincount, maxcount, move, statsdrop = False):
        self.name = name
        self.mincount = mincount
        self.maxcount = maxcount
        self.move = move
        self.price = price
        self.ws = ws
        self.bs = bs
        self.s = s
        self.t = t
        self.maxw = maxw
        self.a = a
        self.ld = ld
        self.sv = sv
        self.statsdrop = statsdrop
        if self.statsdrop:
            self.droptable = []


    def hitMelee(self, modifier):
        roll = random.randint(1,6)
        target = self.ws[0]
        if roll + modifier >= target | roll == 6:
            return True
        if roll == 1: return False
        return False

    def hitRange(self, modifier):
        roll = random.randint(1,6)
        target = self.bs[0]
        if roll + modifier >= target | roll == 6:
            return True
        if roll == 1: return False
        return False

    def __repr__(self):
        return f"{self.name}, {self.price}"

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

def loadUnit(array):
    if (array[1] == ''):
        return
    if array[1].find('‑') == -1:
        min = array[1]
        max = array[1]
    else:
        min = (array[1].split("‑"))[0]
        max = (array[1].split("‑"))[1]

    unit = UnitClass(name=array[0], mincount=min, maxcount=max, price=array[2],
                move = array[3], ws = array[4], bs = array[5], s=array[6], t=array[7], maxw=array[8],a=array[9],
                ld = array[10], sv = array[11])
    LoadedUnits.append(unit)

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
    code = html_bytes.decode("utf-8")
    title_index = 0
    end_index = 0
    #print(code)
    while code.find('<tr class="pTable2_short">', title_index) != -1:
        title_index = code.find('<tr class="pTable2_short">',end_index)
        title_index = code.find('<tr>', title_index)
        start_index = title_index + len('<tr>')
        end_index = code.find('</tr>',start_index)
        table = code[start_index:end_index]
        table = loadUnitTable(table)
        loadUnit(table)

if __name__ == '__main__':
    loadResources()
    LoadedUnits = []
    findunit('Custodian Guard')
    findunit('Commissar Yarrick')
    #seed(0)

    print(LoadedUnits)





