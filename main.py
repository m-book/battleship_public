import wx
import wx.lib.buttons
import time

from model.battle_field import *
from connection import *
from utility import *
from layout import *
from phase import *


class Main:
    server_thread = None
    connection_list = []
    listen_thread_list = []
    other_user_dict = {}
    host = None

    def __init__(self):
        self.field_seize_x = 5
        self.field_seize_y = 5

        self.application = wx.App()
        self.frame = wx.Frame(None, wx.ID_ANY, "バトルシップゲーム", size=(1000, 600))

        self.main_panel = MainPanel(self.frame)
        self.main_panel.SetBackgroundColour("LIGHT BLUE")

        self.battle_panel = BattlePanel(self.main_panel, self)
        self.battle_panel.SetBackgroundColour("LIGHT BLUE")
        self.setting_panel = SettingPanel(self.main_panel, self)
        self.setting_panel.SetBackgroundColour("LIGHT BLUE")

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.battle_panel)
        main_sizer.Add(self.setting_panel)
        self.main_panel.SetSizer(main_sizer)

        main_sizer.Fit(self.main_panel)

        self.battle_field = BattleField(self.field_seize_x, self.field_seize_y)
        self.user = User(-1, '')
        # self.change_phase(PHASE[1])
        # self.init_server_socket()

        # 閉じるイベント
        self.frame.Bind(wx.EVT_CLOSE, self.frame_close)

        self.frame.Show()
        self.application.MainLoop()

    def frame_close(self, event):
        print('finish')
        self.user.upnp.delete_mapping()
        self.frame.Destroy()

    # network関連
    def init_server_socket(self):
        self.server_thread = AcceptThread(self, self.user.port)
        self.server_thread.setDaemon(True)
        self.server_thread.start()
        # time.sleep(1)

    def init_listen_socket(self, conn, is_send_normal_user=False):
        self.connection_list.append(conn)
        listen_thread = ListenThread(conn, self)
        listen_thread.setDaemon(True)
        listen_thread.start()
        self.listen_thread_list.append(listen_thread)
        print('is_host: {}'.format(self.user.is_host))
        if self.user.is_host is True:
            user_id = self.init_host_other_user()
            data = {
                'user_id': user_id,
                'host_name': self.user.name,
                'host_user_id': self.user.user_id
            }
            data = make_send_data(self.user.user_id, CONNECTION_HOST_INIT_RESPONSE, data)
            conn.send(data)
        else:
            if is_send_normal_user is False:
                return
            data = {

            }
            data = make_send_data(self.user.user_id, CONNECTION_NORMAL_INIT_RESPONSE, data)
            conn.send(data)

        # time.sleep(1)

    def connection(self, ip, port, is_send_normal_user=False):
        # ip = "localhost"
        # port = 12345
        bufsize = 1024
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, port))
        self.init_listen_socket(conn, is_send_normal_user)

    def send_data(self, status, data):
        for sock in self.connection_list:
            send_data = make_send_data(self.user.user_id, status, data)
            sock.send(send_data)
            # time.sleep(1)

    def received_data(self, user_id, status, data):
        if status is CONNECTION_HOST_INIT_RESPONSE:
            self.receive_host_init_data(data)
        if status is CONNECTION_HOST_SETTING and self.user.is_host is True:
            self.receive_host_setting(user_id, data)
        if status is CONNECTION_HOST_SETTING_RESPONSE:
            self.receive_host_setting_response(data)
        if status is CONNECTION_SEND_MESSAGE:
            self.receive_message(user_id, data)
        if status is CONNECTION_SHIP_INIT_START:
            self.receive_connect_ship_init_start()
        if status is CONNECTION_SHIP_INIT and self.user.is_host is True:
            self.receive_connect_ship_init()
        if status is CONNECTION_BATTLE_START:
            self.receive_connect_battle_start()
        if status is CONNECTION_BATTLE_PLAYER_CHANGE:
            self.receive_connect_player_change(user_id, data)
        if status is CONNECTION_PLAYER_ACTION:
            self.receive_connect_player_action(user_id, data)
        if status is CONNECTION_PLAYER_ACTION_RESPONSE:
            self.receive_connect_player_action_response(user_id, data)
        if status is CONNECTION_ALIVE_MESSAGE:
            self.receive_connect_alive_message(user_id, data)
        if status is CONNECTION_RESULT:
            self.receive_connect_result(user_id, data)
        if status is CONNECTION_NORMAL_INIT_RESPONSE:
            self.receive_normal_init_response(user_id, data)
        if status is CONNECTION_NORMAL_USER_SETTING:
            self.receive_normal_user_setting(data)
        if status is CONNECTION_NORMAL_USER_SETTING_RESPONSE:
            self.receive_normal_user_setting_response(data)
        if status is CONNECTION_SEND_PUBLIC_KEY and self.user.is_host is True:
            self.receive_send_public_key(user_id, data)
        if status is CONNECTION_SEND_PUBLIC_KEY_RESPONSE:
            self.receive_send_public_key_response(data)

        print('user_id: {0}, status: {1}, data: {2}'.format(user_id, status, data))

    def finish(self):
        for sock in self.connection_list:
            sock.close()
        self.server_thread.join()

    # system関連
    def change_phase(self, phase):
        self.user.phase = phase
        self.setting_panel.information_panel.user_information_panel.phase_panel.set_text(phase[1])

    def decide_user_setting(self, name, port):
        self.user.name = name
        self.user.port = int(port)
        self.init_server_socket()
        self.user.rsa = RSACipher(2048)

    def init_other_user(self):
        pass

    def init_host_other_user(self):
        user_id = self.host.add_user()
        other_user = HostOtherUser(user_id, '')
        self.other_user_dict.update({user_id: other_user})
        return user_id

    def finish_ship_init(self):
        self.host.ship_init_count += 1
        print(self.host.ship_init_count)
        print(self.host.join_user_count)
        if self.host.ship_init_count == self.host.join_user_count:
            data = {}
            self.send_data(CONNECTION_BATTLE_START, data)
            # self.change_phase(PHASE[3])
            self.player_change()

    def player_change(self):
        while True:
            self.host.move_user_id += 1
            if self.host.move_user_id > self.host.join_user_count:
                self.host.move_user_id = 1
            if self.host.move_user_id is 1 and self.host.is_host_alive is True:
                if self.user.is_alive() is True:
                    self.change_phase(PHASE[3])
                    self.receive_system_message('start {0} turn'.format(self.user.name))
                    data = {
                        'is_alive': True
                    }
                    self.send_data(CONNECTION_ALIVE_MESSAGE, data)
                    return
                else:
                    print('no')
                    self.host.is_host_alive = False
                    finish_flag, message = self.decrease_left_user()
                    if finish_flag is True:
                        self.receive_system_message(message)
                        self.change_phase(PHASE[0])
                        return
                    continue
            if self.other_user_dict[self.host.move_user_id].is_alive is True:
                data = {
                    'move_user_id': self.host.move_user_id
                }
                self.send_data(CONNECTION_BATTLE_PLAYER_CHANGE, data)
                return

    def decrease_left_user(self, user_id):
        self.host.left_user_count -= 1
        self.other_user_dict[user_id].is_alive = False
        if self.host.left_user_count is 1:
            user_name = self.user.name
            for other_user in self.other_user_dict.values():
                if other_user.is_alive is True:
                    user_name = other_user.name
                    break
            result_message = '{0} is winner !'.format(user_name)
            data = {
                'result_message': result_message
            }
            self.send_data(CONNECTION_RESULT, data)

            return True, result_message
        return False, ''

    # 通信の内容
    def receive_host_init_data(self, data):
        self.user.user_id = data['user_id']
        host_user_id = data['host_user_id']
        host_user_name = data['host_name']
        other_user = OtherUser(host_user_id, host_user_name)
        self.other_user_dict.update({host_user_id: other_user})
        self.setting_panel.information_panel.init_new_user(self.user.user_id, self.user.name)
        self.setting_panel.information_panel.init_new_user(host_user_id, host_user_name)
        sending_data = {
            'public_pem': self.user.rsa.public_pem.decode('utf-8'),
            'name': self.user.name
        }
        # send_data = encryption(send_data, PRIVATE_KEY)
        self.send_data(CONNECTION_SEND_PUBLIC_KEY, sending_data)

    def receive_send_public_key(self, user_id, data):
        other_user = self.other_user_dict[user_id]
        other_user.name = data['name']
        self.other_user_dict[user_id] = other_user
        self.setting_panel.information_panel.init_new_user(user_id, other_user.name)

        public_pem = data['public_pem']
        public_pem = public_pem.encode('utf-8')
        private_key = self.user.aes.key

        private_key = self.user.rsa.encrypt(plain_text=private_key, pem=public_pem)

        sending_data = {
            'private_key': private_key.decode('utf-8'),
            'to_user_id': user_id,
        }
        # send_data = encryption(send_data, PRIVATE_KEY)
        self.send_data(CONNECTION_SEND_PUBLIC_KEY_RESPONSE, sending_data)

    def receive_send_public_key_response(self, data):
        if data['to_user_id'] is not self.user.user_id:
            return
        private_key = data['private_key']
        private_key = self.user.rsa.decrypt(private_key.encode('utf-8'))
        ip_address = get_own_address(self.user.port, self.user.upnp)
        self.user.aes = AESCipher(key=private_key)
        ip_address = self.user.aes.encrypt(ip_address)
        sending_data = {
            'ip': ip_address.decode('utf-8'),
            'port': self.user.port,
            'name': self.user.name
        }
        self.send_data(CONNECTION_HOST_SETTING, sending_data)

    def receive_host_setting(self, user_id, data):
        other_user = self.other_user_dict[user_id]
        ip_address = data['ip']
        ip_address = self.user.aes.decrypt(ip_address)
        other_user.ip_address = ip_address.decode('utf-8')
        # data = decryption(data, PRIVATE_KEY)
        other_user.port = data['port']
        other_user.name = data['name']
        self.other_user_dict[user_id] = other_user
        self.receive_system_message('{0}が参加'.format(other_user.name))
        user_list = []
        for other_user in self.other_user_dict.values():
            other_user_ip_address = self.user.aes.encrypt(other_user.ip_address)
            user_list.append({
                'user_id': other_user.user_id,
                'user_name': other_user.name,
                'ip_address': other_user_ip_address.decode('utf-8'),
                'port': other_user.port,
            })
        sending_data = {
            'to_user_id': user_id,
            'user_list': user_list,
        }
        self.send_data(CONNECTION_HOST_SETTING_RESPONSE, sending_data)

    def receive_host_setting_response(self, data):
        if self.user.user_id != data['to_user_id']:
            return
        for user in data['user_list']:
            user_id = user['user_id']
            if user_id == self.user.user_id:
                continue
            user_name = user['user_name']
            other_user = OtherUser(user_id, user_name)
            self.other_user_dict.update({user_id: other_user})
            self.setting_panel.information_panel.init_new_user(user_id, user_name)
            ip_address = user['ip_address']
            ip_address = self.user.aes.decrypt(ip_address.encode('utf-8'))
            port = user['port']
            self.connection(ip_address, port)

    def receive_normal_init_response(self, user_id, data):
        sending_data = {
            'to_user_id': user_id,
            'user_id': self.user.user_id,
            'user_name': self.user.name
        }
        self.send_data(CONNECTION_NORMAL_USER_SETTING, sending_data)

    def receive_normal_user_setting(self, data):
        if data['to_user_id'] != self.user.user_id:
            return
        user_id = data['user_id']
        user_name = data['user_name']
        other_user = OtherUser(user_id, user_name)
        self.other_user_dict.update({user_id: other_user})
        self.setting_panel.information_panel.init_new_user(user_id, user_name)
        self.receive_system_message('{0}が参加'.format(user_name))

        sending_data = {}
        self.send_data(CONNECTION_NORMAL_USER_SETTING_RESPONSE, sending_data)

    def receive_normal_user_setting_response(self, data):
        pass

    def receive_connect_ship_init_start(self):
        self.change_phase(PHASE[1])

    def receive_connect_ship_init(self):
        self.finish_ship_init()

    def receive_connect_battle_start(self):
        self.change_phase(PHASE[2])

    def receive_connect_player_change(self, user_id, data):
        if data['move_user_id'] is self.user.user_id:
            is_alive = False
            if self.user.is_alive():
                is_alive = True
                self.change_phase(PHASE[3])
                self.receive_system_message('start {0} turn'.format(self.user.name))
            data = {
                'is_alive': is_alive
            }
            self.send_data(CONNECTION_ALIVE_MESSAGE, data)

    def receive_connect_player_action(self, user_id, data):
        if data['is_attack'] is True:
            attack_cell_id = data['attack_cell_id']
            attacked_message, ship_id, hp = check_ship_attacked(self, attack_cell_id)
            observe_message = check_observe_attack(self, attack_cell_id)
            if ship_id is not None:
                self.setting_panel.information_panel.update_ship_information(self.user.user_id, ship_id, hp)
            response_data = {
                'attacked_message': attacked_message,
                'observe_message': observe_message,
                'ship_id': ship_id,
                'hp': hp
            }
            self.send_data(CONNECTION_PLAYER_ACTION_RESPONSE, response_data)
        else:
            message = data['move_message']
            self.receive_message(user_id, message)
        if self.user.is_host is True:
            self.player_change()

    def receive_connect_player_action_response(self, user_id, data):
        attacked_message = data['attacked_message']
        observe_message = data['observe_message']
        self.receive_message(user_id, attacked_message)
        self.receive_message(user_id, observe_message)
        ship_id = data['ship_id']
        hp = data['hp']
        if ship_id is not FIELD_NOTHING:
            self.setting_panel.information_panel.update_ship_information(user_id, ship_id, hp)

    def receive_connect_alive_message(self, user_id, data):
        if data['is_alive'] is True:
            user_name = self.other_user_dict[user_id].name
            self.receive_system_message('start {0} turn'.format(user_name))
        if self.user.is_host is True and data['is_alive'] is False:
            finish_flag, message = self.decrease_left_user(user_id)
            if finish_flag is True:
                self.receive_system_message(message)
                self.change_phase(PHASE[0])
            else:
                self.player_change()

    def receive_connect_result(self, user_id, data):
        message = data['result_message']
        self.receive_message(user_id, message)
        self.change_phase(PHASE[0])

    def receive_message(self, user_id, message):
        user = self.other_user_dict[user_id]
        self.setting_panel.log_panel.receive_message(user.name, message)

    def receive_system_message(self, message):
        self.setting_panel.log_panel.receive_system_message(message)


if __name__ == '__main__':
    main = Main()
