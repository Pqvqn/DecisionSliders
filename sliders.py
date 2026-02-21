from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QSlider, QWidget, QStyle, QStyleOptionSlider, QLabel, QGroupBox
from PyQt6.QtCore import QRect, QEvent, QPoint, Qt, pyqtSignal, pyqtSlot


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

        self.readOnly = False


    def setReadOnly(self, ro):
        self.readOnly = ro
        for h in self.handles:
            self.handles[h].setEnabled(not ro)

    def addHandles(self, names):
        for name in names:
            self.addHandle(name)

    def addHandle(self, name):
        handle = LabeledSlider(name, QRect(0, 0, self.wid, self.hei), (-50, 50, 50))
        handle.setParent(self)
        handle.setMouseTracking(True)
        handle.installEventFilter(self)
        handle.setEnabled(not self.readOnly)
        handle.show()
        handle.lower()
        handle.valueChanged.connect(lambda x: self.valuesChanged({handle.name: x}))
        
        self.handles[name] = handle

    def renameHandle(self, old_name, new_name):
        self.handles[old_name].setText(new_name)
        self.handles[new_name] = self.handles[old_name]
        del self.handles[old_name]

    def deleteHandle(self, name):
        self.handles[name].setParent(None)
        self.handles[name].deleteLater()
        del self.handles[name]

    def mouseAt(self, pos):
        curr_poss = {hnd.name: (pos - hnd.currentPosition()).manhattanLength() for hnd in reversed(self.children())}
        for hnd in self.children():
            if curr_poss[hnd.name] <= self.MOUSE_PROX:
                hnd.raise_()
        closest = min(curr_poss, key=curr_poss.get)
        if curr_poss[closest] <= self.MOUSE_PROX:
            # brindForward(closest)
            self.changeForward.emit(closest)

    def bringForward(self, name):
        self.handles[name].raise_()

    @pyqtSlot(dict)
    def valuesChanged(self, update):
        handlesort = sorted(self.handles.items(), key=lambda x: x[1].value())
        handlesort = [(n, h, h.leftSide, h.currentPosition().y()) for (n, h) in handlesort]
        for i, (n, h, f, y) in enumerate(handlesort):
            if n not in update:
                continue
            
            prev = self.MOUSE_PROX
            if i > 0:
                diff = handlesort[i - 1][3] - y
                prev = diff

            post = self.MOUSE_PROX
            if i < len(handlesort) - 1:
                diff = y - handlesort[i + 1][3]
                post = diff

            ans = (prev, post)
            best = min(ans)
            best_idx = ans.index(best)

            if best <= self.MOUSE_PROX // 2:
                h.setSide(not handlesort[i + best_idx * 2 - 1][2])
            else:
                h.setSide(False)                 
            
        
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.NoButton:
            self.mouseAt(source.mapToGlobal(event.pos()))
        elif event.type() == QEvent.Type.MouseButtonPress and event.buttons() == Qt.MouseButton.RightButton:
            self.children()[-1].lower()
        return QWidget.eventFilter(self, source, event)


class LabeledSlider(QSlider):
    def __init__(self, text, geometry, range):
        super().__init__()

        self.setGeometry(geometry)
        self.setMinimum(range[0])
        self.setMaximum(range[1])
        self.setTickInterval(range[2])
        self.setTickPosition(QSlider.TickPosition.TicksBothSides)

        self.leftSide = True
        
        # self.setStyleSheet("QSlider::groove:vertical { width: 3px; margin: 0 0; background-color: grey }")
        
        metric = QStyle.PixelMetric.PM_SliderLength
        self.span = self.style().pixelMetric(metric, QStyleOptionSlider(), self)

        self.setTracking(True)

        self.name = ""
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(self.width() // 2 - 13)
        self.setText(text)
        self.label.setStyleSheet("QLabel { background-color : gainsboro; color : black; }")
        self.label.setParent(self)
        self.moveText(0)
        
        self.valueChanged.connect(self.changed)
        self.valueChanged.emit(0)

    def setText(self, text):
        self.name = text
        self.label.setText(" " + text + " ")
        self.label.show()

    def setSide(self, leftSide):
        self.leftSide = leftSide
        self.moveText(self.value())

    def moveText(self, val):
        self.label.move(QPoint(self.width() // 2 + (-self.label.width() - 10 if self.leftSide else 10), self.valueToY(val) - 10))

    @pyqtSlot(int)
    def changed(self, val):
        self.moveText(val)

    def currentPosition(self):
        return self.mapToGlobal(QPoint(self.width() // 2, self.valueToY(self.value())))

    def valueToY(self, val):
        return int(self.height() - QStyle.sliderPositionFromValue(self.minimum(), self.maximum(), val, self.height() - self.span) - self.span / 2)        
