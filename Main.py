from typing import List

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QStatusBar, QMessageBox,
                             QGraphicsEllipseItem)
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
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)  # Устанавливаем подсказки для рендеринга
        self.statusbar = statusbar  # Сохраняем ссылку на статусную строку для вывода сообщений
        self.scale_factor = 1.0  # Инициализируем коэффициент масштабирования
        self.last_pan_point = None  # Инициализируем переменную для последней точки панорамирования
        self.figures = []  # Создаем пустой список для хранения фигур 
        self.points = []  # Список для хранения координат точек
        self.point_items: List[QGraphicsEllipseItem] = [] # Список point-ов, экземпляр класса QGraphicsEllipseItem

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
        if event.button() == Qt.LeftButton:
            scenePos = self.mapToScene(event.pos())
            self.statusbar.showMessage(f"Клик мыши в координатах: ({scenePos.x():.2f}, {scenePos.y():.2f})")
            self.points.append((scenePos.x(), scenePos.y()))  # Добавление координат точки в список
            self.drawPoint(scenePos.x(), scenePos.y())  # Отрисовка точки на сцене
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
        print(111)
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
        self.image_viewer = None
        self.load_image_button = None
        self.statusbar = None
        self.setWindowTitle('3D Helper')
        self.setGeometry(100, 100, 1000, 800)
        self.initUI()

    def initUI(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.load_image_button = QPushButton('Загрузить изображение', self)
        self.load_image_button.clicked.connect(self.load_image)
        layout.addWidget(self.load_image_button)

        self.image_viewer = ImageViewer(self.statusbar)
        layout.addWidget(self.image_viewer)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "",
                                                   "Изображения (*.png *.xpm *.jpg *.jpeg)")
        if file_name:
            self.image_viewer.set_image(file_name)


app = QApplication(sys.argv)
main_window = MainApplication()
main_window.show()
sys.exit(app.exec_())
