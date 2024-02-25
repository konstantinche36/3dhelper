from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPainterPath, QPen
from PyQt5.QtCore import Qt
import sys


class BezierCurveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кривая Безье в PyQt5")
        self.setGeometry(100, 100, 800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Включаем сглаживание

        # Создаем объект QPainterPath и начинаем путь с точки (100, 100)
        path = QPainterPath()
        path.moveTo(100, 100)

        # Добавляем кривую Безье с контрольными точками (100, 200) и (200, 200) и точкой через которую проходит кривая (200, 100)
        path.cubicTo(100, 200, 200, 200, 200, 100)

        # Настраиваем перо для рисования кривой
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)

        # Рисуем кривую Безье
        painter.drawPath(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BezierCurveWidget()
    window.show()
    sys.exit(app.exec_())
