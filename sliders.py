from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QSlider, QWidget, QStyle, QStyleOptionSlider, QLabel, QGroupBox
from PyQt6.QtCore import QRect, QEvent, QPoint, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor


class MultiSlider(QWidget):
    changeForward = pyqtSignal(str)
    updateValues = pyqtSignal(dict)
    
    
    def __init__(self, wid, hei):
        super().__init__()
        self.wid = wid
        self.hei = hei
        self.step = 50
        self.overstep = 0
        self.curr_min = -1
        self.curr_max = 1

        self.handles = {}
        self.MOUSE_PROX = 20

        self.setFixedWidth(wid)
        self.setFixedHeight(hei)

        self.readOnly = False
        self.expandable = False

        self.zero_mark = None    

    def setReadOnly(self, ro):
        self.readOnly = ro
        for h in self.handles:
            self.handles[h].setEnabled(not ro)

    def setExpandable(self, exp):
        self.expandable = exp

        if not self.expandable:
            self.updateRange(-1, 1)
            if self.zero_mark:
                self.zero_mark.setParent(None)
                self.zero_mark.deleteLater()
            self.zero_mark = None
        else:
            self.zero_mark = QLabel("-")
            self.zero_mark.setParent(self)

        self.checkExpansion()

        if self.expandable and len(self.handles) > 0:
            self.moveZeroMark()

    def calcRange(self):
        hrange = (self.curr_min * self.step - (self.overstep if self.expandable else 0),
                 self.curr_max * self.step + (self.overstep if self.expandable else 0),
                 self.step)
        return hrange
    
    def addHandles(self, names):
        for name in names:
            self.addHandle(name)

    def addHandle(self, name):        
        init_size = len(self.handles)
        
        handle = LabeledSlider(name, QRect(0, 0, self.wid, self.hei), self.calcRange())
        handle.setParent(self)
        handle.setMouseTracking(True)
        handle.installEventFilter(self)
        handle.setEnabled(not self.readOnly)
        handle.show()
        handle.lower()
        handle.valueChanged.connect(lambda x: self.valuesChanged({handle.name: x}))
        
        self.handles[name] = handle

        if self.expandable and init_size == 0:
            self.moveZeroMark()

    def renameHandle(self, old_name, new_name):
        self.handles[old_name].setText(new_name)
        self.handles[new_name] = self.handles[old_name]
        del self.handles[old_name]

    def deleteHandle(self, name):
        self.handles[name].setParent(None)
        self.handles[name].deleteLater()
        del self.handles[name]

    def mouseAt(self, pos):
        curr_poss = {hnd.name: (pos - hnd.currentPosition()).manhattanLength() for hnd in reversed(self.handles.values())}
        for hnd in self.handles.values():
            if curr_poss[hnd.name] <= self.MOUSE_PROX:
                hnd.raise_()
        closest = min(curr_poss, key=curr_poss.get)
        if curr_poss[closest] <= self.MOUSE_PROX:
            self.changeForward.emit(closest)

    def bringForward(self, name):
        self.handles[name].raise_()

    @pyqtSlot(dict)
    def valuesChanged(self, update):
        handlesort = sorted(self.handles.items(), key=lambda x: x[1].value())
        handlesortex = [(n, h, h.leftSide, h.currentPosition().y()) for (n, h) in handlesort]
        for i, (n, h, f, y) in enumerate(handlesortex):
            if n not in update:
                continue
            
            prev = self.MOUSE_PROX
            if i > 0:
                diff = handlesortex[i - 1][3] - y
                prev = diff

            post = self.MOUSE_PROX
            if i < len(handlesortex) - 1:
                diff = y - handlesortex[i + 1][3]
                post = diff

            ans = (prev, post)
            best = min(ans)
            best_idx = ans.index(best)

            if best <= self.MOUSE_PROX // 2:
                h.setSide(not handlesortex[i + best_idx * 2 - 1][2])
            else:
                h.setSide(False)
                
        self.updateValues.emit(update)            
            
    def getValues(self):
        return {n: h.value() for (n, h) in self.handles.items()}

    def setValues(self, update):
        for h in update:
            self.handles[h].setValue(update[h])
            
    def checkExpansion(self, handles_sorted=None):
        if not self.expandable:
            return

        if not handles_sorted:
            handles_sorted = sorted(self.handles.items(), key=lambda x: x[1].value())

        if len(handles_sorted) == 0:
            return
        
        lowest = handles_sorted[0][1].value()
        highest = handles_sorted[-1][1].value()
        new_min = self.curr_min
        new_max = self.curr_max

        hrange = self.calcRange()

        if lowest <= hrange[0]:
            new_min -= 1
        elif lowest >= (self.curr_min + 1) * self.step + self.overstep:
            new_min = (lowest - 1) // self.step

        if highest >= hrange[1]:
            new_max += 1
        elif highest <= (self.curr_max - 1) * self.step - self.overstep:
            new_max = (highest + 1) // self.step + 1

        new_min = min(-1, new_min)
        new_max = max(1, new_max)

        if new_min != self.curr_min or new_max != self.curr_max:
            self.updateRange(new_min, new_max)

    def updateRange(self, new_min, new_max):
        self.curr_min = new_min
        self.curr_max = new_max

        hrange = self.calcRange()

        for h in self.handles.values():
            h.setMinimum(hrange[0])
            h.setMaximum(hrange[1])
            h.moveText(h.value())

        if self.expandable and len(self.handles) > 0:
            self.moveZeroMark()

    def moveZeroMark(self):
        first_h = self.handles[list(self.handles.keys())[0]]
        self.zero_mark.move(QPoint(self.zero_mark.width(), first_h.valueToY(0) - self.zero_mark.height() // 2))
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseMove and event.buttons() == Qt.MouseButton.NoButton:
            self.mouseAt(source.mapToGlobal(event.pos()))
        elif event.type() == QEvent.Type.MouseButtonPress and event.buttons() == Qt.MouseButton.RightButton:
            self.children()[-1].lower()
        elif event.type() == QEvent.Type.MouseButtonRelease and self.expandable and \
            not (event.buttons() & Qt.MouseButton.LeftButton):
            if any([self.handles[h].isSliderDown() for h in self.handles]):
                self.checkExpansion()

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
