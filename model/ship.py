from constant import *


class BaseShip:
    def __init__(self, ship_id, hp, name):
        self.ship_id = ship_id
        self.hp = hp
        self.name = name
        self.enable = False


class Warship(BaseShip):
    def __init__(self):
        super().__init__(FIELD_WARSHIP, 3, 'W')


class Destroyer(BaseShip):
    def __init__(self):
        super().__init__(FIELD_DESTROYER, 2, 'D')


class Submarine(BaseShip):
    def __init__(self):
        super().__init__(FIELD_SUBMARINE, 1, 'S')
