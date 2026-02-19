import sys

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QStyle, QHBoxLayout, QStyleOptionSlider, QLabel
from PyQt6.QtCore import QRect, QEvent, QPoint, Qt, pyqtSignal, pyqtSlot

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

        options = ["hey", "wow", "omg", "aah", ":))"]

        self.all_sliders = []
        for i in range(5):
            mslider = MultiSlider(100, 300)
            mslider.addHandles(options)
            mslider.changeForward.connect(self.newForward)
            slider_row.addWidget(mslider)
            self.all_sliders.append(mslider)

    @pyqtSlot(str)
    def newForward(self, name):
        for slider in self.all_sliders:
            slider.bringForward(name)
        

class MultiSlider(QWidget):
    changeForward = pyqtSignal(str)
    
    def __init__(self, wid, hei):
        super().__init__()
        self.wid = wid
        self.hei = hei

        self.handles = {}
        self.MOUSE_PROX = 20

        self.setFixedWidth(wid)
        self.setFixedHeight(hei)

    def addHandles(self, names):
        for name in names:
            self.addHandle(name)

    def addHandle(self, name):
        handle = LabeledSlider(name, QRect(0, 0, self.wid, self.hei), (-50, 50))
        handle.setParent(self)
        handle.setMouseTracking(True)
        handle.installEventFilter(self)

        self.handles[name] = handle

    def renameHandle(self, old_name, new_name):
        self.handles[old_name].setText(new_name)
        self.handles[new_name] = self.handles[old_name]
        del self.handles[old_name]

    def deleteHandle(self, name):
        self.handles[name].deleteLater()
        del self.handles[name]

    def mouseAt(self, pos):
        curr_poss = {name: (pos - hnd.currentPosition()).manhattanLength() for name, hnd in reversed(self.handles.items())}
        closest = min(curr_poss, key=curr_poss.get)
        if curr_poss[closest] <= self.MOUSE_PROX:
            # brindForward(closest)
            self.changeForward.emit(closest)

    def bringForward(self, name):
        for o_name in self.handles:
            if o_name != name:
                self.handles[o_name].stackUnder(self.handles[name])
        
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.NoButton:
            self.mouseAt(source.mapToGlobal(event.pos()))
        return QWidget.eventFilter(self, source, event)


class LabeledSlider(QSlider):
    def __init__(self, text, geometry, range):
        super().__init__()

        self.setGeometry(geometry)
        self.setMinimum(range[0])
        self.setMaximum(range[1])
        
        metric = QStyle.PixelMetric.PM_SliderLength
        self.span = self.style().pixelMetric(metric, QStyleOptionSlider(), self)

        self.setTracking(True)

        self.label = QLabel()
        self.setText(text)
        self.label.setStyleSheet("QLabel { background-color : silver; color : black; }")
        self.label.setParent(self)
        self.label.move(QPoint(60, self.valueToY(0) - 10))
        
        self.valueChanged.connect(self.changed)

    def setText(self, text):
        self.label.setText(" " + text + " ")

    @pyqtSlot(int)
    def changed(self, val):
        self.label.move(QPoint(60, self.valueToY(val) - 10))

    def currentPosition(self):
        return self.mapToGlobal(QPoint(self.width() // 2, self.valueToY(self.value())))

    def valueToY(self, val):
        return int(self.height() - QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), val, self.height() - self.span) - self.span / 2)        


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DecisionWindow()
    window.show()

    sys.exit(app.exec())
