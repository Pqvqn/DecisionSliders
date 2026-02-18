import sys

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QStyle, QHBoxLayout, QStyleOptionSlider
from PyQt6.QtCore import QRect, QEvent, QPoint, Qt

class DecisionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Decision Axes")


        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        slider_row = QHBoxLayout()
        layout.addLayout(slider_row)

        self.all_sliders = []
        for i in range(5):
            mslider = MultiSlider(5, 50, 300)
            slider_row.addWidget(mslider)
            self.all_sliders.append(mslider)      


class MultiSlider(QWidget):
    def __init__(self, num: int, w: int, h: int):
        super().__init__()

        self.handles = [QSlider(self) for i in range(num)]
        self.MOUSE_PROX = 20

        self.setFixedWidth(w * 2)
        self.setFixedHeight(h)

        for handle in self.handles:
            handle.setMouseTracking(True)
            handle.installEventFilter(self)
            handle.setGeometry(QRect(int(w / 2), 0, w, h))
            handle.setMinimum(-50)
            handle.setMaximum(50)

    def currPos(self, handle):
        metric = QStyle.PixelMetric.PM_SliderLength
        span = handle.style().pixelMetric(metric, QStyleOptionSlider(), handle)
        y = handle.height() - QStyle.sliderPositionFromValue(handle.minimum(), handle.maximum(), handle.value(), handle.height() - span) - span / 2
        return self.mapToGlobal(QPoint(int(handle.width() / 2 + handle.x()), int(y + handle.y())))

    def mouseAt(self, pos):
        curr_poss = [(pos - self.currPos(hnd)).manhattanLength() for hnd in self.handles]
        closest = curr_poss.index(min(curr_poss))
        if curr_poss[closest] <= self.MOUSE_PROX:
            for i, hnd in enumerate(self.handles):
                if i != closest:
                    hnd.stackUnder(self.handles[closest])
     
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.NoButton:
            self.mouseAt(source.mapToGlobal(event.pos()))
        return QWidget.eventFilter(self, source, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DecisionWindow()
    window.show()

    sys.exit(app.exec())
