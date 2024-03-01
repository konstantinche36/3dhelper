from typing import List

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QStatusBar, QMessageBox,
                             QGraphicsEllipseItem, QHBoxLayout, QCheckBox, QRadioButton, QButtonGroup,
                             QGraphicsLineItem, QGraphicsPathItem)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QPen, QPainterPath
from PyQt5.QtCore import Qt, QPoint, QRectF
import sys

from XFigure import XFigure

from Utils import generate_unique_name
from XPoint import XPoint


class ImageViewer(QGraphicsView):
    def __init__(self, statusbar, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.scene = QGraphicsScene(self)  # Создаем сцену для отображения графических элементов
        self.setScene(self.scene)  # Устанавливаем сцену в QGraphicsView
        self.pixmap_item = QGraphicsPixmapItem()  # Создаем элемент для отображения изображений
        self.scene.addItem(self.pixmap_item)  # Добавляем элемент изображения на сцену
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform)  # Устанавливаем подсказки для рендеринга
        self.statusbar = statusbar  # Сохраняем ссылку на статусную строку для вывода сообщений
        self.scale_factor = 1.0  # Инициализируем коэффициент масштабирования
        self.last_pan_point = None  # Инициализируем переменную для последней точки панорамирования
        # self.figures = []  # Создаем пустой список для хранения фигур
        self.points = []  # Список для хранения координат точек
        self.point_items: List[QGraphicsEllipseItem] = []  # Список point-ов, экземпляр класса QGraphicsEllipseItem
        self.adding_figure_mode = False  # Добавляем новый атрибут для режима добавления фигур
        self.select_figure_mode = False
        self.edit_figure_mode = False
        self.delete_figure_mode = False
        self.xFigures: List[XFigure] = []
        self.active_figure: XFigure = None
        self.selected_figure: XFigure = None
        self.selected_point: XPoint = None
        self.temp_line = None
        self.temporary_point = None
        self.space_pressed = False
        self.mid_button_press = False  # Необходима, чтобы во добавления фигуры можно было пользоваться центральной кнопкой мыши
        self.base_radius = 5  # Базовый размер точки без масштабирования

    def set_image(self, image_path):
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.pixmap_item.setPixmap(pixmap)
            self.setSceneRect(QRectF(pixmap.rect()))
            self.scale_factor = 1.0  # Сброс коэффициента масштабирования
        else:
            QMessageBox.warning(self, "Ошибка загрузки", "Не удалось загрузить изображение.")

    def mousePressEvent(self, event):
        super(ImageViewer, self).mousePressEvent(event)
        scenePos = self.mapToScene(event.pos())

        if self.adding_figure_mode and event.button() == Qt.LeftButton:
            self.statusbar.showMessage(f"Клик мыши в координатах: ({scenePos.x():.2f}, {scenePos.y():.2f})")
            self.temporary_point = (scenePos.x(), scenePos.y())
            self.drawPoint(*self.temporary_point)
        elif self.select_figure_mode and event.button() == Qt.LeftButton:
            self.statusbar.showMessage(f'Переход в режим select_figure с координатами ')
            self.select_figure(scenePos.x(), scenePos.y())
            self.selected_point = self.select_point(scenePos.x(), scenePos.y())
            if self.selected_figure:
                self.change_color_for_figure(self.selected_figure)
            if self.selected_point:
                self.change_color_for_point(self.selected_point, QColor(0,0,255))

        elif self.edit_figure_mode and event.button() == Qt.LeftButton:
            pass
        elif self.delete_figure_mode and event.button() == Qt.LeftButton:
            pass

        if event.button() == Qt.MidButton:
            self.mid_button_press = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent22(self, event):
        super(ImageViewer, self).mouseMoveEvent(event)
        if self.temporary_point is not None:
            self.temporary_point = None
            self.redrawPoints()

        if self.adding_figure_mode and self.active_figure and len(
                self.active_figure.points) > 0 and not self.mid_button_press:
            # Удалить предыдущую временную линию, если она есть
            if hasattr(self, 'temp_line') and self.temp_line:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None

            # Получить последнюю точку
            last_point = self.active_figure.points[-1]
            # Текущее положение курсора
            current_pos = self.mapToScene(event.pos())

            # Создать временную линию
            path = QPainterPath()
            path.moveTo(last_point.main_x, last_point.main_y)
            path.lineTo(current_pos.x(), current_pos.y())
            self.temp_line = self.scene.addPath(path, QPen(Qt.red, 1, Qt.DashLine))
        elif self.select_figure_mode and self.selected_figure:
            print('wwwwwwwww')
            self.statusbar.showMessage(f'Переход в режим select_figure с координатами 111')

        if self.last_pan_point and self.mid_button_press:
            delta = event.pos() - self.last_pan_point
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pan_point = event.pos()

    def mouseReleaseEvent22(self, event):
        super(ImageViewer, self).mouseReleaseEvent(event)
        if self.adding_figure_mode and event.button() == Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            if not self.active_figure:
                self.active_figure = XFigure(generate_unique_name())
                self.xFigures.append(self.active_figure)

            new_point = XPoint(scenePos.x(), scenePos.y(), scenePos.x(), scenePos.y(), scenePos.x(), scenePos.y())
            self.active_figure.add_point(new_point)

            # Если это не первая точка, рисуем линию от предыдущей точки к новой
            if len(self.active_figure.points) > 1:
                prev_point = self.active_figure.points[-2]
                self.drawLine(prev_point, new_point)

            self.drawPoint(scenePos.x(), scenePos.y())

            # Удаляем временную линию, если она была нарисована
            if self.temp_line:
                self.scene.removeItem(self.temp_line)
                self.temp_line = None

        elif self.select_figure_mode and event.button() == Qt.LeftButton:
            pass
            # self.statusbar.showMessage(f'Переход в режим select_figure с координатами ')
            # self.reset_selection_figures()
            # scenePos = self.mapToScene(event.pos())
            # # self.select_figure(scenePos.x(), scenePos.y())
            # if self.selected_figure:
            #     self.change_color_for_figure(self.selected_figure)

        elif event.button() == Qt.MidButton:
            self.last_pan_point = None
            self.setCursor(Qt.ArrowCursor)
            self.mid_button_press = False
        # self.redrawPoints()

    def select_point(self, x, y):
        self.statusbar.showMessage(f'Переход в метод select_point с координатами x{x} y{y}')
        if self.selected_figure:
            return self.check_point_in_figure(x, y, self.selected_figure)
            # for point in self.selected_figure.points:
            #     # Проверяем, попадает ли точка (x, y) в радиус точки фигуры
            #     if (point.main_x - x) ** 2 + (point.main_y - y) ** 2 <= self.base_radius ** 2:
            #         self.selected_point = point
            #         break

    def select_figure(self, x, y):
        self.statusbar.showMessage(f'Переход в метод select_figure с координатами x{x} y{y}')
        # self.reset_selection_figures()
        self.selected_figure = None
        for figure in self.xFigures:
            # for point in figure.points:
            #     # Проверяем, попадает ли точка (x, y) в радиус точки фигуры
            #     if (point.main_x - x) ** 2 + (point.main_y - y) ** 2 <= self.base_radius ** 2:
            #         self.selected_figure = figure
            #         break
            if self.check_point_in_figure(x, y, figure):
                self.selected_figure = figure
                break

    def check_point_in_figure(self, x, y, figure: XFigure):
        for point in figure.points:
            # Проверяем, попадает ли точка (x, y) в радиус точки фигуры
            if (point.main_x - x) ** 2 + (point.main_y - y) ** 2 <= self.base_radius ** 2:
                return point

    def reset_selection_figures(self):
        print('001')
        self.clearLines()
        # Удаляем только элементы точек
        for item in self.point_items:
            self.scene.removeItem(item)

        for figure in self.xFigures:
            prev_point = None
            for point in figure.points:
                if prev_point:
                    self.drawLine(prev_point, point)
                prev_point = point

    def clearLines(self):
        print('011')
        for item in self.scene.items():
            if isinstance(item, QGraphicsPathItem):
                self.scene.removeItem(item)
        # self.scene.removeItem()
        # for item in self.scene.removeItem():
        #     print(000)
        #     if isinstance(item, QGraphicsLineItem):
        #         print(111)
        #         self.scene.removeItem(item)

    def change_color_for_point(self, point: XPoint, color: QColor = QColor(0, 255, 0)):
        self.drawPoint(point.main_x, point.main_y, color, 2)

    def change_color_for_figure(self, figure: XFigure):
        for point in figure.points:
            self.drawPoint(point.main_x, point.main_y, QColor(0, 255, 0), 2)
            self.drawLinesByFigure(figure)

    def drawPoint(self, x, y, color: QColor = QColor(255, 0, 0), addition_radius_part: int = 0):
        """Отрисовывает точку на заданных координатах с учетом масштабирования."""
        # Рассчитываем фактический размер точки с учетом текущего масштаба
        radius = (self.base_radius + addition_radius_part) / self.scale_factor
        # Создаем эллипс с новым размером
        ellipse = QGraphicsEllipseItem(x - radius, y - radius, 2 * radius, 2 * radius)
        ellipse.setBrush(QBrush(color))  # Заливка красным цветом
        # Убираем обводку, устанавливая прозрачный цвет для пера
        ellipse.setPen(QPen(QColor(0, 0, 0, 0)))  # QColor(0, 0, 0, 0) - это прозрачный цвет
        self.point_items.append(ellipse)
        self.scene.addItem(ellipse)

    def drawBezierCurve(self, startPoint, endPoint, controlPoint1, controlPoint2, addition_width_part=0):
        path = QPainterPath()
        path.moveTo(startPoint)
        path.cubicTo(controlPoint1, controlPoint2, endPoint)

        pen = QPen(Qt.black, 2 + addition_width_part)  # Черное перо толщиной 2
        self.scene.addPath(path, pen)

    def drawLine(self, start_point: XPoint, end_point: XPoint, width: int = 1, color: QColor = QColor(0, 0, 0)):
        path = QPainterPath()
        path.moveTo(start_point.main_x, start_point.main_y)
        path.lineTo(end_point.main_x, end_point.main_y)

        pen = QPen()  # Настроить перо по желанию
        pen.setWidth(width)
        pen.setColor(color)
        self.scene.addPath(path, pen)

    def drawLinesByFigure(self, figure: XFigure, color: QColor = QColor(255, 0, 0)):
        prev_point = None
        for point in figure.points:
            if prev_point:
                self.drawLine(prev_point, point, 2, color)
            prev_point = point

    def redrawPoints(self):
        # Удаляем только элементы точек
        for item in self.point_items:
            self.scene.removeItem(item)
        self.point_items.clear()  # Очищаем список ссылок на элементы точек
        # Перерисовываем точки
        for figure in self.xFigures:
            for point in figure.points:
                self.drawPoint(point.main_x, point.main_y)

    def wheelEvent(self, event):
        """Обрабатывает события прокрутки колесика мыши для масштабирования."""
        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            factor = 1.2
            if event.angleDelta().y() > 0:
                self.scale(factor, factor)
                self.scale_factor *= factor
            else:
                self.scale(1 / factor, 1 / factor)
                self.scale_factor /= factor
            self.statusbar.showMessage(f"Масштаб: {self.scale_factor * 100:.0f}%")
            # Перерисовываем все точки с новым масштабом
            self.redrawPoints()
        else:
            super(ImageViewer, self).wheelEvent(event)


