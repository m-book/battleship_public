from .ship import *
from phase import *
from upnp import UPNP


class User:
    warship = None
    destroyer = None
    submarine = None
    aes = None
    rsa = None
    upnp = UPNP()

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.warship = Warship()
        self.destroyer = Destroyer()
        self.submarine = Submarine()
        self.phase = PHASE[0]
        self.is_host = False
        self.port = 5000

    def get_ship_by_ship_id(self, ship_id):
        if ship_id == FIELD_WARSHIP:
            return self.warship
        elif ship_id == FIELD_DESTROYER:
            return self.destroyer
        else:
            return self.submarine

    def is_alive(self):
        if self.warship.hp > 0:
            return True
        if self.destroyer.hp > 0:
            return True
        if self.submarine.hp > 0:
            return True
        return False


class Host:
    user_id = 0
    ship_init_count = 0
    join_user_count = 0
    left_user_count = 0
    move_user_id = 0
    is_host_alive = True

    def add_user(self):
        self.user_id += 1
        self.join_user_count += 1
        self.left_user_count += 1
        return self.user_id


class OtherUser:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name


class HostOtherUser(OtherUser):
    ip_address = ''
    port = 0

    def __init__(self, user_id, name):
        super().__init__(user_id, name)
        self.phase = self.phase = PHASE[0]
        self.is_alive = True
