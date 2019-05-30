from constant import *


class BattleField:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 一つ目で縦指定、２つ目で横指定
        self.field_list = []
        cell_id = 0
        for i in range(y):
            self.field_list.append([])
            for j in range(x):
                cell = BattleFieldCell(j, i, cell_id)
                self.field_list[i].append(cell)
                cell_id += 1
        self.selected_cell_id = -1
        self.selected_enable_attack_list = []
        self.selected_enable_move_list = []

    def initiate_ship(self, ship_id, field_id):
        cell = self.get_field_cell_by_id(field_id)
        if cell.status is FIELD_NOTHING:
            cell.status = ship_id
            return True
        return False

        # x, y = cell.get_position()
        # if self.field_list[x][y].status == FIELD_NOTHING:
        #     self.field_list[x][y].status = ship_id
        #     return True
        # return False

    def get_ship_enable_move_position(self, cell_id):
        cell = self.get_field_cell_by_id(cell_id)
        enable_list = []
        for y in range(self.y):
            if y == cell.y:
                for x_cell in self.field_list[y]:
                    if x_cell.status == FIELD_NOTHING:
                        enable_list.append((x_cell.x, y))
            if self.field_list[y][cell.x].status == FIELD_NOTHING:
                enable_list.append((self.field_list[y][cell.x].x, self.field_list[y][cell.x].y))
        return enable_list

    def get_ship_enable_attack_position(self, cell_id):
        cell = self.get_field_cell_by_id(cell_id)
        return self.get_around_point(cell.x, cell.y)

    def get_ship_enable_observe_position(self, attacked_x, attacked_y):
        enable_observe_point_list = self.get_around_point(attacked_x, attacked_y)
        observed_ship_id_list = []
        for enable_observe_point in enable_observe_point_list:
            if self.field_list[enable_observe_point[1]][enable_observe_point[0]].status == FIELD_WARSHIP:
                observed_ship_id_list.append(FIELD_WARSHIP)
            if self.field_list[enable_observe_point[1]][enable_observe_point[0]].status == FIELD_DESTROYER:
                observed_ship_id_list.append(FIELD_DESTROYER)
            if self.field_list[enable_observe_point[1]][enable_observe_point[0]].status == FIELD_SUBMARINE:
                observed_ship_id_list.append(FIELD_SUBMARINE)
        return observed_ship_id_list

    def get_around_point(self, center_x, center_y):
        around_list = []
        start_x = center_x - 1
        start_y = center_y - 1
        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0
        finish_x = center_x + 1
        finish_y = center_y + 1
        if finish_x >= self.x:
            finish_x = self.x - 1
        if finish_y >= self.y:
            finish_y = self.y - 1
        for y in range(start_y, finish_y+1):
            for x in range(start_x, finish_x+1):
                if x == center_x and y == center_y:
                    continue
                around_list.append((x, y))
        return around_list

    def get_field_cell_by_id(self, cell_id):
        for x_list in self.field_list:
            for cell in x_list:
                if cell.cell_id == cell_id:
                    return cell
        return None

    def get_field_cell_by_position(self, x, y):
        return self.field_list[y][x]


class BattleFieldCell():
    def __init__(self, x, y, cell_id):
        self.x = x
        self.y = y
        self.cell_id = cell_id
        self.status = FIELD_NOTHING

    def get_position(self):
        return self.x, self.y