class MainApplication(QMainWindow):
    def __init__(self):
        super(MainApplication, self).__init__()
        self.setWindowTitle('3D Helper')
        self.setGeometry(100, 100, 1000, 800)
        self.initUI()

    def initUI(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        hbox_layout = QHBoxLayout()
        button_layout = QVBoxLayout()

        self.load_image_button = QPushButton('Загрузить изображение', self)
        self.load_image_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_image_button)

        # Создаем группу радиокнопок для взаимоисключающего выбора
        self.mode_group = QButtonGroup(self)  # Группа для взаимоисключения кнопок

        # Радиокнопка "Добавить фигуру"
        self.add_figure_radio = QRadioButton('Добавить фигуру', self)
        self.add_figure_radio.toggled.connect(self.toggle_mode)
        self.mode_group.addButton(self.add_figure_radio)
        button_layout.addWidget(self.add_figure_radio)

        # Радиокнопка "Изменить фигуру"
        self.edit_figure_radio = QRadioButton('Изменить фигуру', self)
        self.edit_figure_radio.toggled.connect(self.toggle_mode)
        self.mode_group.addButton(self.edit_figure_radio)
        button_layout.addWidget(self.edit_figure_radio)

        # Радиокнопка "Выделить фигуру"
        self.select_figure_radio = QRadioButton('Выделить фигуру', self)
        self.select_figure_radio.toggled.connect(self.toggle_mode)
        self.mode_group.addButton(self.select_figure_radio)
        button_layout.addWidget(self.select_figure_radio)

        # Радиокнопка "Удалить фигуру"
        self.delete_figure_radio = QRadioButton('Удалить фигуру', self)
        self.delete_figure_radio.toggled.connect(self.toggle_mode)
        self.mode_group.addButton(self.delete_figure_radio)
        button_layout.addWidget(self.delete_figure_radio)

        # По умолчанию выбрана радиокнопка "Добавить фигуру"
        self.add_figure_radio.setChecked(True)

        button_layout.addStretch()

        hbox_layout.addLayout(button_layout)

        self.image_viewer = ImageViewer(self.statusbar)
        hbox_layout.addWidget(self.image_viewer, 1)

        central_widget = QWidget(self)
        central_widget.setLayout(hbox_layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "",
                                                   "Изображения (*.png *.xpm *.jpg *.jpeg)")
        if file_name:
            self.image_viewer.set_image(file_name)

    def toggle_mode(self):
        # Обновление режима в объекте image_viewer в зависимости от выбранной радиокнопки
        self.image_viewer.adding_figure_mode = self.add_figure_radio.isChecked()
        self.image_viewer.editing_figure_mode = self.edit_figure_radio.isChecked()
        self.image_viewer.selecting_figure_mode = self.select_figure_radio.isChecked()
        self.image_viewer.deleting_figure_mode = self.delete_figure_radio.isChecked()
        # Вывод текущего выбранного режима для отладки
        print(f"Добавление: {self.image_viewer.adding_figure_mode}, "
              f"Изменение: {self.image_viewer.editing_figure_mode}, "
              f"Выделение: {self.image_viewer.selecting_figure_mode}, "
              f"Удаление: {self.image_viewer.deleting_figure_mode}")


