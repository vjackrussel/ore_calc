from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton,
                             QAction, QPlainTextEdit, QMessageBox, QTableView,
                             QHeaderView, QLabel)
from PyQt5.QtCore import (pyqtSlot, QAbstractTableModel, Qt, QVariant,
                          QModelIndex, pyqtProperty)
from PyQt5.QtGui import QIcon
from datetime import date, datetime, timedelta
from pprint import pprint
from io import StringIO
import pandas as pd
import requests
import pickle
import sys

requestHeaders = {
    "User-Agent": "Asteroid appraiser by vjackrussel@gmail.com"}
requestBase = "https://esi.evetech.net/latest/markets/"
requestBridge = "/history/?datasource=tranquility&type_id="
theForgeRegionId = 10000002
delveRegionId = 10000060
regionId = theForgeRegionId
with open("ore_data_dict.pkl", "rb") as f:
    ore_data_dict = pickle.load(f)
pickle_update_required = False


def getMarketValue(typeIdInput):
    request_string = (f"{requestBase}{regionId}{requestBridge}{typeIdInput}")
    result = requests.get(request_string, headers=requestHeaders).json()[-2]
    return result["average"], datetime.strptime(result["date"],
                                                "%Y-%m-%d").date()


class DataFrameModel(QAbstractTableModel):
    DtypeRole = Qt.UserRole + 1000
    ValueRole = Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @pyqtSlot(int, Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QVariant()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()
                                       and 0 <= index.column() < self.columnCount()):
            return QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QVariant()

    def roleNames(self):
        roles = {
            Qt.DisplayRole: b"display",
            DataFrameModel.DtypeRole: b"dtype",
            DataFrameModel.ValueRole: b"value"
        }
        return roles


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Ore Calc"
        self.left = 10
        self.top = 10
        self.width = 1400
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create textboxes
        self.textbox = QPlainTextEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(400, 530)
        self.oretextbox = QPlainTextEdit(self)
        self.oretextbox.move(1104, 564)
        self.oretextbox.resize(70, 25)
        self.oretextbox.insertPlainText("22.4")
        self.icetextbox = QPlainTextEdit(self)
        self.icetextbox.move(1300, 564)
        self.icetextbox.resize(70, 25)
        self.icetextbox.insertPlainText("29.8")
        self.mercoxittextbox = QPlainTextEdit(self)
        self.mercoxittextbox.move(900, 564)
        self.mercoxittextbox.resize(70, 25)
        self.mercoxittextbox.insertPlainText("10.4")

        # Create table
        self.table = QTableView(self)
        self.table.move(440, 20)
        self.table.resize(940, 530)
        self.header = self.table.horizontalHeader()

        # Create buttons in the window
        self.calculate_button = QPushButton("Calculate Value", self)
        self.calculate_button.move(20, 560)
        self.options_button = QPushButton("Options", self)
        self.options_button.move(120, 560)

        # Create labels
        self.label = QLabel(self)
        self.label.setText("Total Value:")
        self.label.move(440, 560)
        self.orelabel = QLabel(self)
        self.orelabel.setText("Enter your ore m3/s:")
        self.orelabel.move(1000, 560)
        self.orelabel.setToolTip(
            "Default value of 22.4 m3/s based on a max skill Covetor using 2x Strip Miner I")
        self.icelabel = QLabel(self)
        self.icelabel.setText("Enter your ice m3/s:")
        self.icelabel.move(1200, 560)
        self.icelabel.setToolTip(
            "Default value of 29.8 m3/s based on a max skill Covetor using 2x Ice Harvester II")
        self.mercoxitlabel = QLabel(self)
        self.mercoxitlabel.setText("Enter your mercoxit m3/s:")
        self.mercoxitlabel.move(770, 560)
        self.mercoxitlabel.setFixedWidth(130)
        self.mercoxitlabel.setToolTip(
            "Default value of 10.4 m3/s based on a max skill Covetor using 2x Modulated Deep Core Strip Miner II with no charge")

        # Connect button to function on_click
        self.calculate_button.clicked.connect(self.on_click_calculate)
        self.show()

    @pyqtSlot()
    def on_click_calculate(self):
        global pickle_update_required
        textboxValue = self.textbox.toPlainText()
        textboxValue = StringIO(textboxValue)
        ore_m3_per_sec = float(self.oretextbox.toPlainText())
        ice_m3_per_sec = float(self.icetextbox.toPlainText())
        mercoxit_m3_per_sec = float(self.mercoxittextbox.toPlainText())
        tableValue = pd.read_csv(textboxValue, sep="\t", lineterminator="\n",
                                 names=["Ore", "Compressed Units",
                                        "Volume", "Distance"])
        tableValue = tableValue.drop(columns=['Volume', 'Distance'])
        tableValue["Ore"] = tableValue["Ore"].map(
            lambda x: "Compressed " + x)
        try:
            tableValue["Compressed Units"] = tableValue["Compressed Units"].map(
                lambda x: x.replace(',', ''))
        except Exception as e:
            print(e)
        tableValue[["Compressed Units"]] = tableValue[[
            "Compressed Units"]].apply(pd.to_numeric)
        tableValue = tableValue.groupby(
            "Ore").agg({"Compressed Units": "sum"})
        for i in ["Unit Volume", "Total Volume", "Unit Value", "ISK/Hr",
                  "Total Value"]:
            tableValue[i] = 0.00
        for i, row in tableValue.iterrows():
            tableValue.at[i, "Compressed Units"] = tableValue.at[i,
                                                                 "Compressed Units"] / ore_data_dict[i]["compression_ratio"]
            tableValue.at[i,
                          "Unit Volume"] = ore_data_dict[i]["compressed_volume"]
            tableValue.at[i, "Total Volume"] = tableValue.at[i,
                                                             "Compressed Units"] * tableValue.at[i, "Unit Volume"]
            try:
                if (date.today() - ore_data_dict[i]["date"]).days >= 5:
                    print(f"Market data for {i} too old")
                    raise Exception("market data too old")
                unit_value = ore_data_dict[i]["unit_value"]
            except Exception as e:
                print(e)
                print(f"Fetching market data for {i}")
                unit_value, date_obtained = getMarketValue(
                    ore_data_dict[i]["type_id"])
                ore_data_dict[i]["unit_value"] = unit_value
                ore_data_dict[i]["date"] = date_obtained
                pickle_update_required = True
            tableValue.at[i, "Unit Value"] = unit_value
            if ore_data_dict[i]["compression_ratio"] == 1:
                mined_compressed_units = ice_m3_per_sec / \
                    ore_data_dict[i]["volume"] * 3600
            elif "Mercoxit" in i:
                mined_compressed_units = mercoxit_m3_per_sec / \
                    ore_data_dict[i]["volume"] * 36
            else:
                mined_compressed_units = ore_m3_per_sec / \
                    ore_data_dict[i]["volume"] * 36
            isk_per_hour = mined_compressed_units * unit_value
            tableValue.at[i, "ISK/Hr"] = isk_per_hour
            tableValue.at[i, "Total Value"] = tableValue.at[i,
                                                            "Compressed Units"] * unit_value
        tableValue = tableValue.round(
            {"Unit Volume": 2, "Total Volume": 1, "Unit Value": 2, "ISK/Hr": 2, "Total Value": 2})
        tableValue = tableValue.sort_values(
            by=["Total Value"], ascending=False)
        total_value = format(tableValue["Total Value"].sum(), ",.2f")
        tableValue["ISK/Hr"] = tableValue["ISK/Hr"].apply("{:,.2f}".format)
        tableValue["Unit Value"] = tableValue["Unit Value"].apply(
            "{:,.2f}".format)
        tableValue["Total Value"] = tableValue["Total Value"].apply(
            "{:,.2f}".format)
        tableValue = tableValue.reset_index()
        model = DataFrameModel(tableValue)
        self.table.setModel(model)
        self.label.setText("Total Value: " + total_value + " ISK")
        self.label.setFixedWidth(500)
        self.header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            self.header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        if pickle_update_required:
            with open("ore_data_dict.pkl", "wb") as f:
                pickle.dump(ore_data_dict, f, pickle.HIGHEST_PROTOCOL)
            pickle_update_required = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
