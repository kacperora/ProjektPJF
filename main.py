# This is a sample Python script.


from urllib.request import urlopen
import html
import re
import pandas as pd
import random
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk
from tkinter import messagebox


class Player:

    def __init__(self):
        self.units = None
        self.state = 'selection'
        self.models = []
        return
    def setModels(self, amounts):
        a = 0
        for i in self.units.modelsavailable:
            for x in range(int(amounts[a])):
                self.models.append(Model(i[0]))
            a+=1
        return



class MainWindow:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)

        self.frame.pack(expand=True, fill=BOTH)


class Model:
    def __init__(self, type):
        self.type = type
        self.wounds = type.maxw
        self.hascharged = False
        self.hasmoved = False
        self.destroyed = False
        self.statsnumb = 0
        self.currentstats = self.type.statline[self.statsnumb]

    def takeDMG(self, amount):
        self.wounds -= amount
        if (self.wounds <= 0):
            self.destroyed = True
        elif (self.wounds <= self.currentstats.minw):
            self.statsnumb += 1
            self.currentstats = self.type.statline[self.statsnumb]

    def restoreDMG(self, amount):
        self.wounds += amount
        if self.wounds > self.type.maxw: self.wounds = self.type.maxw
        while self.wounds >= self.currentstats.maxw:
            self.statsnumb += 1
            self.currentstats = self.type.statline[self.statsnumb]


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


class statline:
    def __init__(self, ws, bs, s, t, maxw, minw, a, ld, sv, move):
        self.move = move
        self.ws = int(ws)
        self.bs = int(bs)
        self.s = int(s)
        self.t = int(t)
        self.maxw = int(maxw)
        self.minw = int(minw)
        self.a = a
        self.ld = int(ld)
        if self.ld > 10: self.ld = self.ld % 10
        self.sv = int(sv)

    def __repr__(self):
        return f'{self.move}"\t{self.ws}+\t{self.bs}+\t{self.s}\t{self.t}\t{self.minw}-{self.maxw}\t{self.a}\t{self.ld}\t{self.sv}+'


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

    def hitMelee(self, modifier):
        roll = random.randint(1, 6)
        target = self.ws[0]
        if roll + modifier >= target | roll == 6:
            return True
        if roll == 1:
            return False
        return False

    def hitRange(self, modifier):
        roll = random.randint(1, 6)
        target = self.bs[0]
        if roll + modifier >= target | roll == 6:
            return True
        if roll == 1:
            return False
        return False

    def __repr__(self):
        output = f"{self.name}\t {self.price}"
        output = output + '\n' + 'move\tWS\tBS\tS\tT\tW\tA\tLd\tSv'
        output = output + '\n'
        for i in self.statline:
            output = output + f'\n{i}'
        # print(output)
        return output

    def __str__(self):
        output = f"{self.name}\t {self.price}"
        output = output + '\n' + 'move\tWS\tBS\tS\tT\tW\tA\tLd\tSv'
        output = output + '\n'
        for i in self.statline:
            output = output + f'\n{i}'
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
            # if
            # sum = a[0]*random.randint(1,a[1])


def resolveRoll(input, takeavg=False):
    number = 0
    if len(input.split('+')) == 2:
        b = input.split('+')[1]
    else:
        b = 0
    if len(input.split('D')) == 2:
        if input.split('D')[0] == '':
            a = 1
        else:
            a = input.split('D')[0]
        for i in range(a):
            if takeavg:
                number += (1 + input.split('D')[1]) / 2
            else:
                number += random.randint(1, input.split('D')[1])
    number += b
    return number


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
    LoadedUnits.append(ModelClass(name, maxw, stats, price, statsdrop))
    return LoadedUnits


