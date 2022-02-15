# This is a sample Python script.


from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import ttkwidgets as ttkw
from ttkthemes import ThemedStyle
from tkinter import scrolledtext

from Player import *
from parsers import *
from loaders import *


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)

        self.frame.pack(expand=True, fill=BOTH)


# noinspection PyGlobalUndefined
def loadResources():
    global factions, unitlist, player1, player2, phase, distance, mathhammer, firstplayer
    global secondplayer, status, distance, phase, turn, maxturns, activeplayer, defaultstate
    turn = 0
    maxturns = 1000
    distance = 0
    status = 'begin'
    defaultstate = 'disabled'
    player1 = Player("player1")
    player2 = Player("player2")
    factions = pd.read_csv('Factions.csv', delimiter='|')
    factions = factions.drop(columns={'Ссылка', 'link'})
    unitlist = pd.read_csv('Datasheets.csv', delimiter='|')
    unitlist = unitlist.drop(
        columns={'id', 'source_id', 'role', 'unit_composition', 'power_points', 'transport', 'priest',
                 'psyker', 'open_play_only', 'crusade_only', 'virtual', 'Cost', 'cost_per_unit'})
    factions.drop(factions.columns[factions.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    unitlist.drop(unitlist.columns[unitlist.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
    # print(factions)
    # print(unitlist)


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
    player.state = 'weaponselection'
    refreshUI()
    return


def finishweaponsselection(player):
    root.update()
    player.state = 'ready'
    if player == player2:
        for child in rightplayerframe.winfo_children():
            try:
                child.configure(state='disable')
            except TclError:
                pass
    if player == player1:
        for child in leftplayerframe.winfo_children():
            try:
                child.configure(state='disable')
            except TclError:
                pass


def switchPlayer():
    global activeplayer
    if activeplayer == firstplayer:
        activeplayer = secondplayer
        refreshUI()
    else:
        activeplayer = firstplayer
        nextPhase()


def tryAttack(bs, modifiers, reroll='none'):
    roll = random.randrange(1, 7)
    if roll == 1 and reroll == '1s':
        roll = random.randrange(1, 7)
        if roll + modifiers >= int(bs) or roll == 6 and roll != 1:
            return True
        else:
            return False
    if roll + modifiers >= int(bs) or roll == 6 and roll != 1:
        return True
    else:
        roll = random.randrange(1, 7)
        if roll + modifiers >= int(bs) or roll == 6 and roll != 1:
            return True
        return False


def victory():
    global status
    status = 'summary'
    refreshUI()


def resolveMeleeAttack(ws, attackcount, weaponstr, target, modifiers, DMG, ap, str, targetplayer, reroll='none',
                       rerollw='none', rerollarm='none'):
    strength = meleeStrength(weaponstr, str)
    if targetplayer.unitcount < 1:
        victory()
    attackcount = resolveRoll(attackcount)
    if target.destroyed:
        selectedunit = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
        while selectedunit.destroyed and targetplayer.unitcount > 0:
            selectedunit = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
            resolveMeleeAttack(ws, attackcount, weaponstr, target, modifiers, DMG, ap, str, targetplayer, reroll,
                               rerollw, rerollarm)
    for i in range(attackcount):
        log(f"\tattack {i + 1} of {attackcount}:")
        if tryAttack(ws, modifiers, reroll):
            log("\t\thit!")
            if target.tryWound(strength, modifiers, rerollw):
                log("\t\t\twounded!")
                if not target.tryArmor(int(ap), rerollarm):
                    dmg = resolveRoll(DMG)
                    log(f"\t\t\t\tpassed armor and dealt {dmg} wounds")
                    target.takeDMG(dmg)
                    if target.destroyed:
                        log("target is dead")
                        targetplayer.unitcount -= 1
                        targetplayer.unitdead += 1
                        targetplayer.points_lost += int(target.type.price)
                        if targetplayer.unitcount == 0:
                            victory()

                        elif i < attackcount - 1:
                            log(f"{attackcount - (i + 1)} attacks left, choosing random new target")
                            selectedunit = player2.models[random.randint(0, len(player2.models) - 1)]
                            while selectedunit.destroyed:
                                selectedunit = player2.models[random.randint(0, len(player2.models) - 1)]
                                resolveMeleeAttack(ws, attackcount - i, weaponstr, target, modifiers, DMG, ap, str,
                                                   targetplayer, reroll, rerollw, rerollarm)
                        if activeplayer == player2:
                            player1.unitcount -= 1
                            player1.unitdead += 1
                            if player1.unitcount == 0:
                                victory()
                            elif i < attackcount - 1:
                                log(f"{attackcount - (i + 1)} attacks left, choosing random new target")
                                selectedunit = player1.models[random.randint(0, len(player1.models) - 1)]
                                while selectedunit.destroyed and targetplayer.unitcount > 0:
                                    selectedunit = player1.models[random.randint(0, len(player1.models) - 1)]
                                    resolveMeleeAttack(ws, attackcount - i, weaponstr, target, modifiers, DMG, ap, str,
                                                       targetplayer, reroll, rerollw, rerollarm)
                else:
                    log("\t\t\t\tblocked by armor")
            else:
                log("\t\t\tfailed to wound!")
        else:
            log("\t\tmiss!")


def resolveAttack(bs, attackcount, weaponstr, target, modifiers, DMG, ap, targetplayer, reroll='none', rerollw='none',
                  rerollarm='none'):
    attackcount = resolveRoll(attackcount)
    if targetplayer.unitcount < 1:
        victory()
    if target.destroyed:
        selectedunit = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
        while selectedunit.destroyed and targetplayer.unitcount > 0:
            selectedunit = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
            resolveAttack(bs, attackcount, weaponstr, target, modifiers, DMG, ap, targetplayer, reroll,
                          rerollw, rerollarm)
    for i in range(attackcount):
        log(f"\tattack {i + 1} of {attackcount}:")
        if tryAttack(bs, modifiers, reroll):
            log("\t\thit!")
            if target.tryWound(weaponstr, modifiers, rerollw):
                log("\t\t\twounded!")
                if not target.tryArmor(int(ap), rerollarm):
                    dmg = resolveRoll(DMG)
                    log(f"\t\t\t\tpassed armor and dealt {dmg} wounds")
                    target.takeDMG(dmg)
                    if target.destroyed:
                        log("target is dead")
                        targetplayer.unitcount -= 1
                        targetplayer.unitdead += 1
                        targetplayer.points_lost += int(target.type.price)
                        if targetplayer.unitcount == 0:
                            victory()

                        elif i < attackcount - 1:
                            log(f"{attackcount - (i + 1)} shots left, choosing random new target")
                            selectedunit = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
                            while selectedunit.destroyed and targetplayer.unitcount > 0:
                                selectedunit = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
                                resolveAttack(bs, attackcount - i, weaponstr, selectedunit, modifiers, DMG, ap,
                                              targetplayer,
                                              reroll,
                                              rerollw, rerollarm)
                else:
                    log("\t\t\t\tblocked by armor")
            else:
                log("\t\t\tfailed to wound!")
        else:
            log("\t\tmiss!")


def docharge(player):
    player.has_charged = True
    dist = resolveRoll('2D6')
    global distance
    if abs(distance) - dist <= 1:
        log("charge succesful")
        distance = max(0, distance - dist)
    else:
        log(f"charge failed, rolled {dist} out of needed: {distance - 1}")
    switchPlayer()


def dontcharge(player):
    player.has_charged = False
    switchPlayer()


def log(s):
    print(s)
    logtext.configure(state='normal')
    logtext.insert(INSERT, "\n" + s)
    logtext.configure(state='disabled')


def refreshUI():
    global status
    root.update()
    moveVar = IntVar()

    def select_theme(theme):
        style = ThemedStyle()
        style.set_theme(theme)
        style.theme_use(theme)

    def confirmmovement(player):
        global distance
        distances = []
        maxdistance = 0
        for x in player.models:
            distances.append(x.currentstats.move)
        if moveVar.get() == 1:
            player.has_moved = False
            player.has_advanced = False
            maxdistance = 0
        if moveVar.get() == 2:
            player.has_moved = True
            player.has_advanced = False
            maxdistance = min(distances)
        if moveVar.get() == 3:
            player.has_moved = True
            player.has_advanced = True
            maxdistance = int(min(distances)) + resolveRoll('D6')
        maxdistance = min(int(maxdistance), int(distance))
        maxmovelabel['text'] = maxdistance
        minmovelabel['text'] = maxdistance * -1
        distanceentry['state'] = 'normal'

    def confirmmovedist(player):
        global distance
        if moveVar.get() == 1:
            log(f"{player.name} stays stationary")
            player.has_moved = False
            player.has_advanced = False
        if moveVar.get() == 2:
            log(f"{player.name} moves {distanceentry.get()}\"")
            player.has_moved = True
            player.has_advanced = False
            if distanceentry.get() != '':
                if int(maxmovelabel['text']) >= int(distanceentry.get()) >= int(minmovelabel['text']):
                    distance -= int(distanceentry.get())
                elif int(distanceentry.get()) >= int(minmovelabel['text']):
                    distance -= int(maxmovelabel['text'])
                elif int(distanceentry.get()) <= int(maxmovelabel['text']):
                    distance -= int(minmovelabel['text'])
        if moveVar.get() == 3:
            log(f"{player.name} advances {distanceentry.get()}\"")
            player.has_moved = True
            player.has_advanced = True
            if distanceentry.get() != '':
                if int(maxmovelabel['text']) >= int(distanceentry.get()) >= int(minmovelabel['text']):
                    distance -= int(distanceentry.get())
                elif int(distanceentry.get()) >= int(minmovelabel['text']):
                    distance -= int(maxmovelabel['text'])
                elif int(distanceentry.get()) <= int(maxmovelabel['text']):
                    distance -= int(minmovelabel['text'])
        switchPlayer()

    def select_record(player=player1):
        if player == player2:
            rightamount.delete(0, END)
            # grab record
            selected = my_game2.focus()
            # grab record values
            values = my_game2.item(selected, 'values')
            # output to entry boxes
            rightmodelname['text'] = values[0]
            rightamount.insert(0, values[1])
            return
        # clear entry boxes
        amount.delete(0, END)
        selected = my_game.focus()
        values = my_game.item(selected, 'values')
        modelname['text'] = values[0]
        amount.insert(0, values[1])

    # save Record
    def update_record(player=player1):
        if player == player2:
            selected = my_game2.focus()
            # save new data
            my_game2.item(selected, text="",
                          values=(rightmodelname['text'], rightamount.get()))

            # rightamount.delete(0, END)
            my_game2.selection_clear()
            return

        selected = my_game.focus()
        # save new data
        my_game.item(selected, text="",
                     values=(modelname['text'], amount.get()))

        amount.delete(0, END)
        my_game.selection_clear()

    def select_model(player):

        if player == player2:
            # confirm_weaponlist(player2)
            selected = rightmodellist.focus()
            rightmodelname['text'] = rightmodellist.item(selected, 'values')[0] + \
                                     rightmodellist.item(selected, 'values')[1]
            a = 0
            modelweaponarray = player.models[int(selected)].weapons
            rightweaponlist.delete(*rightweaponlist.get_children())
            # print(modelweaponarray)
            for i in player.units.weapons:
                if a < len(modelweaponarray):
                    rightweaponlist.insert(parent='', index='end', iid=a, text='', values=(i.summary(),
                                                                                           modelweaponarray[a]))
                else:
                    weaponcount = 0
                    rightweaponlist.insert(parent='', index='end', iid=a, text='', values=(i.summary(), weaponcount))
                a += 1
            return
        # confirm_weaponlist(player1)
        selected = modellist.focus()
        modelname['text'] = modellist.item(selected, 'values')[0] + modellist.item(selected, 'values')[1]
        a = 0
        modelweaponarray = player.models[int(selected)].weapons
        weaponlist.delete(*weaponlist.get_children())
        for i in player.units.weapons:
            if a < len(modelweaponarray):
                weaponlist.insert(parent='', index='end', iid=a, text='', values=(i.summary(), modelweaponarray[a]))
            else:
                weaponcount = 0
                weaponlist.insert(parent='', index='end', iid=a, text='', values=(i.summary(), weaponcount))
            a += 1
        return

    def select_weapon(player=player1):
        if player == player2:
            selected = rightweaponlist.focus()
            rightweaponname['text'] = rightweaponlist.item(selected, 'values')[0]
            amount = rightweaponlist.item(selected, 'values')[1]
            a = 0
            rightweaponlist.item(selected, text="", values=(rightweaponname['text'], amount))
            return
        selected = weaponlist.focus()
        weaponname['text'] = weaponlist.item(selected, 'values')[0]
        amount = weaponlist.item(selected, 'values')[1]
        a = 0
        weaponlist.item(selected, text="", values=(weaponname['text'], amount))
        pass

    def update_weapon(player=player1):
        if player == player2:
            selected = rightweaponlist.focus()
            rightweaponlist.item(selected, text="",
                                 values=(rightweaponname['text'], rightamount.get()))
            confirm_weaponlist(player2)
            return
        selected = weaponlist.focus()
        weaponlist.item(selected, text="",
                        values=(weaponname['text'], amount.get()))
        confirm_weaponlist(player1)
        pass

    def confirm_weaponlist(player=player1):
        if player == player2:
            selectedmodel = rightmodellist.focus()
            i = 0
            player.models[int(selectedmodel)].weapons = []
            for each in rightweaponlist.get_children():
                player.models[int(selectedmodel)].weapons.append([int(rightweaponlist.item(i, 'values')[1])])
                i += 1
            player.models[int(selectedmodel)].weapons[-1] = [1]
            return
        selectedmodel = modellist.focus()
        i = 0
        player.models[int(selectedmodel)].weapons = []
        for each in weaponlist.get_children():
            player.models[int(selectedmodel)].weapons.append([int(weaponlist.item(i, 'values')[1])])
            i += 1
        player.models[int(selectedmodel)].weapons[-1] = [1]
        return

    def refreshplayermodelhp(player):
        if player == player2:
            rightmodellist.delete(*rightmodellist.get_children())
            a = 0
            for i in player2.models:
                rightmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.wounds, i.type.maxw))
                a += 1
            pass
        if player == player1:
            leftmodellist.delete(*leftmodellist.get_children())
            a = 0
            for i in player2.models:
                leftmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.wounds, i.type.maxw))
                a += 1
            pass

    def shoot(player):
        if player == player2:
            items = rightplayershoot.get_checked()
            for i in items:
                strings = i.split('-')
                if len(strings) == 3:
                    model = player.models[int(strings[0])]
                    weapon = player.units.weapons[int(strings[1])]
                    setupshooting(model, weapon, player2)
                    refreshplayermodelhp(player1)
        if player == player1:
            items = leftplayershoot.get_checked()
            for i in items:
                strings = i.split('-')
                if len(strings) == 3:
                    model = player.models[int(strings[0])]
                    weapon = player.units.weapons[int(strings[1])]
                    setupshooting(model, weapon, player1)
                    refreshplayermodelhp(player2)
        switchPlayer()

    def melee(player):
        if player == player2:
            items = rightplayermelee.get_checked()
            for i in items:
                strings = i.split('-')
                if len(strings) == 3:
                    model = player.models[int(strings[0])]
                    weapon = player.units.weapons[int(strings[1])]
                    setupmelee(model, weapon, player2)
                    refreshplayermodelhp(player1)
        if player == player1:
            items = leftplayermelee.get_checked()
            for i in items:
                strings = i.split('-')
                if len(strings) == 3:
                    model = player.models[int(strings[0])]
                    weapon = player.units.weapons[int(strings[1])]
                    setupmelee(model, weapon, player1)
                    refreshplayermodelhp(player2)
        switchPlayer()

    def setupmelee(model, weapon, player):
        # setup ui and get parameters
        if player == player1:
            targetplayer = player2
            targetmodellist = rightmodellist
        else:
            targetplayer = player1
            targetmodellist = leftmodellist
        if targetmodellist.focus() == '':
            target = player2.models[random.randint(0, len(player2.models) - 1)]
            while target.destroyed:
                target = player2.models[random.randint(0, len(player2.models) - 1)]
        else:
            target = targetplayer.models[int(targetmodellist.focus())]
        ws = model.currentstats.ws
        defaultmod = 0
        global distance, defaultstate
        weaponstr = weapon.s
        attackcount = model.currentstats.a
        attackcount = resolveRoll(attackcount)
        dmg = weapon.d
        modelnamestr = model.type.name
        weaponnamestr = weapon.name
        modelstr = model.currentstats.s
        # perform attack
        log(f"{player} attacks with model {modelnamestr} {attackcount} times using: {weaponnamestr} with ws = {ws},"
            f" S = {weaponstr} and modifier of {defaultmod}:", )
        resolveMeleeAttack(ws, attackcount, weaponstr, target, defaultmod, dmg, int(weapon.ap), int(modelstr),
                           targetplayer)

    def setupshooting(model, weapon, player):
        # setup ui and get parameters
        if player == player1:
            targetplayer = player2
            targetmodellist = rightmodellist
        else:
            targetplayer = player1
            targetmodellist = leftmodellist
        if targetmodellist.focus() == '':
            target = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
            while target.destroyed:
                target = targetplayer.models[random.randint(0, len(targetplayer.models) - 1)]
        else:
            target = targetplayer.models[int(targetmodellist.focus())]
        bs = model.currentstats.bs
        defaultmod = 0
        global distance, defaultstate
        weaponstr = resolveRoll(weapon.s)
        attackcount = weapon.shots
        if 'Rapid' in weapon.type and int(weapon.range[:-1]) >= distance / 2:
            attackcount = resolveRoll(attackcount)
            attackcount *= 2
        if 'Heavy' in weapon.type and player.has_moved:
            defaultmod = -1
        if 'Dakka' in weapon.type:
            if int(weapon.range[:-1]) >= distance / 2:
                attackcount = attackcount.split('/')[0]
            else:
                attackcount = attackcount.split('/')[1]

        attackcount = resolveRoll(attackcount)
        dmg = weapon.d
        modelnamestr = model.type.name
        weaponnamestr = weapon.name
        # perform attack
        log(f"player 1 attacks with model {modelnamestr} {attackcount} times using: {weaponnamestr} with bs = {bs},"
            f" S = {weaponstr} and modifier of {defaultmod}:", )
        resolveAttack(bs, attackcount, weaponstr, target, defaultmod, dmg, int(weapon.ap), targetplayer)

    if status == 'selection':
        if player1.state == 'selection':
            leftfactioncb = ttk.Combobox(leftplayerframe, values=factions.name.to_list())
            leftfactioncb.set("Pick an Option")
            leftunitcb = ttk.Combobox(leftplayerframe, state='disabled')
            leftunitcb.set("Pick an Option")
            leftplayerunit = ttk.Label(leftplayerframe, justify=LEFT, anchor=NW)
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
            leftplayerconfirmbutton = ttk.Button(leftplayerframe, state='disabled', text='confirm',
                                                 command=lambda: confirm(player1))
            leftplayerconfirmbutton.pack()
            leftplayerconfirmbutton.place(width=leftplayerframe.winfo_width(), height=20, x=0,
                                          y=leftplayerframe.winfo_height() - 40)
        if player1.state == 'confirmed':
            clearFrame(leftplayerframe)
            modelnametxt = ttk.Label(leftplayerframe, text="model name")
            modelnametxt.place(height=20, width=leftplayerframe.winfo_width() * 0.5, x=0, y=0)

            amounttxt = ttk.Label(leftplayerframe, text="amount")
            amounttxt.place(height=20, width=leftplayerframe.winfo_width() * 0.5, x=240, y=0)

            # Entry boxes
            modelname = ttk.Label(leftplayerframe)
            modelname.place(height=20, width=leftplayerframe.winfo_width() * 0.5, x=0, y=20)

            reg = leftplayerframe.register(callback)
            amount = ttk.Entry(leftplayerframe, validate="key", validatecommand=(reg, '%P'))
            amount.place(height=20, width=(leftplayerframe.winfo_width() * 0.5) - 10,
                         x=leftplayerframe.winfo_width() * 0.5,
                         y=20)
            amount.bind("<Return>", update_record)
            game_scroll = ttk.Scrollbar(leftplayerframe)
            game_scroll.pack(side=RIGHT, fill=Y)
            root.update()
            sroll_width = game_scroll.winfo_width()

            game_scroll = ttk.Scrollbar(leftplayerframe, orient='horizontal')
            game_scroll.pack(side=BOTTOM, fill=X)
            selectedbutton = ttk.Button(leftplayerframe, text='confirm', command=update_record)
            selectedbutton.pack()
            selectedbutton.place(height=20, width=leftplayerframe.winfo_width() - 10, x=0, y=40)
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
            confirmbutton = ttk.Button(leftplayerframe, text='finished', command=lambda: selectModels(player1, my_game))
            confirmbutton.pack()
            confirmbutton.place(height=20, width=leftplayerframe.winfo_width() - 10,
                                x=0, y=leftplayerframe.winfo_height() - 20)
        if player1.state == 'weaponselection':
            clearFrame(leftplayerframe)
            modelnametxt = ttk.Label(leftplayerframe, text="model name")
            modelnametxt.place(height=20, width=leftplayerframe.winfo_width() * 0.33, x=0, y=0)

            amounttxt = ttk.Label(leftplayerframe, text="weapon name")
            amounttxt.place(height=20, width=leftplayerframe.winfo_width() * 0.33,
                            x=leftplayerframe.winfo_width() * 0.33, y=0)

            weapontxt = ttk.Label(leftplayerframe, text="amount")
            weapontxt.place(height=20, width=leftplayerframe.winfo_width() * 0.33,
                            x=leftplayerframe.winfo_width() * 0.66, y=0)

            # Entry boxes
            modelname = ttk.Label(leftplayerframe, text="model name")
            modelname.place(height=20, width=leftplayerframe.winfo_width() * 0.33, x=0, y=20)
            weaponname = ttk.Label(leftplayerframe, text="weapon name")
            weaponname.place(height=20, width=leftplayerframe.winfo_width() * 0.33,
                             x=leftplayerframe.winfo_width() * 0.33, y=20)

            reg = leftplayerframe.register(callback)
            amount = ttk.Entry(leftplayerframe, validate="key", validatecommand=(reg, '%P'))
            amount.place(height=20, width=leftplayerframe.winfo_width() * 0.33, x=leftplayerframe.winfo_width() * 0.66,
                         y=20)

            selectedbutton = ttk.Button(leftplayerframe, text='confirm', command=update_weapon)
            amount.bind("<Return>", update_weapon)
            selectedbutton.pack()
            selectedbutton.place(height=20, width=leftplayerframe.winfo_width(), x=0, y=40)
            modellist = ttk.Treeview(leftplayerframe)
            modellist.pack()
            modellist.place(height=(leftplayerframe.winfo_height() - 40) / 2, width=leftplayerframe.winfo_width(),
                            x=0, y=60)
            modellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
            modellist['columns'] = ('modelname', 'modelnumber')
            modellist.column("#0", width=0, stretch=NO)
            modellist.column("modelname", anchor=CENTER, width=80)
            modellist.column("modelnumber", anchor=CENTER, width=80)
            modellist.heading("#0", text="", anchor=CENTER)
            modellist.heading("modelname", text="Model", anchor=CENTER)
            modellist.heading("modelnumber", text="Number", anchor=CENTER)
            weaponlist = ttk.Treeview(leftplayerframe)
            weaponlist.pack()
            weaponlist.place(height=((leftplayerframe.winfo_height() - 40) / 2) - 40,
                             width=leftplayerframe.winfo_width(),
                             x=0, y=((leftplayerframe.winfo_height() - 40) / 2) + 60)
            weaponlist.bind('<<TreeviewSelect>>', lambda _: select_weapon())
            weaponlist['columns'] = ('weapon', 'count')
            weaponlist.column("#0", width=0, stretch=NO)
            weaponlist.column("weapon", anchor=CENTER, width=80)
            weaponlist.column("count", anchor=CENTER, width=80)
            weaponlist.heading("#0", text="", anchor=CENTER)
            weaponlist.heading("weapon", text="Weapon", anchor=CENTER)
            weaponlist.heading("count", text="Count", anchor=CENTER)
            weaponlist.bind("<Return>", lambda _: update_weapon(player1))

            leftfinishweaponsbutton = ttk.Button(leftplayerframe, text='finish setting up weapons',
                                                 command=lambda: finishweaponsselection(player1))
            leftfinishweaponsbutton.pack()
            leftfinishweaponsbutton.place(y=leftplayerframe.winfo_height() - 40, x=0, height=40,
                                          width=leftplayerframe.winfo_width())
            a = 0
            count = 1
            lastname = player1.models[0].type.name
            for i in player1.models:
                # (i)
                if i.type.name != lastname: count = 1
                modellist.insert(parent='', index='end', iid=a, text='', values=(i.type.name, count))
                lastname = i.type.name
                count += 1
                a = a + 1
            # confirmbutton = Button(leftplayerframe, text='finished', command=lambda: selectModels(player1, my_game))
            # confirmbutton.pack()
            # confirmbutton.place(height=20, width=leftplayerframe.winfo_width(),
            # x=0, y=leftplayerframe.winfo_height() - 20)
        if player1.state != 'ready':
            player1.state = ''

        if player2.state == 'selection':
            rightfactioncb = ttk.Combobox(rightplayerframe, values=factions.name.to_list())
            rightfactioncb.set("Pick an Option")
            rightunitcb = ttk.Combobox(rightplayerframe, state='disabled')
            rightunitcb.set("Pick an Option")
            rightplayerunit = ttk.Label(rightplayerframe, justify=LEFT, anchor=NW)
            rightplayerunit.pack()
            rightplayerunit.place(width=rightplayerframe.winfo_width(), height=rightplayerframe.winfo_height() - 40,
                                  x=0,
                                  y=0)
            rightfactioncb.pack()
            rightfactioncb.place(width=rightplayerframe.winfo_width() * 0.5, height=20, x=0,
                                 y=rightplayerframe.winfo_height() - 20)
            rightunitcb.pack()
            rightunitcb.place(width=rightplayerframe.winfo_width() * 0.5, height=20, x=240,
                              y=rightplayerframe.winfo_height() - 20)
            rightfactioncb.bind('<<ComboboxSelected>>', lambda _: cBoxLoad(rightfactioncb, rightunitcb))
            rightunitcb.bind('<<ComboboxSelected>>', lambda _: selectUnit(player2, rightunitcb.get(), rightplayerunit,
                                                                          rightplayerconfirmbutton))
            rightplayerconfirmbutton = ttk.Button(rightplayerframe, state='disabled', text='confirm',
                                                  command=lambda: confirm(player2))
            rightplayerconfirmbutton.pack()
            rightplayerconfirmbutton.place(width=rightplayerframe.winfo_width(), height=20, x=0,
                                           y=rightplayerframe.winfo_height() - 40)
        if player2.state == 'confirmed':
            clearFrame(rightplayerframe)
            rightmodelnametxt = ttk.Label(rightplayerframe, text="model name")
            rightmodelnametxt.place(height=20, width=rightplayerframe.winfo_width() * 0.5, x=0, y=0)

            rightamounttxt = ttk.Label(rightplayerframe, text="amount")
            rightamounttxt.place(height=20, width=rightplayerframe.winfo_width() * 0.5, x=240, y=0)

            # Entry boxes
            rightmodelname = ttk.Label(rightplayerframe)
            rightmodelname.place(height=20, width=rightplayerframe.winfo_width() * 0.5, x=0, y=20)
            reg = mainframe.register(callback)
            rightamount = ttk.Entry(rightplayerframe, validate="key", validatecommand=(reg, '%P'))
            rightamount.place(height=20, width=rightplayerframe.winfo_width() * 0.5,
                              x=rightplayerframe.winfo_width() * 0.5,
                              y=20)
            rightamount.bind("<Return>", lambda _: update_record(player2))
            rightgame_scroll = ttk.Scrollbar(rightplayerframe)
            rightgame_scroll.pack(side=RIGHT, fill=Y)
            root.update()
            sroll_width = rightgame_scroll.winfo_width()

            rightgame_scroll = ttk.Scrollbar(rightplayerframe, orient='horizontal')
            rightgame_scroll.pack(side=BOTTOM, fill=X)
            rightselectedbutton = ttk.Button(rightplayerframe, text='confirm', command=lambda: update_record(player2))
            rightselectedbutton.pack()
            rightselectedbutton.place(height=20, width=rightplayerframe.winfo_width(), x=0, y=40)
            my_game2 = ttk.Treeview(rightplayerframe, yscrollcommand=rightgame_scroll.set,
                                    xscrollcommand=rightgame_scroll.set)
            my_game2.pack(fill=BOTH)
            my_game2.place(height=rightplayerframe.winfo_height() - 40,
                           width=rightplayerframe.winfo_width() - sroll_width,
                           x=0, y=60)
            my_game2.bind('<<TreeviewSelect>>', lambda _: select_record(player2))
            rightgame_scroll.config(command=my_game2.yview)
            rightgame_scroll.config(command=my_game2.xview)
            my_game2['columns'] = ('unitname', 'amount')
            my_game2.column("#0", width=0, stretch=NO)
            my_game2.column("unitname", anchor=CENTER, width=80)
            my_game2.column("amount", anchor=CENTER, width=80)
            my_game2.heading("#0", text="", anchor=CENTER)
            my_game2.heading("unitname", text="Name", anchor=CENTER)
            my_game2.heading("amount", text="Amount", anchor=CENTER)
            a = 0
            for i in player2.units.modelsavailable:
                my_game2.insert(parent='', index='end', iid=a, text='', values=(i[0].name, 0))
                a = a + 1
            rightconfirmbutton = ttk.Button(rightplayerframe, text='finished',
                                            command=lambda: selectModels(player2, my_game2))
            rightconfirmbutton.pack()
            rightconfirmbutton.place(height=20, width=rightplayerframe.winfo_width(),
                                     x=0, y=rightplayerframe.winfo_height() - 20)
        if player2.state == 'weaponselection':
            clearFrame(rightplayerframe)
            rightmodelnametxt = ttk.Label(rightplayerframe, text="model name")
            rightmodelnametxt.place(height=20, width=rightplayerframe.winfo_width() * 0.33, x=0, y=0)

            rightamounttxt = ttk.Label(rightplayerframe, text="weapon name")
            rightamounttxt.place(height=20, width=rightplayerframe.winfo_width() * 0.33,
                                 x=rightplayerframe.winfo_width() * 0.33, y=0)

            rightweapontxt = ttk.Label(rightplayerframe, text="amount")
            rightweapontxt.place(height=20, width=rightplayerframe.winfo_width() * 0.33,
                                 x=rightplayerframe.winfo_width() * 0.66, y=0)

            # Entry boxes
            rightmodelname = ttk.Label(rightplayerframe, text="model name")
            rightmodelname.place(height=20, width=rightplayerframe.winfo_width() * 0.33, x=0, y=20)
            rightweaponname = ttk.Label(rightplayerframe, text="weapon name")
            rightweaponname.place(height=20, width=rightplayerframe.winfo_width() * 0.33,
                                  x=rightplayerframe.winfo_width() * 0.33, y=20)

            reg = mainframe.register(callback)
            rightamount = ttk.Entry(rightplayerframe, validate="key", validatecommand=(reg, '%P'))
            rightamount.place(height=20, width=rightplayerframe.winfo_width() * 0.33,
                              x=rightplayerframe.winfo_width() * 0.66,
                              y=20)

            rightamount.bind("<Return>", lambda _: update_weapon(player2))
            rightselectedbutton = ttk.Button(rightplayerframe, text='confirm', command=lambda: update_weapon(player2))
            rightselectedbutton.pack()
            rightselectedbutton.place(height=20, width=rightplayerframe.winfo_width(), x=0, y=40)
            rightmodellist = ttk.Treeview(rightplayerframe)
            rightmodellist.pack()
            rightmodellist.place(height=(rightplayerframe.winfo_height() - 40) / 2,
                                 width=rightplayerframe.winfo_width(),
                                 x=0, y=60)
            rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player2))
            rightmodellist['columns'] = ('modelname', 'modelnumber')
            rightmodellist.column("#0", width=0, stretch=NO)
            rightmodellist.column("modelname", anchor=CENTER, width=80)
            rightmodellist.column("modelnumber", anchor=CENTER, width=80)
            rightmodellist.heading("#0", text="", anchor=CENTER)
            rightmodellist.heading("modelname", text="Model", anchor=CENTER)
            rightmodellist.heading("modelnumber", text="Number", anchor=CENTER)
            rightweaponlist = ttk.Treeview(rightplayerframe)
            rightweaponlist.pack()
            rightweaponlist.place(height=((rightplayerframe.winfo_height() - 40) / 2) - 40,
                                  width=rightplayerframe.winfo_width(),
                                  x=0, y=((rightplayerframe.winfo_height() - 40) / 2) + 60)
            rightweaponlist.bind('<<TreeviewSelect>>', lambda _: select_weapon(player2))
            rightweaponlist['columns'] = ('weapon', 'count')
            rightweaponlist.column("#0", width=0, stretch=NO)
            rightweaponlist.column("weapon", anchor=CENTER, width=80)
            rightweaponlist.column("count", anchor=CENTER, width=80)
            rightweaponlist.heading("#0", text="", anchor=CENTER)
            rightweaponlist.heading("weapon", text="Weapon", anchor=CENTER)
            rightweaponlist.heading("count", text="Count", anchor=CENTER)
            rightweaponlist.bind("<Return>", lambda _: update_weapon(player2))
            rightfinishweaponsbutton = ttk.Button(rightplayerframe, text='finish setting up weapons',
                                                  command=lambda: finishweaponsselection(player2))
            rightfinishweaponsbutton.pack()
            rightfinishweaponsbutton.place(y=rightplayerframe.winfo_height() - 40, x=0, height=40,
                                           width=rightplayerframe.winfo_width())
            a = 0
            count = 1
            lastname = player2.models[0].type.name
            for i in player2.models:
                # (i)
                if i.type.name != lastname: count = 1
                rightmodellist.insert(parent='', index='end', iid=a, text='', values=(i.type.name, count))
                lastname = i.type.name
                count += 1
                a += 1
            # confirmbutton = Button(rightplayerframe, text='finished', command=lambda: selectModels(player2, my_game))
            # confirmbutton.pack()
            # confirmbutton.place(height=20, width=rightplayerframe.winfo_width(),
            # x=0, y=rightplayerframe.winfo_height() - 20)
        if player2.state != 'ready':
            player2.state = ''

    if status == 'begin':
        root.update()

        global Var1, Var2
        Var1 = IntVar()
        Var2 = IntVar()
        mainframe.grid_columnconfigure(0, minsize=mainframe.winfo_width() / 2)
        mainframe.grid_columnconfigure(1, minsize=mainframe.winfo_width() / 2)

        ChkBttn = ttk.Checkbutton(mainframe, text="Mathhamer mode (średnie wartości rzutów)", variable=Var1,
                                  command=set_math)
        # ChkBttn.grid(row=3, column=0,sticky='ew')
        label = ttk.Label(mainframe, text='Wybierz zaczynającego gracza:')
        label.grid(row=0, column=0, sticky='ew')
        RBttn = ttk.Radiobutton(mainframe, text="Gracz lewy", variable=Var2,
                                value=1)
        RBttn2 = ttk.Radiobutton(mainframe, text="Gracz prawy", variable=Var2,
                                 value=2)
        reg = mainframe.register(callback)
        rangeentry = ttk.Entry(mainframe, validate="key", validatecommand=(reg, '%P'))
        rangetxt = ttk.Label(mainframe, text='Wybierz dystans początkowy')
        rangeentry.insert(END, '100')
        rangetxt.grid(row=0, column=1, sticky='ew')
        rangeentry.grid(row=1, column=1, sticky='ew')
        RBttn.grid(row=1, column=0, sticky='ew')
        RBttn2.grid(row=2, column=0, sticky='ew')
        stylelabel = ttk.Label(mainframe, text="Wybierz styl UI")
        stylelabel.grid(row=3, column=0, sticky='ew')
        style = ThemedStyle(root)
        styleselect = ttk.Combobox(mainframe, values=style.theme_names())
        styleselect.bind('<<ComboboxSelected>>', lambda _: select_theme(styleselect.get()))
        styleselect.grid(row=4, column=0, sticky='ew')
        turnlimitlabel = ttk.Label(mainframe, text = "Ustal limit tur (zostaw 0 by zostawić bez limitu)")
        turnlimitlabel.grid(row = 2, column=1, sticky='ew')
        turnlimitentry = ttk.Entry(mainframe, validate="key", validatecommand=(reg, '%P'))
        turnlimitentry.insert(END, 0)
        turnlimitentry.grid(row=3, column=1, sticky='ew')
        startButton = ttk.Button(diceframe, text="Begin", command=lambda: startbattle(int(rangeentry.get()),
                                 int(turnlimitentry.get())))
        startButton.place(x=0, y=0, width=diceframe.winfo_width(), height=diceframe.winfo_height())
        status = 'selection'
        phaselabel['text'] = 'Game configuration'
        playerlabel['text'] = 'Please select units and game parameters'
        refreshUI()
    if status == 'game':
        phaselabel['text'] = phase + ' phase'
        global activeplayer
        if activeplayer == player1:
            playerlabel['text'] = 'player1'
        if activeplayer == player2:
            playerlabel['text'] = 'player2'
        clearFrame(mainframe)
        clearFrame(leftplayerframe)
        clearFrame(rightplayerframe)
        clearFrame(diceframe)
        #distlabel = ttk.Label(diceframe, text=f"distance = {distance}",  font=("Arial", 60), anchor="center")
        #distlabel.pack(fill=BOTH)

        distdisp = Canvas(diceframe, background = '#464646')
        s = ThemedStyle()
        distdisp.create_text(int(diceframe.winfo_width()/2),20, fill="#a6a6a6", font="Times 20 italic bold",
                           text=f"{distance}\"")
        distdisp.create_line(0, int(diceframe.winfo_height()/2), int(diceframe.winfo_width()), int(diceframe.winfo_height()/2), arrow=BOTH, fill = 'white')
        distdisp.pack(fill=BOTH)
        # print(distance)
        if phase == 'movement':
            moveVar.set(1)
            RBttn = ttk.Radiobutton(mainframe, text="Stay stationary", variable=moveVar,
                                    value=1)
            RBttn2 = ttk.Radiobutton(mainframe, text="Move ", variable=moveVar,
                                     value=2)
            RBttn3 = ttk.Radiobutton(mainframe, text="Advance", variable=moveVar,
                                     value=3)
            mainframe.grid_remove()
            mainframe.grid_columnconfigure(0, weight=2, minsize=0)
            mainframe.grid_columnconfigure(1, weight=1, minsize=0)
            mainframe.grid_columnconfigure(2, weight=1, minsize=0)
            RBttn.grid(row=1, column=0, sticky='ew')
            RBttn2.grid(row=2, column=0, sticky='ew')
            RBttn3.grid(row=3, column=0, sticky='ew')
            confirmmove = ttk.Button(mainframe, text='confirm', command=lambda: confirmmovement(activeplayer))
            confirmmove.grid(row=4, column=0, sticky='ew')
            minmovetext = ttk.Label(mainframe, text='min movement')
            maxmovetext = ttk.Label(mainframe, text='max movement')
            minmovelabel = ttk.Label(mainframe, text='0')
            maxmovelabel = ttk.Label(mainframe)
            minmovetext.grid(row=0, column=1, sticky='ew')
            maxmovetext.grid(row=0, column=2, sticky='ew')
            minmovelabel.grid(row=1, column=1, sticky='ew')
            maxmovelabel.grid(row=1, column=2, sticky='ew')
            reg = mainframe.register(callback)
            distanceentry = ttk.Entry(mainframe, state='disabled',validate = "key", validatecommand=(reg, '%P'))
            distanceentry.grid(row=2, column=1, columnspan=2, sticky='ew')
            confirmdistance = ttk.Button(mainframe, text='move', command=lambda: confirmmovedist(activeplayer))
            confirmdistance.grid(row=3, column=1, columnspan=2, sticky='ew')
            pass
        if phase == 'shoot':
            if activeplayer == player1:
                leftplayershoot = ttkw.CheckboxTreeview(leftplayerframe)
                leftplayershoot.pack()
                leftplayershoot.place(width=leftplayerframe.winfo_width(), height=leftplayerframe.winfo_height() - 40,
                                      x=0,
                                      y=0)
                idmodel = 0
                idweapon = 0
                for model in player1.models:
                    if model.destroyed == False:
                        leftplayershoot.insert("", "end", str(idmodel), text=model.type.name)
                        modelweaponarray = model.weapons
                        a = 0
                        for i in player1.units.weapons:
                            if len(modelweaponarray) != 0:
                                for x in range((modelweaponarray[a])[0]):
                                    if i.range != "Melee":
                                        if int(i.range[:-1]) >= int(distance) and (player1.has_advanced == False or (
                                                player1.has_advanced == True and 'Assault' in i.type)):
                                            leftplayershoot.insert(parent=str(idmodel), index='end',
                                                                   iid=str(idmodel) + '-' + str(a) + '-' + str(
                                                                       idweapon),
                                                                   text=i.name)
                                    idweapon += 1
                                a += 1
                                idweapon = 0
                        idmodel += 1
                leftplayershootbutton = ttk.Button(leftplayerframe, text='shoot', command=lambda: shoot(player1))
                leftplayershootbutton.pack()
                leftplayershootbutton.place(width=leftplayerframe.winfo_width(), height=40,
                                            x=0,
                                            y=leftplayerframe.winfo_height() - 40)
                rightmodellist = ttk.Treeview(rightplayerframe)
                rightmodellist.pack()
                rightmodellist.place(height=rightplayerframe.winfo_height(), width=rightplayerframe.winfo_width(),
                                     x=0, y=0)
                # rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
                rightmodellist['columns'] = ('modelname', 'modelhp', 'modelmaxhp')
                rightmodellist.column("#0", width=0, stretch=NO)
                rightmodellist.column("modelname", anchor=CENTER, width=80)
                rightmodellist.column("modelhp", anchor=CENTER, width=80)
                rightmodellist.column("modelmaxhp", anchor=CENTER, width=80)
                rightmodellist.heading("#0", text="", anchor=CENTER)
                rightmodellist.heading("modelname", text="Model", anchor=CENTER)
                rightmodellist.heading("modelhp", text='Current HP', anchor=CENTER)
                rightmodellist.heading("modelmaxhp", text='Max Hp', anchor=CENTER)
                a = 0
                for i in player2.models:
                    rightmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.wounds, i.type.maxw))
                    a += 1
            if activeplayer == player2:
                rightplayershoot = ttkw.CheckboxTreeview(rightplayerframe)
                rightplayershoot.pack()
                rightplayershoot.place(width=rightplayerframe.winfo_width(),
                                       height=rightplayerframe.winfo_height() - 40,
                                       x=0,
                                       y=0)
                idmodel = 0
                idweapon = 0
                for model in player2.models:
                    if model.destroyed == False:
                        rightplayershoot.insert("", "end", str(idmodel), text=model.type.name)
                        modelweaponarray = model.weapons
                        a = 0
                        for i in player2.units.weapons:
                            if len(modelweaponarray) != 0:
                                for x in range((modelweaponarray[a])[0]):
                                    if i.range != "Melee":
                                        if int(i.range[:-1]) >= int(distance) and (player2.has_advanced == False or (
                                                player2.has_advanced == True and 'Assault' in i.type)):
                                            rightplayershoot.insert(parent=str(idmodel), index='end',
                                                                    iid=str(idmodel) + '-' + str(a) + '-' + str(
                                                                        idweapon),
                                                                    text=i.name)
                                    idweapon += 1
                                a += 1
                                idweapon = 0
                        idmodel += 1
                rightplayershootbutton = ttk.Button(rightplayerframe, text='shoot', command=lambda: shoot(player2))
                rightplayershootbutton.pack()
                rightplayershootbutton.place(width=rightplayerframe.winfo_width(), height=40,
                                             x=0,
                                             y=rightplayerframe.winfo_height() - 40)
                leftmodellist = ttk.Treeview(leftplayerframe)
                leftmodellist.pack()
                leftmodellist.place(height=leftplayerframe.winfo_height(), width=leftplayerframe.winfo_width(),
                                    x=0, y=0)
                # rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
                leftmodellist['columns'] = ('modelname', 'modelhp', 'modelmaxhp')
                leftmodellist.column("#0", width=0, stretch=NO)
                leftmodellist.column("modelname", anchor=CENTER, width=80)
                leftmodellist.column("modelhp", anchor=CENTER, width=80)
                leftmodellist.column("modelmaxhp", anchor=CENTER, width=80)
                leftmodellist.heading("#0", text="", anchor=CENTER)
                leftmodellist.heading("modelname", text="Model", anchor=CENTER)
                leftmodellist.heading("modelhp", text='Current HP', anchor=CENTER)
                leftmodellist.heading("modelmaxhp", text='Max Hp', anchor=CENTER)
                a = 0
                for i in player1.models:
                    leftmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.wounds, i.type.maxw))
                    a += 1
        if phase == 'charge':
            if activeplayer.has_advanced or distance < 1 or distance > 12:
                activeplayer.has_charged = False
                log(f"{activeplayer.name} cannot charge, continuing")
                switchPlayer()
            else:
                chargeyesbutton = ttk.Button(mainframe, text='yes', command=lambda: docharge(activeplayer))
                chargenobutton = ttk.Button(mainframe, text='no', command=lambda: dontcharge(activeplayer))
                chargelabel = ttk.Label(mainframe, text="Do you want to charge?")
                chargelabel.grid(row=0, column=0, columnspan=2)
                chargeyesbutton.grid(row=1, column=0)
                chargenobutton.grid(row=1, column=1)
            pass
        if phase == 'melee':
            log('went into melee')
            if distance > 1:
                log('units too far, melee cannot proceed')
                switchPlayer()


            elif activeplayer == player1:
                leftplayermelee = ttkw.CheckboxTreeview(leftplayerframe)
                leftplayermelee.pack()
                leftplayermelee.place(width=leftplayerframe.winfo_width(), height=leftplayerframe.winfo_height() - 40,
                                      x=0,
                                      y=0)
                idmodel = 0
                idweapon = 0
                for model in player1.models:
                    if model.destroyed == False:
                        leftplayermelee.insert("", "end", str(idmodel), text=model.type.name)
                        modelweaponarray = model.weapons
                        a = 0
                        for i in player1.units.weapons:
                            if len(modelweaponarray) != 0:
                                for x in range((modelweaponarray[a])[0]):
                                    if i.range == "Melee":
                                        leftplayermelee.insert(parent=str(idmodel), index='end',
                                                               iid=str(idmodel) + '-' + str(a) + '-' + str(
                                                                   idweapon),
                                                               text=i.name)
                                    idweapon += 1
                                a += 1
                                idweapon = 0
                        idmodel += 1
                leftplayermeleebutton = ttk.Button(leftplayerframe, text='melee', command=lambda: melee(player1))
                leftplayermeleebutton.pack()
                leftplayermeleebutton.place(width=leftplayerframe.winfo_width(), height=40,
                                            x=0,
                                            y=leftplayerframe.winfo_height() - 40)
                rightmodellist = ttk.Treeview(rightplayerframe)
                rightmodellist.pack()
                rightmodellist.place(height=rightplayerframe.winfo_height(), width=rightplayerframe.winfo_width(),
                                     x=0, y=0)
                # rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
                rightmodellist['columns'] = ('modelname', 'modelhp', 'modelmaxhp')
                rightmodellist.column("#0", width=0, stretch=NO)
                rightmodellist.column("modelname", anchor=CENTER, width=80)
                rightmodellist.column("modelhp", anchor=CENTER, width=80)
                rightmodellist.column("modelmaxhp", anchor=CENTER, width=80)
                rightmodellist.heading("#0", text="", anchor=CENTER)
                rightmodellist.heading("modelname", text="Model", anchor=CENTER)
                rightmodellist.heading("modelhp", text='Current HP', anchor=CENTER)
                rightmodellist.heading("modelmaxhp", text='Max Hp', anchor=CENTER)
                a = 0
                for i in player2.models:
                    rightmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.wounds, i.type.maxw))
                    a += 1
            elif activeplayer == player2:
                rightplayermelee = ttkw.CheckboxTreeview(rightplayerframe)
                rightplayermelee.pack()
                rightplayermelee.place(width=rightplayerframe.winfo_width(),
                                       height=rightplayerframe.winfo_height() - 40,
                                       x=0,
                                       y=0)
                idmodel = 0
                idweapon = 0
                for model in player2.models:
                    if model.destroyed == False:
                        rightplayermelee.insert("", "end", str(idmodel), text=model.type.name)
                        modelweaponarray = model.weapons
                        a = 0
                        for i in player2.units.weapons:
                            if len(modelweaponarray) != 0:
                                for x in range((modelweaponarray[a])[0]):
                                    if i.range == "Melee":
                                        rightplayermelee.insert(parent=str(idmodel), index='end',
                                                                iid=str(idmodel) + '-' + str(a) + '-' + str(
                                                                    idweapon),
                                                                text=i.name)
                                    idweapon += 1
                                a += 1
                                idweapon = 0
                        idmodel += 1
                rightplayermeleebutton = ttk.Button(rightplayerframe, text='melee', command=lambda: melee(player2))
                rightplayermeleebutton.pack()
                rightplayermeleebutton.place(width=rightplayerframe.winfo_width(), height=40,
                                             x=0,
                                             y=rightplayerframe.winfo_height() - 40)
                leftmodellist = ttk.Treeview(leftplayerframe)
                leftmodellist.pack()
                leftmodellist.place(height=leftplayerframe.winfo_height(), width=leftplayerframe.winfo_width(),
                                    x=0, y=0)
                # rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
                leftmodellist['columns'] = ('modelname', 'modelhp', 'modelmaxhp')
                leftmodellist.column("#0", width=0, stretch=NO)
                leftmodellist.column("modelname", anchor=CENTER, width=80)
                leftmodellist.column("modelhp", anchor=CENTER, width=80)
                leftmodellist.column("modelmaxhp", anchor=CENTER, width=80)
                leftmodellist.heading("#0", text="", anchor=CENTER)
                leftmodellist.heading("modelname", text="Model", anchor=CENTER)
                leftmodellist.heading("modelhp", text='Current HP', anchor=CENTER)
                leftmodellist.heading("modelmaxhp", text='Max Hp', anchor=CENTER)
                a = 0
                for i in player1.models:
                    leftmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.wounds, i.type.maxw))
                    a += 1
    if status == 'summary':
        clearFrame(mainframe)
        clearFrame(leftplayerframe)
        clearFrame(rightplayerframe)
        clearFrame(diceframe)
        phaselabel['text'] = 'Game finished'

        if player1.unitcount == 0:
            victor = player2
        if player2.unitcount == 0:
            victor = player1
        if player1.points_lost > player2.points_lost:
            victor = player2
        elif player1.points_lost < player2.points_lost:
            victor = player1
        else:
            victor = secondplayer
        playerlabel['text'] = f'{victor} victory'
        leftmodellist = ttk.Treeview(leftplayerframe)
        leftmodellist.tag_configure('destroyed', background='red')
        leftmodellist.pack()
        leftmodellist.place(height=leftplayerframe.winfo_height(), width=leftplayerframe.winfo_width(),
                            x=0, y=0)
        # rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
        leftmodellist['columns'] = ('modelname', 'value')
        leftmodellist.column("#0", width=0, stretch=NO)
        leftmodellist.column("modelname", anchor=CENTER, width=80)
        leftmodellist.column("value", anchor=CENTER, width=80)
        leftmodellist.heading("#0", text="", anchor=CENTER)
        leftmodellist.heading("modelname", text="Model", anchor=CENTER)
        leftmodellist.heading("value", text='Value', anchor=CENTER)
        a = 0
        for i in player1.models:
            if i.destroyed:
                leftmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.type.price),
                                     tags='destroyed')
            else:
                leftmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.type.price))
            a += 1

        rightmodellist = ttk.Treeview(rightplayerframe)
        rightmodellist.tag_configure('destroyed', background='red')
        rightmodellist.pack()
        rightmodellist.place(height=rightplayerframe.winfo_height(), width=rightplayerframe.winfo_width(),
                             x=0, y=0)
        # rightmodellist.bind('<<TreeviewSelect>>', lambda _: select_model(player1))
        rightmodellist['columns'] = ('modelname', 'value', 'modelmaxhp')
        rightmodellist.column("#0", width=0, stretch=NO)
        rightmodellist.column("modelname", anchor=CENTER, width=80)
        rightmodellist.column("value", anchor=CENTER, width=80)
        rightmodellist.heading("#0", text="", anchor=CENTER)
        rightmodellist.heading("modelname", text="Model", anchor=CENTER)
        rightmodellist.heading("value", text='Value', anchor=CENTER)
        a = 0
        for i in player2.models:
            if i.destroyed:
                rightmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.type.price),
                                      tags=('destroyed',))
            else:
                rightmodellist.insert(parent='', index='end', iid=a, values=(i.type.name, i.type.price))
            a += 1
        resetbutton = ttk.Button(mainframe, text="start over?", command=reset)
        resetbutton.pack(fill=BOTH)
        pass


