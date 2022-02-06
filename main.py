import sys
import sqlite3

from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QLabel, \
    QLineEdit, QDialog, QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(self.width(), self.height())
        self.db = sqlite3.connect('coffee.sqlite')
        self.curs = self.db.cursor()
        self.update_view()
        self.add.clicked.connect(self.run_edit)
        self.selected = None
        self.view.itemSelectionChanged.connect(self.select)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.update_view()

    def select(self):
        self.selected = self.view.selectedItems()
        if self.selected:
            row = self.selected[0].row()
            for i in self.selected:
                if i.row() == row:
                    continue
                else:
                    self.selected = None
                    break
        else:
            self.selected = None
        if self.selected and len(self.selected) != 7:
            self.selected = None
        if self.selected:
            new = []
            for i in self.selected:
                new.append(i.text())
            self.selected = new

    def run_edit(self):
        mode = 'Edit' if self.selected else 'New'
        print(mode)
        edited, values = EditForm(self, self.selected[1:] if self.selected else None).exec_()
        if edited:
            if mode == 'New':
                p1, p2, p3, p4, p5, p6 = values
                values = (self.get_free_id(), p1, p2, p3, p4, p5, p6)
                self.curs.execute(f'INSERT INTO coffee VALUES (?,?,?,?,?,?,?)', values)
                self.db.commit()
                self.update_view()
            else:
                self.curs.execute(f'''UPDATE coffee
                SET sort = ?, bake = ?, type = ?, description = ?, price = ?, volume = ?
                WHERE id == {int(self.selected[0])}''', values)
                self.db.commit()
                self.update_view()

    def update_view(self):
        self.list_coffee = self.curs.execute("SELECT * FROM coffee").fetchall()
        self.view.setRowCount(len(self.list_coffee))
        self.view.setColumnCount(len(self.list_coffee[0]))
        self.view.setHorizontalHeaderLabels(['ID', 'Name', 'Bake level', 'Type',
                                             'Description', 'Price', 'Packing Volume'])
        for i, cell in enumerate(self.list_coffee):
            for j, value in enumerate(cell):
                self.view.setItem(i, j, QTableWidgetItem(str(value)))

    def get_free_id(self):
        max_id = len(self.list_coffee)
        for i in range(10000):
            if i == max_id:
                return i + 1
            if self.list_coffee[i][0] == i + 1:
                continue
            else:
                return i + 1


class EditForm(QDialog):
    def __init__(self, parent=None, params=None):
        super().__init__(parent, Qt.WindowCloseButtonHint)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.edited = False
        self.p3.itemSelectionChanged.connect(self.select)
        if params:
            self.v1, self.v2, self.v3, self.v4, self.v5, self.v6 = params
        else:
            self.v1, self.v2, self.v3, self.v4, self.v5, self.v6 = ('', '', 'Молотый', '', 0, 0)
        self.set()
        self.save.clicked.connect(self.commit)

    def set(self):
        self.p1.setText(self.v1)
        self.p2.setText(self.v2)
        self.p3.setCurrentRow(['Молотый', 'В зернах'].index(self.v3))
        self.p4.setText(self.v4)
        self.p5.setText(str(self.v5))
        self.p6.setText(str(self.v6))

    def select(self):
        self.selected = self.p3.selectedItems()[0].text()

    def commit(self):
        try:
            self.v1, self.v2, self.v3, self.v4, self.v5, self.v6 = \
                self.p1.toPlainText(), self.p2.toPlainText(), self.selected, \
                self.p4.toPlainText(), int(self.p5.text()), int(self.p6.text())
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Цена и обьем упаковки должны быть числом', QMessageBox.Ok)
            return
        if not all([self.v1, self.v2, self.v2, self.v4, self.v5, self.v6]):
            QMessageBox.critical(self, 'Ошибка', 'Заполнены не все параметры', QMessageBox.Ok)
        else:
            self.edited = True
            self.exec_()

    def exec_(self):
        super(EditForm, self).exec_()
        self.close()
        return self.edited, (self.v1, self.v2, self.v3, self.v4, self.v5, self.v6)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    f = Window()
    f.show()
    sys.exit(app.exec())
