import venv
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsView,
)

from PyQt6.QtCore import Qt, QSize, QLocale, QPoint, pyqtSignal
from PyQt6.QtGui import QBrush, QPainter, QKeyEvent, QColor

import numpy as np
import sys

class CustomViewer(QGraphicsView):
    pass

class MainWindow(QWidget):
    def __init__(self, buttons_positions, max_x, max_y):
        super().__init__()

        self.setWindowTitle("Hi there")
        self.resize(1000, 800)

        self.scene = QGraphicsScene(0, 0, max_x, max_y)

        for position in buttons_positions:
            self.paint_circle(position)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.sf = 1
        self.view.scale(0.01, 0.01)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.view)

        # self.setLayout(hbox)

    def paint_circle(self, position):
        circle = QGraphicsEllipseItem(0, 0, 500, 500)
        circle.setPos(*position)

        circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        circle.setBrush(QBrush(Qt.GlobalColor.blue))
        self.scene.addItem(circle)

    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent) and event.text() == '+':
            self.sf /= 1.6
            self.view.scale(2, 2)

            for i in self.scene.items():
                if isinstance(i, QGraphicsEllipseItem):
                    i.setScale(self.sf)

        if isinstance(event, QKeyEvent) and event.text() == '-':
            self.sf *= 1.6
            self.view.scale(0.5, 0.5)

            for i in self.scene.items():
                if isinstance(i, QGraphicsEllipseItem):
                    i.setScale(self.sf)
        
        return super().keyPressEvent(event)


points_positions = []
with open('tmp.txt', 'r') as file:
    for line in file.read().split('\n'):
        if line:
            point = list(map(float, line.split(',')))
            points_positions.append(list(map(int, point)))

app = QApplication(sys.argv)

window = MainWindow(points_positions, 667427, 1170555)
window.show()

app.exec()
