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
        

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.NoButton:
            for slider in self.all_sliders:
                slider.mouseAt(event.pos())
            
        return QMainWindow.eventFilter(self, source, event)


class MultiSlider(QWidget):
    def __init__(self, num: int, w: int, h: int):
        super().__init__()

        self.handles = [QSlider(self) for i in range(num)]
        self.MOUSE_PROX = 20

        self.setFixedWidth(w * 2)
        self.setFixedHeight(h)

        for handle in self.handles:
            handle.setGeometry(QRect(int(w / 2), 0, w, h))
            handle.setMinimum(-50)
            handle.setMaximum(50)

    def currPos(self, handle):
        span = handle.style().pixelMetric(QStyle.PixelMetric.PM_SliderLength, QStyleOptionSlider(), handle)
        y = handle.height() - QStyle.sliderPositionFromValue(handle.minimum(), handle.maximum(), handle.value(), handle.height() - span) - span
        return self.mapToGlobal(QPoint(int(handle.x() + handle.width() / 2), int(handle.y() + y)))

    def mouseAt(self, pos):
        curr_poss = [(pos - self.currPos(hnd)).manhattanLength() for hnd in self.handles]
        closest = curr_poss.index(min(curr_poss))
        if curr_poss[closest] <= self.MOUSE_PROX:
            for i, hnd in enumerate(self.handles):
                if i != closest:
                    hnd.stackUnder(self.handles[closest])
        

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DecisionWindow()
    window.show()
    app.installEventFilter(window)

    sys.exit(app.exec())
