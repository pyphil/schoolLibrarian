import sqlite3
from PyQt6 import QtCore, QtWidgets
from mainwindow import Ui_MainWindow
from edit import Ui_Dialog

# 5628 InventarNr Duplikat
# SELECT MAX(InventarNr) FROM Lehrerbibliothek


class Database():
    def __init__(self):
        pass

    def opendb(self):
        self.verbindung = sqlite3.connect("tlibrary.db")
        self.c = self.verbindung.cursor()

    def closedb(self):
        self.c.close()
        self.verbindung.close()

    def getList(self):
        self.opendb()
        biblist = list(self.c.execute(
            """ SELECT * from Lehrerbibliothek """
        ))
        self.closedb()
        return biblist

    def getShelfMarkList(self):
        self.opendb()
        slist = list(self.c.execute(
            """ SELECT * from Signaturliste """
        ))
        self.closedb
        return slist

    def getLocationList(self):
        self.opendb()
        locationList = list(self.c.execute(
            """ SELECT * from Location """
        ))
        self.closedb
        return locationList

    def getFilteredList(self, k, field, location, exist_combo):
        self.opendb()
        if field == 0 and location == 0:
            flist = list(self.c.execute(
                """ SELECT * from Lehrerbibliothek
                WHERE "Titel" LIKE ? OR "Autor" LIKE ? OR InventarNr LIKE ?
                """,
                (k, k, k)))
        elif field != 0 and location == 0:
            flist = list(self.c.execute(
                """ SELECT * from Lehrerbibliothek
                WHERE ("Titel" LIKE ? OR "Autor" LIKE ? OR InventarNr LIKE ?)
                      AND "Bereich/Signatur" LIKE ?
                """,
                (k, k, k, field)))
        elif field == 0 and location != 0:
            flist = list(self.c.execute(
                """ SELECT * from Lehrerbibliothek
                WHERE ("Titel" LIKE ? OR "Autor" LIKE ? OR InventarNr LIKE ?)
                      AND "Standort" LIKE ?
                """,
                (k, k, k, location)))
        elif field != 0 and location != 0:
            flist = list(self.c.execute(
                """ SELECT * from Lehrerbibliothek
                WHERE ("Titel" LIKE ? OR "Autor" LIKE ? OR InventarNr LIKE ?)
                      AND "Bereich/Signatur" LIKE ? AND "Standort" LIKE ?
                """,
                (k, k, k, field, location)))
        self.closedb()

        finallist = []
        for i in flist:
            if exist_combo == 1 and (i[5] == 0 or i[5] == 1):
                finallist.append(i)
            elif exist_combo == 2 and i[5] == 0:
                finallist.append(i)
            elif exist_combo == 3 and i[5] == 1:
                finallist.append(i)
            elif exist_combo == 4 and i[5] == -1:
                finallist.append(i)
            elif exist_combo == 0:
                finallist.append(i)

        return finallist

    def getSelectedEntry(self, id):
        self.opendb()
        entry = list(self.c.execute(
            """ SELECT * from Lehrerbibliothek 
                WHERE id = ?
            """,
            (id,)))
        self.closedb()
        return entry


class Edit(Ui_Dialog, QtWidgets.QDialog):
    def __init__(self, main, db, entry):
        super(Edit, self).__init__(main)
        self.setupUi(self)
        self.show()
        self.db = db

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(
                self.save_entry)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel).clicked.connect(
                self.close_window)

        # fill in data
        self.lineEdit_author.setText(entry[0][0])
        self.lineEdit_title.setText(entry[0][1])
        marklist = self.db.getShelfMarkList()
        for i in marklist:
            self.comboBox_ShelfMark.addItem(i[0])
        self.comboBox_ShelfMark.setCurrentText(entry[0][2])

    def save_entry(self):
        pass
    
    def close_window(self):
        self.close()


