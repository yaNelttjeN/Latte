import sys
import sqlite3

from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QLabel, \
    QLineEdit, QWidget, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5 import uic


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(self.width(), self.height())
        self.db = sqlite3.connect('coffee.sqlite')
        self.curs = self.db.cursor()
        self.list_coffee = self.curs.execute("SELECT * FROM coffee").fetchall()
        self.view.setRowCount(len(self.list_coffee))
        self.view.setColumnCount(len(self.list_coffee[0]))
        self.view.setHorizontalHeaderLabels(['ID', 'Name', 'Bake level', 'Type',
                                             'Description', 'Price', 'Packing Volume'])
        for i, cell in enumerate(self.list_coffee):
            for j, value in enumerate(cell):
                self.view.setItem(i, j, QTableWidgetItem(str(value)))
        self.setMouseTracking(True)
        self.add.clicked.connect(self.info)

    def info(self):
        print(self.width())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    f = Window()
    f.show()
    sys.exit(app.exec())