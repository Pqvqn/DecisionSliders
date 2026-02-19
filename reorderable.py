from PyQt6.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QLayout
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt

class ReorderTray(QFrame):

    entryChanged = pyqtSignal(str, str)

    def __init__(self, maxcols, horizpanel, generator):
        super().__init__()

        self.maxcols = maxcols
        self.horizpanel = horizpanel
        self.generator = generator

        self.setFrameShape(QFrame.Shape.Box)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.reorderables = [self.blankPanel()]
        self.source = -1

        self.refillGrid()

    def blankPanel(self):
        return Reorderable(-1, self.horizpanel, self.generator() if self.generator else None)

    def getItems(self):
        return [(self.reorderables[i].entryName, self.reorderables[i].inside) for i in range(len(self.reorderables) - 1)]

    def insertAt(self, reorderable, idx):
        self.reorderables.insert(idx, reorderable)
        self.refillGrid()

    def removeAt(self, idx):
        r = self.reorderables.pop(idx)
        self.refillGrid()
        return r

    def refillGrid(self):
        removed = set()
        
        while item := self.grid.takeAt(0):
            r = item.widget()
            if r is not None:
                removed.add(r)
                if r not in self.reorderables:
                    r.selected.disconnect(self.buttonSelected)
                    r.nameChanged.disconnect(self.nameChanged)

        for i, r in enumerate(self.reorderables):
            coords = self.idxToCoords(i)
            self.grid.addWidget(r, coords[0], coords[1], alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            r.idx = i
            if r not in removed:
                r.selected.connect(self.buttonSelected)
                r.nameChanged.connect(self.nameChanged)
            if i < len(self.reorderables) - 1:
                self.reorderables[i].controlButton.show()
            else:
                self.reorderables[i].controlButton.hide()

        cols = self.grid.columnCount()
        for i in range(cols):
            self.grid.setColumnStretch(i, 0)
        self.grid.setColumnStretch(cols, 1)
        
        rows = self.grid.rowCount()
        for i in range(rows):
            self.grid.setRowStretch(i, 0)
        self.grid.setRowStretch(rows, 1)
        
        
    @pyqtSlot(int, str, str)
    def nameChanged(self, idx, oldname, newname):
        samename = [item for i, item in enumerate(self.getItems()) if i != idx and item[0] == newname]
        if len(samename) > 0:
            self.reorderables[idx].setName(newname + "*")
            return

        if idx == len(self.reorderables) - 1:
            new_blank = self.blankPanel()
            self.insertAt(new_blank, len(self.reorderables))
            new_blank.nameEdit.setFocus()
        elif newname == "":
            r = self.removeAt(idx)
            r.deleteLater()
            
        self.entryChanged.emit(oldname, newname)
            
    
    @pyqtSlot(int)
    def buttonSelected(self, idx):
        isDest = self.source >= 0

        if isDest:
            wid = self.removeAt(self.source)
            self.insertAt(wid, idx if idx <= self.source else idx)
            self.source = -1
        else:
            self.source = idx

        for r in self.reorderables:
            r.setState(isDest, idx)
            
    def idxToCoords(self, idx):
        if self.maxcols <= 0:
            return (0, idx)
        return (idx // self.maxcols, idx % self.maxcols)
        

class Reorderable(QWidget):

    selected = pyqtSignal(int)
    nameChanged = pyqtSignal(int, str, str)

    def __init__(self, idx, horiz, inside):
        super().__init__()

        self.idx = idx
        layout = QHBoxLayout() if horiz else QVBoxLayout()
        self.setLayout(layout)

        self.inside = inside

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.setFixedHeight(50)

        self.entryName = ""
        self.nameEdit = QLineEdit()
        self.nameEdit.editingFinished.connect(self.editingFinished)
        layout.addWidget(self.nameEdit)

        if inside:
            layout.addWidget(inside)

        self.controlButton = QPushButton()
        self.controlButton.setFixedSize(20, 20)
        # self.controlButton.setCheckable(True)
        self.controlButton.pressed.connect(self.pressed)
        layout.addWidget(self.controlButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setState(True, -1)

    def setName(self, name):
        self.nameEdit.setText(name)
        self.editingFinished()
    
    def pressed(self):
        self.selected.emit(self.idx)

    @pyqtSlot()
    def editingFinished(self):
        newname = self.nameEdit.text()
        oldname = self.entryName
        if newname != oldname:
            self.entryName = newname
            self.nameChanged.emit(self.idx, oldname, newname)

    @pyqtSlot()
    def setState(self, isSource, fault):
        if not isSource:
            if fault == self.idx:
                self.controlButton.setText("⦿")
            else:
                self.controlButton.setText("○")
        else:
            self.controlButton.setText("●")
