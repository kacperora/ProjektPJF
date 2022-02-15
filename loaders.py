import html
import urllib
import urllib.request

import pandas as pd

from modelclass import ModelClass
from statline import statline
from weapon import *
from bs4 import BeautifulSoup
from unitclass import *


def loadWeapon(temp):
    # print(temp)
    try:
        i = 0
        if bool(re.search(r'\d', temp[i])):
            i += 1
        name = ''
        while i < len(temp) and temp[i] != 'Melee' and temp[i][0].isdigit() is False:
            if temp[i] != '\\xa0-':
                name += temp[i] + ' '
            i += 1
        range = temp[i]
        i += 1
        type = ''
        while i < len(temp) and temp[i][-1].isdigit() is False:
            type += temp[i] + ' '
            if 'Melee' in type:
                break
            i += 1
        shots = temp[i]
        i += 1
        S = temp[i]
        i += 1
        AP = temp[i]
        i += 1
        DMG = temp[i]
        if name.startswith('Blast'):
            return 0
        weapon = Weapon(name, range, shots, type, S, AP, DMG)

        # print('weapon loaded')
        # print(weapon)
        return weapon
    except IndexError:
        # print('ping')
        return 0


def weaponnamecheck(name):
    if name.startswith('Each'):
        return False
    elif name.startswith('If'):
        return False
    elif name.startswith('Blast'):
        return False
    elif name.startswith('When'):
        return False
    elif name.startswith('Each time'):
        return False
    elif 'Before' in name:
        return False
    elif name.startswith('After'):
        return False
    elif name.startswith('One use'):
        return False
    elif name.startswith('Roll'):
        return False
    else:
        return True


def findunit(name):
    if findUnitUrl(name) == 0:
        exit(0)
    headers = {'User-Agent': 'Mozilla/5.0'}
    request = urllib.request.Request(url=findUnitUrl(name), headers=headers)
    response = urllib.request.urlopen(request)
    # page = urlopen(findUnitUrl(name))
    html_bytes = response.read()

    code = BeautifulSoup(html_bytes.decode("utf-8"), 'html.parser')
    weaponscode = code.findAll('table')[1]
    weaponscode = weaponscode.findAll('tr')
    code = code.findAll('table')[0]
    prices = code.find_all("div", {"class": "PriceTag"})
    costs = []
    for i in range(0, len(prices), 2):
        costs.append(int(prices[i].get_text()))
    code = code.findAll('tr')
    # print(costs)
    unitStats = []
    table = []
    temp = code[2].get_text()
    temp = temp.splitlines()
    unitStats.append(temp)
    weapon_name = ''
    i = 0
    for x in range(4, len(code), 2):
        temp = code[x].get_text()
        temp = temp.splitlines()
        if temp[1] == '':
            unitStats.append(temp)
        else:
            table.append(loadUnit(unitStats, costs[i]))
            i += 1
            unitStats = [temp]
    table.append(loadUnit(unitStats, costs[i]))
    weaponStats = []
    for x in range(2, len(weaponscode)):
        temp = weaponscode[x].get_text(separator=" ")
        temp = temp.split(' ')
        temp[:] = [x for x in temp if x]
        # print(temp)
        if temp[0] == '\xa0-':
            i = x
            while weaponscode[i].get_text(separator=" ").split(' ')[0] == '\xa0-' or \
                    weaponscode[i].get_text(separator=" ").split(' ')[0] == 'Blast' or \
                    weaponscode[i].get_text(separator=" ").split(' ')[0] == 'Each' or \
                    'When' in weaponscode[i].get_text(separator=" "):
                i -= 1
            weapon_name = ''
            for str in weaponscode[i].get_text(separator=" ").split(' '):
                if str == 'Blast' or str == 'Before':
                    break
                weapon_name += str + ' '
            # print(weapon_name)
        # if temp.count('Melee') != 0 or temp.count('%d+'):
        #    print(temp)
        weapon = loadWeapon(temp)
        if weapon != 0:
            if not weaponnamecheck(weapon.name):
                weapon = 0
            if weapon != 0:
                if temp[0] == '\xa0-':
                    # print('ping')
                    weapon.name = weapon_name + weapon.name
                #    weapon = 0
                # if weapon != 0:
                # print(weapon)
                print(weapon.name)
                weaponStats.append(weapon)
    weaponStats.append(Weapon('Close combat Weapon', 'Melee', 'Melee', 'Melee', 'User', 0, -1))
    # print(weaponStats)
    unit = UnitClass(table, weaponStats)
    return unit


def findUnitUrl(name):
    try:
        unitlist = pd.read_csv('Datasheets.csv', delimiter='|')
        unitlist = unitlist.drop(
            columns={'id', 'source_id', 'role', 'unit_composition', 'power_points', 'transport', 'priest',
                     'psyker', 'open_play_only', 'crusade_only', 'virtual', 'Cost', 'cost_per_unit'})
        unitlist.drop(unitlist.columns[unitlist.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
        link = unitlist.loc[unitlist['name'] == name].iloc[0]['link']

        return link
    except KeyError:
        return 0


def loadUnitTable(table):
    output = []
    table = html.unescape(table)

    index1 = table.find('">') + 2
    index2 = table.find('<', index1)

    indexname1 = table.find("</div>", table.find("PriceTag")) + 6
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


def getWeaponName(temp):
    try:
        i = 0
        if bool(re.search(r'\d', temp[i])):
            i += 1
        name = ''
        while i < len(temp) and temp[i] != 'Melee' and temp[i][0].isdigit() is False:
            if temp[i] != '\\xa0-':
                name += temp[i] + ' '
            i += 1
        if name == 'Blast':
            return 0
        # print('weapon loaded')
        # print(weapon)
        return name
    except IndexError:
        # print('ping')
        return 0


def loadUnit(array, cost=0):
    # print(array)
    price = cost
    LoadedUnits = []
    name = ''.join([i for i in array[0][1] if not i.isdigit()])
    maxw = array[0][7].split('-')[-1]
    stats = []
    if len(array) == 1:
        statsdrop = False
    else:
        statsdrop = True
    for x in range(0, len(array)):
        ws = ''.join([i for i in array[x][3] if i.isdigit()])
        bs = ''.join([i for i in array[x][4] if i.isdigit()])
        s = array[x][5]
        t = array[x][6]
        if len(array[x][7].split('-')) == 2 and array[x][7].split('-')[0] != '1':
            minw = array[x][7].split('-')[0]
            maxw = array[x][7].split('-')[1]
        elif len(array[x][7].split('-')) == 1:
            maxw = array[x][7].split('-')[0]
            minw = 1
        else:
            maxw = array[x][7].split('-')[1]
            minw = 1
        a = array[x][8]
        ld = array[x][9]
        sv = ''.join([i for i in array[x][10] if i.isdigit()])
        move = ''.join([i for i in array[x][2].split('-')[0] if i.isdigit()])
        stats.append(statline(ws, bs, s, t, maxw, minw, a, ld, sv, move))
    if name.startswith("‑"):
        name = name[1:]
    LoadedUnits.append(ModelClass(name, maxw, stats, price, statsdrop))
    return LoadedUnits