class SchoolLib(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super(SchoolLib, self).__init__()
        self.setupUi(self)
        res = app.primaryScreen().availableGeometry()
        if res.height() <= 800:
            self.showMaximized()
        self.show()

        # Kopfzeile der Tabelle festlegen
        headers = ["Author", "Title", "Field/Shelf Mark", "Inventory Number",
                   "Location", "Existing", "ID"]
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(headers)
        # ID verstecken
        self.tableWidget.setColumnHidden(6, True)

        # Database
        self.db = Database()
        # Load signature list into combobox
        marklist = self.db.getShelfMarkList()
        self.comboBox_Field.addItem("Alle Bereiche/Signaturen")
        for i in marklist:
            self.comboBox_Field.addItem(i[0])
        self.comboBox_Field.setCurrentIndex(0)

        locationList = self.db.getLocationList()
        self.comboBox_Location.addItem("Alle Standorte")
        for i in locationList:
            self.comboBox_Location.addItem(i[0])
        self.comboBox_Location.setCurrentIndex(0)

        self.comboBox_Existing.addItem("alle")
        self.comboBox_Existing.addItem("vorhanden/prüfen!")
        self.comboBox_Existing.addItem("prüfen!")
        self.comboBox_Existing.addItem("vorhanden")
        self.comboBox_Existing.addItem("nicht vorhanden")
        self.comboBox_Existing.setCurrentIndex(0)

        self.lineEdit.setFocus()

        # signals and slots
        self.lineEdit.returnPressed.connect(self.search)
        self.pushButton.clicked.connect(self.search)
        self.comboBox_Field.activated.connect(self.search)
        self.comboBox_Location.activated.connect(self.search)
        self.comboBox_Existing.activated.connect(self.search)
        self.actionEdit_Entry.triggered.connect(self.edit)

        # Load content
        self.load_all()

        # resize to column contents at the beginning only
        self.tableWidget.resizeColumnsToContents()

    def load_all(self):
        booklist = self.db.getList()
        self.load_list(booklist)

    def load_list(self, b):
        self.tableWidget.setRowCount(len(b))

        for i in range(len(b)):
            self.tableWidget.setItem(
                i, 0, QtWidgets.QTableWidgetItem(b[i][0]))
            self.tableWidget.setItem(
                i, 1, QtWidgets.QTableWidgetItem(b[i][1]))
            self.tableWidget.setItem(
                i, 2, QtWidgets.QTableWidgetItem(b[i][2]))

            # set data role to store data as numeric to achieve
            # numerical ordering
            item = QtWidgets.QTableWidgetItem()
            item.setData(QtCore.Qt.ItemDataRole.DisplayRole, b[i][3])
            self.tableWidget.setItem(i, 3, item)

            self.tableWidget.setItem(
                i, 4, QtWidgets.QTableWidgetItem(b[i][4]))

            if b[i][5] == 1:
                exists = "vorhanden"
            elif b[i][5] == 0:
                exists = "prüfen!"
            elif b[i][5] == -1:
                exists = "nicht vorhanden"
            else:
                exists = "?"
            self.tableWidget.setItem(
                i, 5, QtWidgets.QTableWidgetItem(exists))

            # set data role to store data as numeric to achieve
            # numerical ordering
            item_id = QtWidgets.QTableWidgetItem()
            item_id.setData(QtCore.Qt.ItemDataRole.DisplayRole, b[i][6])
            self.tableWidget.setItem(i, 6, item_id)

    def search(self):
        self.tableWidget.setRowCount(0)
        keyword = self.lineEdit.text()
        keyword = "%"+keyword+"%"
        if self.comboBox_Field.currentIndex() != 0:
            field = self.comboBox_Field.currentText()
        else:
            field = 0
        if self.comboBox_Location.currentIndex() != 0:
            location = self.comboBox_Location.currentText()
        else:
            location = 0
        exist_combo = self.comboBox_Existing.currentIndex()
        booklist = self.db.getFilteredList(
            keyword, field, location, exist_combo)
        self.load_list(booklist)

    def edit(self):
        # get current id
        current_row = self.tableWidget.currentRow()
        current_id = self.tableWidget.item(current_row, 6).text()
        
        # get data from db
        entry = self.db.getSelectedEntry(current_id)

        edit_dialogue = Edit(self, self.db, entry)


if __name__ == "__main__":
    import sys
    # from os import environ
    # environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'Round'
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = SchoolLib()
    sys.exit(app.exec())
