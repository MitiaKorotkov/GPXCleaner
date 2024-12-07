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
import pandas as pd

from random import randint
import sys

from gpx_parser import read_gpx


def get_random_color():
    return QColor(randint(1, 255), randint(1, 255), randint(1, 255))


class CustomViewer(QGraphicsView):
    pass


class MainWindow(QWidget):
    def __init__(self, max_x, max_y):
        super().__init__()

        self.sf = 1

        self.setWindowTitle("Hi there")
        self.resize(1000, 800)

        self.scene = QGraphicsScene(0, 0, max_x, max_y)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.scale(0.01, 0.01)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.view)

    def paint_circle(self, position, color, radius=500):
        circle = QGraphicsEllipseItem(0, 0, radius, radius)
        circle.setPos(*position)

        circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        circle.setBrush(QBrush(color))

        self.scene.addItem(circle)

    def paint_path(self, points, num_labels, radius=500, color=None):
        colors = [
            get_random_color() if color is None else color for _ in range(num_labels)
        ]

        for x, y, label in points:
            self.paint_circle([x, y], colors[label], radius=radius)

    def zoom(self, x):
        self.view.scale(x, x)

        for i in self.scene.items():
            if isinstance(i, QGraphicsEllipseItem):
                i.setScale(self.sf)

    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent) and event.text() == "+":
            self.sf /= 1.6
            self.zoom(2)

        if isinstance(event, QKeyEvent) and event.text() == "-":
            self.sf *= 1.6
            self.zoom(0.5)

        return super().keyPressEvent(event)


def view_df(df: pd.DataFrame):
    BIG_NUMBER = 1e8

    df["rel_lat"] = df["lat"] - df["lat"].min()
    df["rel_lon"] = df["lon"] - df["lon"].min()

    max_lon = df["rel_lon"].max() * BIG_NUMBER
    max_lat = df["rel_lat"].max() * BIG_NUMBER

    app = QApplication(sys.argv)
    window = MainWindow(1.1 * max_lon, 1.1 * max_lat)

    if "deleted" in df.columns:
        deleted_df = df[df["deleted"]]
        deleted_points = [
            [lon * BIG_NUMBER, lat * BIG_NUMBER, 0]
            for lon, lat in zip(deleted_df["rel_lon"], deleted_df["rel_lat"])
        ]
        window.paint_path(
            points=deleted_points,
            num_labels=1,
            radius=1500,
            color=Qt.GlobalColor.black,
        )

    points = [
        [lon * BIG_NUMBER, lat * BIG_NUMBER, label]
        for lon, lat, label in zip(df["rel_lon"], df["rel_lat"], df["cluster"])
    ]

    window.paint_path(points=points, num_labels=df["cluster"].unique().shape[0])

    window.show()
    app.exec()


def open_gpx(dir_name, filename):
    df = read_gpx(dir_name, [filename])

    df["cluster"] = np.array([-1 for _ in range(df.shape[0])])

    view_df(df)


if __name__ == "__main__":
    open_gpx("tmp", "tmp")
