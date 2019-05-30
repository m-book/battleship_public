import wx
import wx.lib.buttons
from model.user import *
from phase import *
from utility import *


class MainPanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(frame, wx.ID_ANY)


class BattlePanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(600, 600))
        self.main = main
        field_seize_x = main.field_seize_x
        field_seize_y = main.field_seize_y
        battle_sizer = wx.GridSizer(rows=field_seize_x, cols=field_seize_y, hgap=1, vgap=1)
        for i in range(field_seize_x * field_seize_y):
            button = wx.lib.buttons.GenButton(self, i, '')
            button.Bind(wx.EVT_BUTTON, self.click_battle_button)
            set_button_color(button, 'BLUE')
            # button.SetForegroundColour("WHITE")
            # button.SetBackgroundColour("BLUE")
            battle_sizer.Add(button, flag=wx.EXPAND)

        self.SetSizer(battle_sizer)
        battle_sizer.Fit(self)

    def click_battle_button(self, event):
        event_id = event.GetId()
        if self.main.user.phase == PHASE[1]:
            ship_init_phase_action(self.main, event)
            return
        if self.main.user.phase == PHASE[3]:
            ship_alive_phase_action(self.main, event)
            return
        if self.main.user.phase == PHASE[4]:
            ship_attack_phase_action(self.main, event)
            return
        if self.main.user.phase == PHASE[5]:
            ship_move_phase_action(self.main, event)
            return


class SettingPanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(400, 600))
        self.information_panel = InformationPanel(self, main)
        # self.phase_panel = PhasePanel(self)
        # self.own_setting_panel = OwnSettingPanel(self)
        # self.host_ip_panel = HostIPPanel(self, main)
        # self.is_host_panel = IsHostPanel(self, main)
        self.log_panel = LogPanel(self, main)
        self.main = main

        setting_sizer = wx.BoxSizer(wx.VERTICAL)
        setting_sizer.Add(self.information_panel)
        # setting_sizer.Add(self.phase_panel)
        # setting_sizer.Add(self.own_setting_panel)
        # setting_sizer.Add(self.host_ip_panel)
        # setting_sizer.Add(self.is_host_panel)
        setting_sizer.Add(self.log_panel)
        self.SetSizer(setting_sizer)
        setting_sizer.Fit(self)


class InformationPanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(400, 280))
        self.notebook = wx.Notebook(self, wx.ID_ANY, size=(400, 300))
        self.ship_information_panel_dict = {}

        self.user_information_panel = UserInformationPanel(self.notebook, main)
        self.user_information_panel.SetBackgroundColour("WHITE")
        self.notebook.InsertPage(0, self.user_information_panel, "user_info")

    def init_new_user(self, user_id, user_name):
        ship_information_panel = ShipInformationPanel(self.notebook, user_name)
        ship_information_panel.SetBackgroundColour("WHITE")
        self.notebook.InsertPage(1, ship_information_panel, user_name)
        self.ship_information_panel_dict.update({user_id: ship_information_panel})

    def update_ship_information(self, user_id, ship_id, hp):
        ship_information_panel = self.ship_information_panel_dict[user_id]
        ship_information_panel.set_ship_hp(ship_id=ship_id, hp=hp)


class UserInformationPanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(400, 200))
        self.phase_panel = PhasePanel(self)
        self.own_setting_panel = OwnSettingPanel(self)
        self.host_ip_panel = HostIPPanel(self, main)
        self.is_host_panel = IsHostPanel(self, main)

        setting_sizer = wx.BoxSizer(wx.VERTICAL)
        setting_sizer.Add(self.phase_panel)
        setting_sizer.Add(self.own_setting_panel)
        setting_sizer.Add(self.host_ip_panel)
        setting_sizer.Add(self.is_host_panel)
        self.SetSizer(setting_sizer)
        setting_sizer.Fit(self)


