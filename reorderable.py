from PyQt6.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QWidget, QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QLayout
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt

class ReorderTray(QGroupBox):

    entryChanged = pyqtSignal(str, str)

    def __init__(self, maxcols, horizpanel, generator, title):
        super().__init__(title)

        self.maxcols = maxcols
        self.horizpanel = horizpanel
        self.generator = generator

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.creator = QLineEdit()
        self.creator.editingFinished.connect(self.createNew)

        self.reorderables = []
        self.source = -1

        self.refillGrid()

    def blankPanel(self):
        r = Reorderable(-1, self.horizpanel, self.generator() if self.generator else None)
        r.selected.connect(self.buttonSelected)
        r.nameChanged.connect(self.nameChanged)
        return r

    def getItems(self):
        return [(self.reorderables[i].entryName, self.reorderables[i].inside) for i in range(len(self.reorderables))]

    def insertAt(self, reorderable, idx):
        self.reorderables.insert(idx, reorderable)
        self.refillGrid()

    def removeAt(self, idx):
        r = self.reorderables.pop(idx)
        self.refillGrid()
        return r

    def refillGrid(self):
        while self.grid.takeAt(0):
            pass

        for i, r in enumerate(self.reorderables):
            coords = self.idxToCoords(i)
            self.grid.addWidget(r, coords[0], coords[1], alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            r.idx = i

        lastcoord = self.idxToCoords(len(self.reorderables))
        self.grid.addWidget(self.creator, lastcoord[0], lastcoord[1])

        cols = self.grid.columnCount()
        for i in range(cols):
            self.grid.setColumnStretch(i, 0)
        self.grid.setColumnStretch(cols, 1)
        
        rows = self.grid.rowCount()
        for i in range(rows):
            self.grid.setRowStretch(i, 0)
        self.grid.setRowStretch(rows, 1)
        

    @pyqtSlot()
    def createNew(self):
        if self.creator.text() == "":
            return
        
        new_blank = self.blankPanel()
        self.insertAt(new_blank, len(self.reorderables))
        new_blank.setName(self.creator.text())
        self.creator.setText("")
        
    @pyqtSlot(int, str, str)
    def nameChanged(self, idx, oldname, newname):
        samename = [item for i, item in enumerate(self.getItems()) if i != idx and item[0] == newname]

        if len(samename) > 0:
            self.reorderables[idx].setName(newname + "*")
            return

        if newname == "":
            r = self.removeAt(idx) 
            r.selected.disconnect(self.buttonSelected)
            r.nameChanged.disconnect(self.nameChanged)
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
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # self.setFixedHeight(50)

        self.entryName = ""
        self.nameEdit = QLineEdit()
        self.nameEdit.editingFinished.connect(self.editingFinished)
        layout.addWidget(self.nameEdit)

        self.inside = inside
        if inside:
            layout.addWidget(inside, alignment=Qt.AlignmentFlag.AlignCenter)

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
            self.nameChanged.emit(self.idx, oldname, newname)
            self.entryName = self.nameEdit.text()

    @pyqtSlot()
    def setState(self, isSource, fault):
        if not isSource:
            if fault == self.idx:
                self.controlButton.setText("⦿")
            else:
                self.controlButton.setText("○")
        else:
            self.controlButton.setText("●")
