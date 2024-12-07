from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsItem,
    QGraphicsView,
)

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QBrush, QPainter, QKeyEvent, QColor, QPen

import numpy as np
import pandas as pd

from random import randint
import sys

from gpx_parser import read_gpx


def get_random_color():
    return QColor(randint(1, 255), randint(1, 255), randint(1, 255))


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
        circle = QGraphicsEllipseItem(-radius / 2, -radius / 2, radius, radius)
        circle.setPos(*position)

        circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        circle.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        circle.setBrush(QBrush(color))

        self.scene.addItem(circle)

    def paint_line(self, point1, point2, color):
        line = QGraphicsLineItem(int(point1[0]), int(point1[1]), int(point2[0]), int(point2[1]))
        pen = QPen(color, 4)
        line.setPen(pen)
        self.scene.addItem(line)

    def paint_path(self, points, radius=500, colors=None, show_segments=False):
        if colors is None:
            num_labels = len(set([label for _, _, label in points]))
            colors = [get_random_color() for _ in range(num_labels)]

        if show_segments:
            for i in range(len(points) - 1):
                self.paint_line(points[i][:2], points[i + 1][:2], Qt.GlobalColor.blue)

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


def view_df(df: pd.DataFrame, show_deleted=False, show_segments=False):
    BIG_NUMBER = 1e8

    df["rel_lat"] = (df["lat"] - df["lat"].min()) * BIG_NUMBER
    df["rel_lon"] = (df["lon"] - df["lon"].min()) * BIG_NUMBER

    max_lon = df["rel_lon"].max()
    max_lat = df["rel_lat"].max()

    app = QApplication(sys.argv)
    window = MainWindow(1.1 * max_lon, 1.1 * max_lat)

    if show_deleted:
        deleted_df = df[df["deleted"]]
        deleted_points = [
            [x, y, 0] for x, y in zip(deleted_df["rel_lat"], deleted_df["rel_lon"])
        ]
        window.paint_path(
            points=deleted_points,
            radius=1500,
            colors=[Qt.GlobalColor.black],
        )

    points = [
        [x, y, label]
        for x, y, label in zip(df["rel_lat"], df["rel_lon"], df["cluster"])
    ]
    window.paint_path(points=points, show_segments=show_segments)

    window.show()
    app.exec()


def open_gpx(dir_name, filename):
    df = read_gpx(dir_name, [filename])
    df["cluster"] = np.array([-1 for _ in range(df.shape[0])])

    view_df(df)


if __name__ == "__main__":
    open_gpx("tmp", "tmp")
