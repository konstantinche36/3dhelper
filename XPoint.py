class XPoint:
    def __init__(self, main_x, main_y, ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y):
        self._main_x = main_x
        self._main_y = main_y
        self._ctrl1_x = ctrl1_x
        self._ctrl1_y = ctrl1_y
        self._ctrl2_x = ctrl2_x
        self._ctrl2_y = ctrl2_y

    @property
    def main_x(self):
        return self._main_x

    @main_x.setter
    def main_x(self, value):
        self._main_x = value

    @property
    def main_y(self):
        return self._main_y

    @main_y.setter
    def main_y(self, value):
        self._main_y = value

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

    def unique_identifier(self):
        return hash((self._main_x, self._main_y, self._ctrl1_x, self._ctrl1_y, self._ctrl2_x, self._ctrl2_y))



    def __eq__(self, other):
        return (self._main_x, self._main_y, self._ctrl1_x, self._ctrl1_y, self._ctrl2_x, self._ctrl2_y) == \
               (other._main_x, other._main_y, other._ctrl1_x, other._ctrl1_y, other._ctrl2_x, other._ctrl2_y)

    def __hash__(self):
        return hash((self._main_x, self._main_y, self._ctrl1_x, self._ctrl1_y, self._ctrl2_x, self._ctrl2_y))

