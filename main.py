import sys

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QStyle
from PyQt6.QtCore import QRect, QEvent, QPoint, Qt

class DecisionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Decision Axes")


        self.sliders = MultiSlider(5, 50, 300)
        
        self.setCentralWidget(self.sliders)


    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove:
            if self.sliders.underMouse() and event.buttons() == Qt.MouseButton.NoButton:
                self.sliders.mouseAt(event.pos())
            
        return QMainWindow.eventFilter(self, source, event)


class MultiSlider(QWidget):
    def __init__(self, num: int, w: int, h: int):
        super().__init__()

        self.handles = [QSlider(self) for i in range(num)]
        self.MOUSE_PROX = 20

        for handle in self.handles:
            handle.setGeometry(QRect(0, 0, w, h))

    def currPos(self, handle):
        y = handle.height() - QStyle.sliderPositionFromValue(handle.minimum(), handle.maximum(), handle.value(), handle.height())
        return self.mapToGlobal(QPoint(int(handle.x() + handle.width() / 2), y))

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