class ShipInformationPanel(wx.Panel):
    def __init__(self, frame, name):
        super().__init__(frame, wx.ID_ANY, size=(400, 200))
        self.name_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.name_title_text = wx.StaticText(self.name_panel, wx.ID_ANY, "名前: ")
        self.name_text = wx.StaticText(self.name_panel, wx.ID_ANY, name)
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(self.name_title_text)
        name_sizer.Add(self.name_text)
        self.SetSizer(name_sizer)
        name_sizer.Fit(self)

        self.warship_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.warship_title_text = wx.StaticText(self.warship_panel, wx.ID_ANY, "戦艦: ")
        self.warship_text = wx.StaticText(self.warship_panel, wx.ID_ANY, "3/3")
        warship_sizer = wx.BoxSizer(wx.HORIZONTAL)
        warship_sizer.Add(self.warship_title_text)
        warship_sizer.Add(self.warship_text)
        self.SetSizer(warship_sizer)
        warship_sizer.Fit(self)

        self.destroyer_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.destroyer_title_text = wx.StaticText(self.destroyer_panel, wx.ID_ANY, "駆逐艦: ")
        self.destroyer_text = wx.StaticText(self.destroyer_panel, wx.ID_ANY, "2/2")
        destroyer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        destroyer_sizer.Add(self.destroyer_title_text)
        destroyer_sizer.Add(self.destroyer_text)
        self.SetSizer(destroyer_sizer)
        destroyer_sizer.Fit(self)

        self.submarine_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.submarine_title_text = wx.StaticText(self.submarine_panel, wx.ID_ANY, "潜水艦: ")
        self.submarine_text = wx.StaticText(self.submarine_panel, wx.ID_ANY, "1/1")
        submarine_sizer = wx.BoxSizer(wx.HORIZONTAL)
        submarine_sizer.Add(self.submarine_title_text)
        submarine_sizer.Add(self.submarine_text)
        self.SetSizer(submarine_sizer)
        submarine_sizer.Fit(self)

        ship_information_sizer = wx.BoxSizer(wx.VERTICAL)
        ship_information_sizer.Add(self.name_panel)
        ship_information_sizer.Add(self.warship_panel)
        ship_information_sizer.Add(self.destroyer_panel)
        ship_information_sizer.Add(self.submarine_panel)
        self.SetSizer(ship_information_sizer)
        ship_information_sizer.Fit(self)

    def set_ship_hp(self, ship_id, hp):
        if ship_id == FIELD_WARSHIP:
            self.warship_text.SetLabel('{0}/3'.format(hp))
        if ship_id == FIELD_DESTROYER:
            self.destroyer_text.SetLabel('{0}/2'.format(hp))
        if ship_id == FIELD_SUBMARINE:
            self.submarine_text.SetLabel('{0}/1'.format(hp))


class PhasePanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(frame, wx.ID_ANY, size=(400, 50))
        self.phase_title_text = wx.StaticText(self, wx.ID_ANY, "PHASE--")
        self.phase_text = wx.StaticText(self, wx.ID_ANY, PHASE[0][1])
        phase_sizer = wx.BoxSizer(wx.HORIZONTAL)
        phase_sizer.Add(self.phase_title_text)
        phase_sizer.Add(self.phase_text)
        self.SetSizer(phase_sizer)
        phase_sizer.Fit(self)

    def set_text(self, content):
        self.phase_text.SetLabel(content)


class OwnSettingPanel(wx.Panel):
    def __init__(self, frame):
        super().__init__(frame, wx.ID_ANY, size=(400, 50))
        self.name_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.name_title_text = wx.StaticText(self.name_panel, wx.ID_ANY, "名前: ")
        self.name_text = wx.TextCtrl(self.name_panel, wx.ID_ANY, size=(200, 25))
        self.name_text.SetMaxLength(15)
        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(self.name_title_text)
        name_sizer.Add(self.name_text)
        self.SetSizer(name_sizer)
        name_sizer.Fit(self)

        self.own_port_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.own_port_title_text = wx.StaticText(self.own_port_panel, wx.ID_ANY, "自分のポート: ")
        self.own_port_text = wx.TextCtrl(self.own_port_panel, wx.ID_ANY, size=(50, 25))
        self.own_port_text.SetMaxLength(5)
        own_port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        own_port_sizer.Add(self.own_port_title_text)
        own_port_sizer.Add(self.own_port_text)
        self.SetSizer(own_port_sizer)
        own_port_sizer.Fit(self)

        own_setting_sizer = wx.BoxSizer(wx.VERTICAL)
        own_setting_sizer.Add(self.name_panel)
        own_setting_sizer.Add(self.own_port_panel)
        self.SetSizer(own_setting_sizer)
        own_setting_sizer.Fit(self)

    def decide(self):
        self.name_text.SetEditable(False)
        self.own_port_text.SetEditable(False)
        return self.name_text.GetValue(), self.own_port_text.GetValue()


class HostIPPanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(400, 75))
        self.main = main
        self.ip_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.ip_description = wx.StaticText(self.ip_panel, wx.ID_ANY, "ホストのIPアドレス: ")
        self.host_ip_text = wx.TextCtrl(self.ip_panel, wx.ID_ANY, size=(200, 25))
        self.host_ip_text.SetMaxLength(20)
        ip_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ip_sizer.Add(self.ip_description)
        ip_sizer.Add(self.host_ip_text)
        self.SetSizer(ip_sizer)
        ip_sizer.Fit(self)

        self.port_panel = wx.Panel(self, wx.ID_ANY, size=(400, 25))
        self.port_description = wx.StaticText(self.port_panel, wx.ID_ANY, "ホストのポート: ")
        self.host_port_text = wx.TextCtrl(self.port_panel, wx.ID_ANY, size=(50, 25))
        self.host_port_text.SetMaxLength(5)
        port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        port_sizer.Add(self.port_description)
        port_sizer.Add(self.host_port_text)
        self.SetSizer(port_sizer)
        port_sizer.Fit(self)

        self.connection_button = wx.Button(self, wx.ID_ANY, "CONNECT")
        host_ip_sizer = wx.BoxSizer(wx.VERTICAL)
        host_ip_sizer.Add(self.ip_panel)
        host_ip_sizer.Add(self.port_panel)
        host_ip_sizer.Add(self.connection_button)
        self.SetSizer(host_ip_sizer)
        host_ip_sizer.Fit(self)

        self.connection_button.Bind(wx.EVT_BUTTON, self.click_connect_button)

    def get_ip_value(self):
        return self.host_ip_text.GetValue()

    def get_port_value(self):
        return self.host_port_text.GetValue()

    def click_connect_button(self, event):
        name, port = self.main.setting_panel.information_panel.user_information_panel.own_setting_panel.decide()
        self.main.decide_user_setting(name, port)
        self.decide()
        self.main.connection(self.get_ip_value(), int(self.get_port_value()))
        print('connect')

    def decide(self):
        self.host_ip_text.SetEditable(False)
        self.host_port_text.SetEditable(False)
        self.connection_button.Disable()


class IsHostPanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(400, 50))
        self.main = main
        self.is_host_title_text = wx.StaticText(self, wx.ID_ANY, "ホスト: ")
        self.checkbox = wx.CheckBox(self, wx.ID_ANY)
        self.game_start_button = wx.Button(self, wx.ID_ANY, "START")
        is_host_sizer = wx.BoxSizer(wx.HORIZONTAL)
        is_host_sizer.Add(self.is_host_title_text)
        is_host_sizer.Add(self.checkbox)
        is_host_sizer.Add(self.game_start_button)
        self.SetSizer(is_host_sizer)
        is_host_sizer.Fit(self)

        self.game_start_button.Bind(wx.EVT_BUTTON, self.click_start_button)
        self.checkbox.Bind(wx.EVT_CHECKBOX, self.change_checkbox)

    def get_is_host(self):
        return self.checkbox.GetValue()

    def click_start_button(self, event):
        if self.main.user.is_host:
            self.main.send_data(CONNECTION_SHIP_INIT_START, {})
            self.main.change_phase(PHASE[1])

    def change_checkbox(self, event):
        self.checkbox.Disable()
        self.main.user.is_host = True
        self.main.host = Host()
        self.main.user.aes = AESCipher()
        self.main.user.user_id = self.main.host.add_user()
        print('change')
        name, port = self.main.setting_panel.information_panel.user_information_panel.own_setting_panel.decide()
        self.main.decide_user_setting(name, port)
        self.main.receive_system_message('host ip: {0}'.format(get_own_address(port, self.main.user.upnp)))
        self.main.setting_panel.information_panel.init_new_user(self.main.user.user_id, self.main.user.name)


class LogPanel(wx.Panel):
    def __init__(self, frame, main):
        super().__init__(frame, wx.ID_ANY, size=(400, 300))
        self.main = main
        element_array = ()
        self.listbox = wx.ListBox(self, wx.ID_ANY, choices=element_array, size=(400, 250))
        self.message_text = wx.TextCtrl(self, wx.ID_ANY, size=(350, 25))
        self.message_text.SetMaxLength(30)
        self.send_button = wx.Button(self, wx.ID_ANY, "SEND")
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer.Add(self.listbox)
        log_sizer.Add(self.message_text)
        log_sizer.Add(self.send_button)
        self.SetSizer(log_sizer)
        log_sizer.Fit(self)

        self.send_button.Bind(wx.EVT_BUTTON, self.click_send_button)

    def click_send_button(self, event):
        message = self.message_text.GetValue()
        self.main.send_data(CONNECTION_SEND_MESSAGE, message)
        self.message_text.Clear()
        self.receive_message(self.main.user.name, message)

    def receive_message(self, name, message):
        self.listbox.Append('{0}: {1}'.format(name, message))

    def receive_system_message(self, message):
        self.listbox.Append('system: {0}'.format(message))


def set_button_color(button, color):
    button.SetForegroundColour(color)
    button.SetBackgroundColour(color)
    button.SetForegroundColour("WHITE")
