import sqlite3
from PyQt6 import QtCore, QtWidgets
from datetime import datetime
from mainwindow import Ui_MainWindow
from edit import Ui_Dialog

# 5628 InventarNr Duplikat macht nichts
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

    def getNextIventoryNumber(self):
        self.opendb()
        next_inv_no = self.c.execute(
            """ SELECT MAX(InventarNr) from Lehrerbibliothek
            """,).fetchone()
        self.closedb()
        return next_inv_no[0]

    def saveEntry(self, data, new_id, time):
        self.opendb()
        self.c.execute(
            """ INSERT INTO Lehrerbibliothek
                (Autor, Titel, "Bereich/Signatur",
                InventarNr, Standort, Vorhanden, ID, Erstellungsdatum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (data[0], data[1], data[2], data[3],
             data[4], data[5], new_id, time)
        )
        self.verbindung.commit()
        self.closedb

    def updateEntry(self, data, current_id, time):
        self.opendb()
        self.c.execute(
            """ UPDATE Lehrerbibliothek
                SET Autor = ?, Titel = ?, "Bereich/Signatur" = ?,
                    InventarNr = ?, Standort = ?, Vorhanden = ?,
                    LetzteAenderung = ?
                WHERE ID = ?
            """,
            (data[0], data[1], data[2], data[3], data[4], data[5],
             time, current_id)
        )
        self.verbindung.commit()
        self.closedb


class Edit(Ui_Dialog, QtWidgets.QDialog):
    def __init__(self, main, db, entry, current_id):
        super(Edit, self).__init__(main)
        self.setupUi(self)
        self.show()
        self.db = db
        self.current_id = current_id
        self.main = main

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(
                self.update_entry)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel).clicked.connect(
                self.close_window)

        self.comboBox_existing.setStyleSheet("combobox-popup: 0;")
        self.comboBox_location.setStyleSheet("combobox-popup: 0;")
        self.comboBox_ShelfMark.setStyleSheet("combobox-popup: 0;")

        # fill in data
        self.lineEdit_author.setText(entry[0][0])
        self.lineEdit_title.setText(entry[0][1])

        marklist = self.db.getShelfMarkList()
        for i in marklist:
            self.comboBox_ShelfMark.addItem(i[0])
        self.comboBox_ShelfMark.setCurrentText(entry[0][2])

        self.spinBox_inventoryNumber.setValue(entry[0][3])

        locationList = self.db.getLocationList()
        self.comboBox_location.addItem("")
        for i in locationList:
            self.comboBox_location.addItem(i[0])
        # self.comboBox_location.setCurrentIndex(0)
        self.comboBox_location.setCurrentText(entry[0][4])

        self.comboBox_existing.addItem("prüfen!")
        self.comboBox_existing.addItem("vorhanden")
        self.comboBox_existing.addItem("nicht vorhanden")
        # self.comboBox_existing.setCurrentIndex(0)
        if entry[0][5] == 0:
            self.comboBox_existing.setCurrentIndex(0)
        elif entry[0][5] == 1:
            self.comboBox_existing.setCurrentIndex(1)
        elif entry[0][5] == -1:
            self.comboBox_existing.setCurrentIndex(2)

    def update_entry(self):
        data = []

        # Author
        data.append(self.lineEdit_author.text())
        # Title
        data.append(self.lineEdit_title.text())
        # Shelf Mark
        data.append(self.comboBox_ShelfMark.currentText())
        # Inventory Number
        data.append(self.spinBox_inventoryNumber.value())
        # location
        data.append(self.comboBox_location.currentText())
        # existing
        val = self.comboBox_existing.currentIndex()
        if val == 0:
            data.append(0)
        elif val == 1:
            data.append(1)
        elif val == 2:
            data.append(-1)

        # time
        time = datetime.strftime(datetime.now(), "%d. %b %Y, %H:%M")

        self.db.updateEntry(data, self.current_id, time)
        self.close_window()
        self.main.search()

    def close_window(self):
        self.close()


class New(Ui_Dialog, QtWidgets.QDialog):
    def __init__(self, main, db):
        super(New, self).__init__(main)
        self.setupUi(self)
        self.show()
        self.db = db
        self.main = main

        # Make changes to Gui
        self.setWindowTitle("Neuer Eintrag")
        self.groupBox_2.setTitle("Eingabe der Details des neuen Mediums:")

        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(
                self.save_entry)
        self.buttonBox.button(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel).clicked.connect(
                self.close_window)

        self.comboBox_existing.setStyleSheet("combobox-popup: 0;")
        self.comboBox_location.setStyleSheet("combobox-popup: 0;")
        self.comboBox_ShelfMark.setStyleSheet("combobox-popup: 0;")

        marklist = self.db.getShelfMarkList()
        for i in marklist:
            self.comboBox_ShelfMark.addItem(i[0])

        # Get next inventory number
        self.new_id = self.db.getNextIventoryNumber()+1
        self.spinBox_inventoryNumber.setValue(self.new_id)

        locationList = self.db.getLocationList()
        self.comboBox_location.addItem("")
        for i in locationList:
            self.comboBox_location.addItem(i[0])
        # self.comboBox_location.setCurrentIndex(0)

        self.comboBox_existing.addItem("prüfen!")
        self.comboBox_existing.addItem("vorhanden")
        self.comboBox_existing.addItem("nicht vorhanden")
        self.comboBox_existing.setCurrentIndex(1)

    def save_entry(self):
        data = []

        # Author
        data.append(self.lineEdit_author.text())
        # Title
        data.append(self.lineEdit_title.text())
        # Shelf Mark
        data.append(self.comboBox_ShelfMark.currentText())
        # Inventory Number
        data.append(self.spinBox_inventoryNumber.value())
        # location
        data.append(self.comboBox_location.currentText())
        # existing
        val = self.comboBox_existing.currentIndex()
        if val == 0:
            data.append(0)
        elif val == 1:
            data.append(1)
        elif val == 2:
            data.append(-1)

        # time
        time = datetime.strftime(datetime.now(), "%d. %b %Y, %H:%M")

        self.db.saveEntry(data, self.new_id, time)
        self.close_window()
        self.main.search()

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
        headers = ["Autor", "Titel", "Bereich/Signatur", "Inventarnummer",
                   "Standort", "Vorhanden", "ID"]
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(headers)
        # ID verstecken
        self.tableWidget.setColumnHidden(6, True)

        self.tableWidget.clicked.connect(self.enableButtons)

        # Stil Combobox für Fusion ändern
        self.comboBox_Field.setStyleSheet("combobox-popup: 0;")
        self.comboBox_Location.setStyleSheet("combobox-popup: 0;")
        self.comboBox_Existing.setStyleSheet("combobox-popup: 0;")

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
        self.comboBox_Existing.setCurrentIndex(1)

        self.lineEdit.setFocus()

        # signals and slots
        self.lineEdit.returnPressed.connect(self.search)
        self.pushButton.clicked.connect(self.search)
        self.comboBox_Field.activated.connect(self.search)
        self.comboBox_Location.activated.connect(self.search)
        self.comboBox_Existing.activated.connect(self.search)
        self.actionNew.triggered.connect(self.new)
        self.actionEdit_Entry.triggered.connect(self.edit)
        self.tableWidget.clicked.connect(self.updateDetails)

        # deactivate Toolbar Buttons
        self.actionEdit_Entry.setEnabled(False)
        self.actionDelete_Entry.setEnabled(False)

        # Load content
        self.load_all()

        # resize to column contents at the beginning only
        self.tableWidget.resizeColumnsToContents()

        self.tableWidget.keyPressEvent = self.key

    # react on keypress to update details
    def key(self, e):
        if e.key() == QtCore.Qt.Key.Key_Down:
            self.tableWidget.selectRow(self.tableWidget.currentRow() + 1)
            self.updateDetails()
        if e.key() == QtCore.Qt.Key.Key_Up:
            self.tableWidget.selectRow(self.tableWidget.currentRow() - 1)
            self.updateDetails()

    def enableButtons(self):
        self.actionEdit_Entry.setEnabled(True)
        self.actionDelete_Entry.setEnabled(True)

    def disableButtons(self):
        self.actionEdit_Entry.setEnabled(False)
        self.actionDelete_Entry.setEnabled(False)

    def load_all(self):
        booklist = self.db.getList()
        self.load_list(booklist)

    def load_list(self, b):
        self.disableButtons()
        # disable sorting that might be turned on in tableWidget to loop
        # through rows successfully
        self.tableWidget.setSortingEnabled(False)

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

        # turn on sorting again
        self.tableWidget.setSortingEnabled(True)

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

    def new(self):
        New(self, self.db)

    def edit(self):
        # get current id
        current_row = self.tableWidget.currentRow()
        current_id = self.tableWidget.item(current_row, 6).text()

        # get data from db
        entry = self.db.getSelectedEntry(current_id)

        Edit(self, self.db, entry, current_id)

    def updateDetails(self):
        # get current id
        current_row = self.tableWidget.currentRow()
        current_id = self.tableWidget.item(current_row, 6).text()

        # get data from db
        entry = self.db.getSelectedEntry(current_id)

        self.lineEdit_created.setText(entry[0][10])
        self.lineEdit_lastEdited.setText(entry[0][7])


if __name__ == "__main__":
    import sys
    # from os import environ
    # environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'Round'
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = SchoolLib()
    sys.exit(app.exec())
