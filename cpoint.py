class CPoint:
    def __init__(self, x, y, ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y):
        self._x = x
        self._y = y
        self._ctrl1_x = ctrl1_x
        self._ctrl1_y = ctrl1_y
        self._ctrl2_x = ctrl2_x
        self._ctrl2_y = ctrl2_y

    # Геттеры и сеттеры для координат точки
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    # Геттеры и сеттеры для первой контрольной точки
    @property
    def ctrl1_x(self):
        return self._ctrl1_x

    @ctrl1_x.setter
    def ctrl1_x(self, value):
        self._ctrl1_x = value

    @property
    def ctrl1_y(self):
        return self._ctrl1_y

    @ctrl1_y.setter
    def ctrl1_y(self, value):
        self._ctrl1_y = value

    # Геттеры и сеттеры для второй контрольной точки
    @property
    def ctrl2_x(self):
        return self._ctrl2_x

    @ctrl2_x.setter
    def ctrl2_x(self, value):
        self._ctrl2_x = value

    @property
    def ctrl2_y(self):
        return self._ctrl2_y

    @ctrl2_y.setter
    def ctrl2_y(self, value):
        self._ctrl2_y = value