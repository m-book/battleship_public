from constant import *
from model.user import *
import wx
import math

PHASE = ((0, 'NOTHING'), (1, 'SHIP_INIT'), (2, 'ENEMY'), (3, 'IS_ALIVE'), (4, 'ATTACK'), (5, 'MOVE'))


def ship_init_phase_action(main, event):
    event_id = event.GetId()
    if main.user.warship.enable == False:
        flag = main.battle_field.initiate_ship(FIELD_WARSHIP, event_id)
        if flag is True:
            main.user.warship.enable = True
            event.GetEventObject().SetLabel('W')
    elif main.user.destroyer.enable == False:
        flag = main.battle_field.initiate_ship(FIELD_DESTROYER, event_id)
        if flag is True:
            main.user.destroyer.enable = True
            event.GetEventObject().SetLabel('D')
    elif main.user.submarine.enable == False:
        flag = main.battle_field.initiate_ship(FIELD_SUBMARINE, event_id)
        if flag is True:
            main.user.submarine.enable = True
            event.GetEventObject().SetLabel('S')
    # if main.user.warship.enable and main.user.destroyer.enable and main.user.submarine.enable:
        # main.user.phase = PHASE[3]
        # return
        if main.user.is_host:
            main.finish_ship_init()
        else:
            main.send_data(CONNECTION_SHIP_INIT, {})


def ship_alive_phase_action(main, event):
    from layout import set_button_color
    event_id = event.GetId()
    cell = main.battle_field.get_field_cell_by_id(event_id)
    if cell.status is FIELD_NOTHING:
        return
    point_list = main.battle_field.get_ship_enable_attack_position(cell.cell_id)
    for point in point_list:
        enable_cell = main.battle_field.get_field_cell_by_position(point[0], point[1])
        button = wx.FindWindowById(enable_cell.cell_id)
        set_button_color(button, 'RED')
        # button.SetBackgroundColour("RED")
        # button.SetForegroundColour("RED")
        main.battle_field.selected_enable_attack_list.append(enable_cell.cell_id)
    main.battle_field.selected_cell_id = event_id
    main.change_phase(PHASE[4])


def ship_attack_phase_action(main, event):
    from layout import set_button_color
    event_id = event.GetId()
    cell = main.battle_field.get_field_cell_by_id(event_id)
    if event_id in main.battle_field.selected_enable_attack_list:
        data = {
            'is_attack': True,
            'attack_cell_id': event_id
        }
        main.send_data(CONNECTION_PLAYER_ACTION, data)
        reset_select(main)
        main.change_phase(PHASE[2])
        if main.user.is_host is True:
            main.player_change()
        return
    if event_id is main.battle_field.selected_cell_id:
        reset_select(main)
        point_list = main.battle_field.get_ship_enable_move_position(cell.cell_id)
        for point in point_list:
            enable_cell = main.battle_field.get_field_cell_by_position(point[0], point[1])
            button = wx.FindWindowById(enable_cell.cell_id)
            set_button_color(button, 'GREEN')
            # button.SetBackgroundColour("GREEN")
            # button.SetForegroundColour("GREEN")
            main.battle_field.selected_enable_move_list.append(enable_cell.cell_id)
        main.change_phase(PHASE[5])
        main.battle_field.selected_cell_id = event_id
        return
    reset_select(main)


def ship_move_phase_action(main, event):
    event_id = event.GetId()
    cell = main.battle_field.get_field_cell_by_id(event_id)
    if event_id in main.battle_field.selected_enable_move_list:
        pre_cell = main.battle_field.get_field_cell_by_id(main.battle_field.selected_cell_id)
        temp_status = pre_cell.status
        pre_cell.status = FIELD_NOTHING
        button = wx.FindWindowById(pre_cell.cell_id)
        button.SetLabel('')
        cell.status = temp_status
        button = wx.FindWindowById(cell.cell_id)
        ship_name = ''
        if cell.status is FIELD_WARSHIP:
            button.SetLabel('W')
            ship_name = '戦艦'
        elif cell.status is FIELD_DESTROYER:
            button.SetLabel('D')
            ship_name = '駆逐艦'
        elif cell.status is FIELD_SUBMARINE:
            button.SetLabel('S')
            ship_name = '潜水艦'
        move_x = cell.x - pre_cell.x
        move_y = cell.y - pre_cell.y
        if move_x is not 0:
            if move_x < 0:
                direction = '西'
            else:
                direction = '東'
            distance = abs(move_x)
        else:
            if move_y < 0:
                direction = '北'
            else:
                direction = '南'
            distance = abs(move_y)
        reset_select(main)
        message = '{0}が{1}に{2}移動'.format(ship_name, direction, distance)
        data = {
            'is_attack': False,
            'move_message': message
        }
        main.send_data(CONNECTION_PLAYER_ACTION, data)
        reset_select(main)
        main.change_phase(PHASE[2])
        if main.user.is_host:
            main.player_change()
        return
    reset_select(main)


def reset_select(main):
    from layout import set_button_color
    main.change_phase(PHASE[3])
    main.battle_field.selected_cell_id = -1
    main.battle_field.selected_enable_attack_list.clear()
    for i in range(main.field_seize_x * main.field_seize_y):
        button = wx.FindWindowById(i)
        set_button_color(button, 'BLUE')
        # button.SetBackgroundColour("BLUE")
        # button.SetForegroundColour("BLUE")


def check_ship_attacked(main, attack_point):
    cell = main.battle_field.get_field_cell_by_id(attack_point)
    button = wx.FindWindowById(cell.cell_id)
    if cell.status is FIELD_WARSHIP:
        ship = main.user.get_ship_by_ship_id(FIELD_WARSHIP)
        ship.hp -= 1
        if ship.hp <= 0:
            cell.status = FIELD_NOTHING
            button.SetLabel("")
        result = "戦艦が被弾", FIELD_WARSHIP, ship.hp
    elif cell.status is FIELD_DESTROYER:
        ship = main.user.get_ship_by_ship_id(FIELD_DESTROYER)
        ship.hp -= 1
        if ship.hp <= 0:
            cell.status = FIELD_NOTHING
            button.SetLabel("")
        result = "駆逐艦が被弾", FIELD_DESTROYER, ship.hp
    elif cell.status is FIELD_SUBMARINE:
        ship = main.user.get_ship_by_ship_id(FIELD_SUBMARINE)
        ship.hp -= 1
        if ship.hp <= 0:
            cell.status = FIELD_NOTHING
            button.SetLabel("")
        result = "潜水艦が被弾", FIELD_SUBMARINE, ship.hp
    else:
        result = "被弾なし", FIELD_NOTHING, -1
    return result


def check_observe_attack(main, attack_point):
    cell = main.battle_field.get_field_cell_by_id(attack_point)
    observed_ship_id_list = main.battle_field.get_ship_enable_observe_position(cell.x, cell.y)
    result = ""
    for ship_id in observed_ship_id_list:
        if ship_id is FIELD_WARSHIP:
            if result != "":
                result += ", "
            result += "戦艦が水しぶきを確認"
        elif ship_id is FIELD_DESTROYER:
            if result != "":
                result += ", "
            result += "駆逐艦が水しぶきを確認"
        elif ship_id is FIELD_SUBMARINE:
            if result != "":
                result += ", "
            result += "潜水艦が水しぶきを確認"
    return result