def loadResources():
    global factions, unitlist, player1, player2, phase, distance, mathhammer, firstplayer, secondplayer, status
    status = 'begin'
    player1 = Player()
    player2 = Player()
    factions = pd.read_csv('http://wahapedia.ru/wh40k9ed/Factions.csv', delimiter='|')
    factions = factions.drop(columns={'Ссылка', 'link'})
    unitlist = pd.read_csv('http://wahapedia.ru/wh40k9ed/Datasheets.csv', delimiter='|')
    unitlist = unitlist.drop(
        columns={'id', 'source_id', 'role', 'unit_composition', 'power_points', 'transport', 'priest',
                 'psyker', 'open_play_only', 'crusade_only', 'virtual', 'Cost', 'cost_per_unit'})
    factions.drop(factions.columns[factions.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    unitlist.drop(unitlist.columns[unitlist.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    # print(factions)
    # print(unitlist)


def findUnitUrl(name):
    try:
        link = unitlist.loc[unitlist['name'] == name].iloc[0]['link']
        return link
    except KeyError:
        return 0


def findunit(name):
    if findUnitUrl(name) == 0:
        exit(0)
    page = urlopen(findUnitUrl(name))
    html_bytes = page.read()
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
    i = 0
    for x in range(4, len(code), 2):
        temp = code[x].get_text()
        temp = temp.splitlines()
        if temp[1] == '':
            unitStats.append(temp)
        else:
            table.append(loadUnit(unitStats, costs[i]))
            i += 1
            unitStats = []
            unitStats.append(temp)
    table.append(loadUnit(unitStats, costs[i]))
    unit = UnitClass(table)

    #TODO: testować na bjornie - uwaga na dispersed/focused
    weaponStats = []
    table = []
    temp = weaponscode[2].get_text(separator=" ")
    #temp = temp.splitlines()
    print(temp+'/n')
    weaponStats.append(temp)
    i = 0
    for x in range(4, len(weaponscode)):
        temp = weaponscode[x].get_text(separator=" ")
        #temp = temp.splitlines()
        print(temp)
        #if temp[1] == '':
            #unitStats.append(temp)
        #else:
            #table.append(loadUnit(unitStats, costs[i]))
            #i += 1
            #unitStats = []
            #unitStats.append(temp)
    return unit


def confirm(player):
    player.state = 'confirmed'
    refreshUI()


def clearFrame(frame):
    for widgets in frame.winfo_children():
        widgets.destroy()


def selectModels(player, modelamounts):
    amounts = []
    for i in modelamounts.get_children():
        amounts.append(modelamounts.item(i, 'values')[1])
    player.setModels(amounts)
    return


def refreshUI():
    global status
    root.update()

    def select_record():
        # clear entry boxes
        amount.delete(0, END)

        # grab record
        selected = my_game.focus()
        # grab record values
        values = my_game.item(selected, 'values')
        # temp_label.config(text=selected)

        # output to entry boxes
        modelname['text'] = values[0]
        amount.insert(0, values[1])

    # save Record
    def update_record():

        selected = my_game.focus()
        # save new data
        my_game.item(selected, text="",
                     values=(modelname['text'], amount.get()))

        # clear entry boxes
        modelname['text'] = ''
        amount.delete(0, END)

    if status == 'selection':
        if player1.state == 'selection':
            leftfactioncb = ttk.Combobox(leftplayerframe, values=factions.name.to_list())
            leftfactioncb.set("Pick an Option")
            leftunitcb = ttk.Combobox(leftplayerframe, state='disabled')
            leftunitcb.set("Pick an Option")
            leftplayerunit = Label(leftplayerframe, justify=LEFT, anchor=NW)
            leftplayerunit.pack()
            leftplayerunit.place(width=leftplayerframe.winfo_width(), height=leftplayerframe.winfo_height() - 40, x=0,
                                 y=0)
            leftfactioncb.pack()
            leftfactioncb.place(width=leftplayerframe.winfo_width() * 0.5, height=20, x=0,
                                y=leftplayerframe.winfo_height() - 20)
            leftunitcb.pack()
            leftunitcb.place(width=leftplayerframe.winfo_width() * 0.5, height=20, x=240,
                             y=leftplayerframe.winfo_height() - 20)
            leftfactioncb.bind('<<ComboboxSelected>>', lambda _: cBoxLoad(leftfactioncb, leftunitcb))
            leftunitcb.bind('<<ComboboxSelected>>', lambda _: selectUnit(player1, leftunitcb.get(), leftplayerunit,
                                                                         leftplayerconfirmbutton))
            leftplayerconfirmbutton = Button(leftplayerframe, state='disabled', text='confirm',
                                             command=lambda: confirm(player1))
            leftplayerconfirmbutton.pack()
            leftplayerconfirmbutton.place(width=leftplayerframe.winfo_width(), height=20, x=0,
                                          y=leftplayerframe.winfo_height() - 40)
        if player1.state == 'confirmed':
            clearFrame(leftplayerframe)
            modelnametxt = Label(leftplayerframe, text="model name")
            modelnametxt.place(height=20, width=240, x=0, y=0)

            amounttxt = Label(leftplayerframe, text="amount")
            amounttxt.place(height=20, width=240, x=240, y=0)

            # Entry boxes
            modelname = Label(leftplayerframe)
            modelname.place(height=20, width=leftplayerframe.winfo_width() * 0.5, x=0, y=20)
            amount = Entry(leftplayerframe)
            amount.place(height=20, width=leftplayerframe.winfo_width() * 0.5, x=leftplayerframe.winfo_width() * 0.5,
                         y=20)
            game_scroll = Scrollbar(leftplayerframe)
            game_scroll.pack(side=RIGHT, fill=Y)
            root.update()
            sroll_width = game_scroll.winfo_width()

            game_scroll = Scrollbar(leftplayerframe, orient='horizontal')
            game_scroll.pack(side=BOTTOM, fill=X)
            selectedbutton = Button(leftplayerframe, text='confirm', command=update_record)
            selectedbutton.pack()
            selectedbutton.place(height=20, width=leftplayerframe.winfo_width(), x=0, y=40)
            my_game = ttk.Treeview(leftplayerframe, yscrollcommand=game_scroll.set, xscrollcommand=game_scroll.set)
            my_game.pack(fill=BOTH)
            my_game.place(height=leftplayerframe.winfo_height() - 40, width=leftplayerframe.winfo_width() - sroll_width,
                          x=0, y=60)
            my_game.bind('<<TreeviewSelect>>', lambda _: select_record())
            game_scroll.config(command=my_game.yview)
            game_scroll.config(command=my_game.xview)
            my_game['columns'] = ('unitname', 'amount')
            my_game.column("#0", width=0, stretch=NO)
            my_game.column("unitname", anchor=CENTER, width=80)
            my_game.column("amount", anchor=CENTER, width=80)
            my_game.heading("#0", text="", anchor=CENTER)
            my_game.heading("unitname", text="Name", anchor=CENTER)
            my_game.heading("amount", text="Amount", anchor=CENTER)
            a = 0
            for i in player1.units.modelsavailable:
                my_game.insert(parent='', index='end', iid=a, text='', values=(i[0].name, 0))
                a = a + 1
            confirmbutton = Button(leftplayerframe, text = 'finished', command = lambda:selectModels(player1, my_game))
            confirmbutton.pack()
            confirmbutton.place(height=20, width=leftplayerframe.winfo_width(),
                          x=0, y=leftplayerframe.winfo_height()-20)

        if player2.state == 'selection':
            rightfactioncb = ttk.Combobox(rightplayerframe, values=factions.name.to_list())
            rightfactioncb.set("Pick an Option")
            rightunitcb = ttk.Combobox(rightplayerframe, state='disabled')
            rightunitcb.set("Pick an Option")
            rightplayerunit = Label(rightplayerframe)
            rightplayerunit.pack()
            rightplayerunit.place(width=480, height=500, x=0, y=0)
            rightfactioncb.pack()
            rightfactioncb.place(width=240, height=20, x=0, y=730)
            rightunitcb.pack()
            rightunitcb.place(width=240, height=20, x=240, y=730)
            rightfactioncb.bind('<<ComboboxSelected>>', lambda _: cBoxLoad(rightfactioncb, rightunitcb))
            rightunitcb.bind('<<ComboboxSelected>>', lambda _: selectUnit(player2, rightunitcb.get(), rightplayerunit,
                                                                          rightplayerconfirmbutton))
            rightplayerconfirmbutton = Button(rightplayerframe, state='disabled', text='confirm')
            rightplayerconfirmbutton.pack()
    if status == 'begin':
        startButton = Button(mainframe, text="My Button", command=startbattle)
        startButton.place(relx=0.5, rely=0.5, anchor=CENTER)
        global Var1, Var2
        Var1 = IntVar()
        Var2 = IntVar()
        ChkBttn = Checkbutton(mainframe, text="Mathhamer mode (średnie wartości rzutów)", variable=Var1,
                              command=set_math)
        ChkBttn.pack()
        label = Label(mainframe, text='Wybierz zaczynającego gracza:')
        label.pack()
        RBttn = Radiobutton(mainframe, text="Gracz lewy", variable=Var2,
                            value=1)
        RBttn2 = Radiobutton(mainframe, text="Gracz prawy", variable=Var2,
                             value=2)
        RBttn.pack()
        RBttn2.pack()
        status = 'selection'
        refreshUI()


def cBoxLoad(cboxin, cboxout):
    cboxin['state'] = 'disabled'
    name = cboxin.get()
    cboxout['state'] = 'disabled'
    cboxout['values'] = loadUnitsFaction(name)
    cboxout['state'] = 'normal'
    cboxin['state'] = 'normal'


def set_math():
    mathhammer = bool(Var1.get())


def startbattle():
    if player1.units is None or player2.units is None:
        messagebox.showwarning(title='brak jednostek', message='obie strony muszą wybrać jdenostki')
        return
    if Var2.get() == 1:
        firstplayer = player1
        secondplayer = player2
    else:
        firstplayer = player2
        secondplayer = player1


def selectUnit(player, name, label, button):
    player.units = findunit(name)
    text = f'{player.units}'
    a = ''
    label.config(text=text)
    LoadedUnits.clear()
    button['state'] = 'normal'


def loadUnitsFaction(factionname):
    faction_id = factions.loc[factions['name'] == factionname]
    faction_id = faction_id.iloc[0][0]
    # unitlist = unitlist.sort_values(axis = 1, by=['name'])
    return unitlist.loc[unitlist['faction_id'] == faction_id].sort_values(by='name')['name'].to_list()


if __name__ == '__main__':
    loadResources()
    LoadedUnits = []
    # print(unitlist)
    # findunit('Ares Gunship')
    # findunit('Shield-Captain')
    # seed(0)
    root = Tk()
    root.geometry("1920x1000")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _: exit(0))
    root.resizable(width=0, height=0)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # print(f'{screen_width}x{screen_height}')
    window = MainWindow(root)
    headframe = Frame(root, width=screen_width, height=screen_height * 0.25, background='red')
    headframe.pack()
    headframe.place(height=screen_height * 0.25, width=screen_width, x=0, y=0)
    leftplayerframe = Frame(root, background='blue')
    leftplayerframe.pack()
    leftplayerframe.place(height=screen_height * 0.75, width=screen_width * 0.25, x=0, y=screen_height * 0.25)
    leftplayerframe.pack_propagate(0)
    rightplayerframe = Frame(root, background='green')
    rightplayerframe.pack()
    rightplayerframe.place(height=screen_height * 0.75, width=screen_width * 0.25, x=screen_width * 0.75,
                           y=screen_height * 0.25)
    diceframe = Frame(root, width=screen_width * 0.25, height=screen_height * 0.75, background='yellow')
    diceframe.pack()
    diceframe.place(height=screen_height * 0.1, width=screen_width * 0.5, x=screen_width * 0.25, y=screen_height * 0.9)
    mainframe = Frame(root, width=screen_width * 0.5, height=screen_height * 0.75, background='black')
    mainframe.pack()
    mainframe.place(height=screen_height * 0.65, width=screen_width * 0.5, x=screen_width * 0.25,
                    y=screen_height * 0.25)
    refreshUI()
    root.mainloop()
    # print(LoadedUnits)