class MainApplication(QMainWindow):
    def __init__(self):
        super(MainApplication, self).__init__()
        self.setWindowTitle('3D Helper')
        self.setGeometry(100, 100, 1000, 800)
        self.initUI()

    def initUI(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        hbox_layout = QHBoxLayout()
        button_layout = QVBoxLayout()

        self.load_image_button = QPushButton('Загрузить изображение', self)
        self.load_image_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_image_button)

        # Создаем группу для радиокнопок
        self.radio_button_group = QButtonGroup(self)
        self.radio_button_group.setExclusive(True)  # Только одна кнопка в группе может быть выбрана

        # Создаем радиокнопки
        self.add_figure_radio = QRadioButton("Добавить фигуру")
        self.edit_figure_radio = QRadioButton("Изменить фигуру")
        self.select_figure_radio = QRadioButton("Выделить фигуру")
        self.delete_figure_radio = QRadioButton("Удалить фигуру")

        # Добавляем радиокнопки в группу
        self.radio_button_group.addButton(self.add_figure_radio)
        self.radio_button_group.addButton(self.edit_figure_radio)
        self.radio_button_group.addButton(self.select_figure_radio)
        self.radio_button_group.addButton(self.delete_figure_radio)

        # Добавляем радиокнопки в вертикальный макет
        button_layout.addWidget(self.add_figure_radio)
        button_layout.addWidget(self.edit_figure_radio)
        button_layout.addWidget(self.select_figure_radio)
        button_layout.addWidget(self.delete_figure_radio)

        # # Делаем радиокнопку "Добавить фигуру" выбранной по умолчанию
        # self.add_figure_radio.setChecked(True)

        # Связываем события переключения радиокнопок с методами
        self.add_figure_radio.toggled.connect(self.toggle_drawing_mode)
        self.edit_figure_radio.toggled.connect(self.toggle_edit_mode)
        self.select_figure_radio.toggled.connect(self.toggle_select_mode)
        self.delete_figure_radio.toggled.connect(self.toggle_delete_mode)
        # Для остальных радиокнопок аналогично связать с методами

        button_layout.addStretch()

        hbox_layout.addLayout(button_layout)

        self.image_viewer = ImageViewer(self.statusbar)
        hbox_layout.addWidget(self.image_viewer, 1)

        central_widget = QWidget(self)
        central_widget.setLayout(hbox_layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "",
                                                   "Изображения (*.png *.xpm *.jpg *.jpeg)")
        if file_name:
            self.image_viewer.set_image(file_name)

    def toggle_drawing_mode(self, checked):
        # Этот метод вызывается, когда состояние радиокнопки "Добавить фигуру" изменяется
        self.image_viewer.adding_figure_mode = checked
        self.image_viewer.active_figure = None
        if checked:
            print("Режим добавления фигур включен")
            self.statusbar.showMessage("Режим добавления фигур включен")
        else:
            print("Режим добавления фигур выключен")

    def toggle_edit_mode(self, checked):
        # Этот метод вызывается, когда состояние радиокнопки "Добавить фигуру" изменяется
        self.image_viewer.edit_figure_mode = checked
        self.image_viewer.active_figure = None
        if checked:
            print("Режим редактирования фигур включен")
            self.statusbar.showMessage("Режим редактирования фигур включен")
        else:
            print("Режим редактирования фигур выключен")

    def toggle_select_mode(self, checked):
        # Этот метод вызывается, когда состояние радиокнопки "Добавить фигуру" изменяется
        self.image_viewer.select_figure_mode = checked
        self.image_viewer.active_figure = None
        if checked:
            print("Режим выделения фигур включен")
            self.statusbar.showMessage("Режим выделения фигур включен")
        else:
            print("Режим выделения фигур выключен")

    def toggle_delete_mode(self, checked):
        # Этот метод вызывается, когда состояние радиокнопки "Добавить фигуру" изменяется
        self.image_viewer.delete_figure_mode = checked
        self.image_viewer.active_figure = None
        if checked:
            print("Режим удаления фигур включен")
            self.statusbar.showMessage("Режим удаления фигур включен")
        else:
            print("Режим удаления фигур выключен")


app = QApplication(sys.argv)
main_window = MainApplication()
main_window.show()
sys.exit(app.exec_())
