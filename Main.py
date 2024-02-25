from typing import List

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QStatusBar, QMessageBox,
                             QGraphicsEllipseItem, QHBoxLayout, QCheckBox, QRadioButton, QButtonGroup)
from PyQt5.QtGui import QPixmap, QPainter, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QPoint, QRectF
import sys


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
        self.figures = []  # Создаем пустой список для хранения фигур 
        # self.points: List[CPoint] = []  # Список для хранения координат точек
        self.points = []  # Список для хранения координат точек
        self.point_items: List[QGraphicsEllipseItem] = []  # Список point-ов, экземпляр класса QGraphicsEllipseItem
        self.adding_figure_mode = False  # Добавляем новый атрибут для режима добавления фигур
        self.edit_figure_radio = False  # Добавляем новый атрибут для режима добавления фигур
        self.select_figure_radio = False  # Добавляем новый атрибут для режима добавления фигур
        self.delete_figure_radio = False  # Добавляем новый атрибут для режима добавления фигур
        # self.drawing_enabled = False

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
        # if self.adding_figure_mode and event.button() == Qt.LeftButton:  # Проверяем, включен ли режим добавления фигур
        super(ImageViewer, self).mousePressEvent(event)
        if self.adding_figure_mode and event.button() == Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            self.statusbar.showMessage(f"Клик мыши в координатах: ({scenePos.x():.2f}, {scenePos.y():.2f})")
            self.points.append((scenePos.x(), scenePos.y()))
            self.drawPoint(scenePos.x(), scenePos.y())
        elif event.button() == Qt.MidButton:
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def drawPoint(self, x, y):
        """Отрисовывает точку на заданных координатах с учетом масштабирования."""
        base_radius = 5  # Базовый размер точки без масштабирования
        # Рассчитываем фактический размер точки с учетом текущего масштаба
        radius = base_radius / self.scale_factor
        # Создаем эллипс с новым размером
        ellipse = QGraphicsEllipseItem(x - radius, y - radius, 2 * radius, 2 * radius)
        ellipse.setBrush(QBrush(QColor(255, 0, 0)))  # Заливка красным цветом
        # Убираем обводку, устанавливая прозрачный цвет для пера
        ellipse.setPen(QPen(QColor(0, 0, 0, 0)))  # QColor(0, 0, 0, 0) - это прозрачный цвет
        self.point_items.append(ellipse)
        self.scene.addItem(ellipse)

    def mouseMoveEvent(self, event):
        if self.last_pan_point is not None:
            delta = event.pos() - self.last_pan_point
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pan_point = event.pos()
        else:
            super(ImageViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MidButton:
            self.last_pan_point = None
            self.setCursor(Qt.ArrowCursor)
        else:
            super(ImageViewer, self).mouseReleaseEvent(event)

    def redrawPoints(self):
        # Удаляем только элементы точек
        for item in self.point_items:
            print(f'del {item}')
            self.scene.removeItem(item)
        self.point_items.clear()  # Очищаем список ссылок на элементы точек

        # Перерисовываем точки
        for point in self.points:
            self.drawPoint(*point)

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
        if checked:
            print("Режим добавления фигур включен")
        else:
            print("Режим добавления фигур выключен")


app = QApplication(sys.argv)
main_window = MainApplication()
main_window.show()
sys.exit(app.exec_())
