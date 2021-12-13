# This is a sample Python script.


from urllib.request import urlopen
import html
import re
import random

class Unit:
    def __init__(self, name, price, ws, bs, s, t, maxw, a, ld, sv):
        name = name
        price = price
        ws = ws
        bs = bs
        s = s
        t = t
        maxw = maxw
        a = a
        ld = ld
        sv = sv

class Weapon:
    d = 0
    def __init__(self, name, range, s, ap, D):
        self.name = name
        self.range = range
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

    indexname1 = table.find("</div>",table.find("PriceTag"))+6
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





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #seed(0)
    page = urlopen("https://wahapedia.ru/wh40k9ed/factions/astra-cartographica/Voidsmen-at-arms")
    html_bytes = page.read()
    code = html_bytes.decode("utf-8")
    #print(code)
    title_index = code.find('<tr class="pTable2_short">')
    title_index = code.find('<tr>')
    start_index = title_index + len('<tr>')
    end_index = code.find('</tr>',start_index)
    table = code[start_index:end_index]
    print (table)
    table = loadUnitTable(table)
    print(table)