def reset():
    clearFrame(mainframe)
    clearFrame(diceframe)
    clearFrame(leftplayerframe)
    clearFrame(rightplayerframe)
    logtext.delete('1.0', END)
    loadResources()
    refreshUI()


def cBoxLoad(cboxin, cboxout):
    cboxin['state'] = 'disabled'
    name = cboxin.get()
    cboxout['state'] = 'disabled'
    cboxout['values'] = loadUnitsFaction(name)
    cboxout['state'] = 'normal'
    cboxin['state'] = 'normal'


def nextPhase():
    global phase, turn, status
    if phase == 'movement':
        phase = 'shoot'
    elif phase == 'shoot':
        phase = 'charge'
    elif phase == 'charge':
        phase = 'melee'
    elif phase == 'melee':
        turn += 1
        if turn < maxturns:
            phase = 'movement'
        else:
            status = 'summary'
    refreshUI()


def set_math():
    global mathhammer
    mathhammer = bool(Var1.get())


def startbattle(startdist, turnlimit):
    global firstplayer, secondplayer, status, phase, activeplayer, distance, maxturns
    if player1.state != 'ready' or player2.state != 'ready':
        messagebox.showwarning(title='brak jednostek', message='obie strony muszą wybrać jdenostki')
        return
    if Var2.get() == 1:
        firstplayer = player1
        secondplayer = player2
    else:
        firstplayer = player2
        secondplayer = player1
    status = 'game'
    phase = 'movement'
    distance = startdist
    maxturns = turnlimit
    activeplayer = firstplayer
    refreshUI()


