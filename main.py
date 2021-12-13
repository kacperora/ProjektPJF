# This is a sample Python script.

from bs4 import BeautifulSoup
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from selenium import webdriver
from urllib.request import urlopen
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
            if
            sum = a[0]*random.randint(1,a[1])




def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    seed(0)
    page = urlopen("https://wahapedia.ru/wh40k9ed/factions/astra-cartographica/Voidsmen-at-arms")
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    print(html)
    title_index = html.find('<tr class="pTable2_short">')
    title_index = html.find('<tr>')
    start_index = title_index + len('<tr>')
    end_index = html.find('</tr>',start_index)
    table = html[start_index:end_index]
    print (table)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