def selectUnit(player, name, label, button):
    player.units = findunit(name)
    text = f'{player.units}'
    a = ''
    print()
    label.config(text=text)
    LoadedUnits.clear()
    button['state'] = 'normal'


def loadUnitsFaction(factionname):
    faction_id = factions.loc[factions['name'] == factionname]
    faction_id = faction_id.iloc[0][0]
    # unitlist = unitlist.sort_values(axis = 1, by=['name'])
    return unitlist.loc[unitlist['faction_id'] == faction_id].sort_values(by='name')['name'].to_list()


def callback(input):
    if input.isdigit():
        print(input)
        return True
    else:
        print(input)
        return False


if __name__ == '__main__':
    loadResources()
    LoadedUnits = []
    root = Tk()

    root.geometry("1920x1000")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _: exit(0))
    root.resizable(width=0, height=0)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window = MainWindow(root)
    headframe = ttk.Frame(root, width=screen_width, height=screen_height * 0.25)
    # style = ThemedStyle(headframe)
    # style.set_theme("equilux")
    headframe.pack()
    headframe.place(height=screen_height * 0.25, width=screen_width, x=0, y=0)
    leftplayerframe = ttk.Frame(root)
    leftplayerframe.pack()
    leftplayerframe.place(height=screen_height * 0.75, width=screen_width * 0.25, x=0, y=screen_height * 0.25)
    leftplayerframe.pack_propagate(0)
    rightplayerframe = ttk.Frame(root)
    rightplayerframe.pack()
    rightplayerframe.place(height=screen_height * 0.75, width=screen_width * 0.25, x=screen_width * 0.75,
                           y=screen_height * 0.25)
    diceframe = ttk.Frame(root, width=screen_width * 0.25, height=screen_height * 0.10)
    diceframe.pack()
    diceframe.place(height=screen_height * 0.1, width=screen_width * 0.5, x=screen_width * 0.25, y=screen_height * 0.8)
    mainframe = ttk.Frame(root, width=screen_width * 0.5, height=screen_height * 0.55)
    mainframe.pack()
    mainframe.place(height=screen_height * 0.55, width=screen_width * 0.5, x=screen_width * 0.25,
                    y=screen_height * 0.25)
    root.update()
    phaselabel = ttk.Label(headframe, font=("Arial", 60), anchor="center")
    phaselabel.place(x=0, y=0, width=headframe.winfo_width(), height=int(headframe.winfo_height() * 2 / 3))
    playerlabel = ttk.Label(headframe, font=("Arial", 40), anchor="center")
    playerlabel.place(x=0, y=int(headframe.winfo_height() * 2 / 3), width=headframe.winfo_width(),
                      height=int(headframe.winfo_height() * 1 / 3))
    logframe = ttk.Frame(root, width=screen_width * 0.5, height=screen_height * 0.1)
    logframe.place(x=screen_width * 0.25, y=screen_height * 0.9, width=screen_width * 0.5, height=screen_height * 0.1)
    root.update()
    logtext = scrolledtext.ScrolledText(logframe,
                                        font=("Times New Roman",
                                              15), state='disabled')
    logtext.place(x=0, y=0, width=screen_width * 0.5, height=screen_height * 0.1)
    refreshUI()
    root.mainloop()
