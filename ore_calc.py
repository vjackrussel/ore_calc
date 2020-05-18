from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, QAction,
                             QPlainTextEdit, QMessageBox, QTableView, QHeaderView, QLabel)
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, Qt, QVariant, QModelIndex, pyqtProperty
from PyQt5.QtGui import QIcon
from datetime import date, datetime, timedelta
from pprint import pprint
from io import StringIO
import pandas as pd
import requests
import pickle
import sys

requestHeaders = {"User-Agent": "Asteroid appraiser by vjackrussel@gmail.com"}
requestBase = "https://esi.evetech.net/latest/markets/"
requestBridge = "/history/?datasource=tranquility&type_id="
theForgeRegionId = 10000002
delveRegionId = 10000060
regionId = theForgeRegionId

with open("ore_data_dict.pkl", "rb") as f:
    ore_data_dict = pickle.load(f)
pickleUpdateRequired = False


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
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
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

        self.textbox = QPlainTextEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(400, 530)

        self.table = QTableView(self)
        self.table.move(440, 20)
        self.table.resize(940, 530)
        self.header = self.table.horizontalHeader()

        self.totalValueLabel = QLabel(self)
        self.totalValueLabel.move(445, 560)
        self.totalValueLabel.setText("Total Value:")

        self.orelabel = QLabel(self)
        self.oretextbox = QPlainTextEdit(self)
        self.orelabel.move(1022, 560)
        self.oretextbox.move(1126, 564)
        self.oretextbox.resize(70, 24)
        self.orelabel.setText("Enter your ore m3/s:")
        self.oretextbox.insertPlainText("22.4")
        self.orelabel.setToolTip(
            "Default value of 22.4 m3/s based on a max skill Covetor using 2x Strip Miner I")

        self.icelabel = QLabel(self)
        self.icetextbox = QPlainTextEdit(self)
        self.icelabel.move(1210, 560)
        self.icetextbox.move(1310, 564)
        self.icetextbox.resize(70, 24)
        self.icelabel.setText("Enter your ice m3/s:")
        self.icetextbox.insertPlainText("29.8")
        self.icelabel.setToolTip(
            "Default value of 29.8 m3/s based on a max skill Covetor using 2x Ice Harvester II")

        self.mercoxitlabel = QLabel(self)
        self.mercoxittextbox = QPlainTextEdit(self)
        self.mercoxitlabel.move(808, 560)
        self.mercoxitlabel.setFixedWidth(130)
        self.mercoxittextbox.move(938, 564)
        self.mercoxittextbox.resize(70, 24)
        self.mercoxitlabel.setText("Enter your mercoxit m3/s:")
        self.mercoxittextbox.insertPlainText("10.4")
        self.mercoxitlabel.setToolTip(
            "Default value of 10.4 m3/s based on a max skill Covetor using 2x Modulated Deep Core Strip Miner II with no charge")

        self.calculate_button = QPushButton("Calculate Value", self)
        self.calculate_button.move(20, 560)
        self.options_button = QPushButton("Options", self)
        self.options_button.move(130, 560)

        self.calculate_button.clicked.connect(self.on_click_calculate)
        self.show()

    @pyqtSlot()
    def on_click_calculate(self):
        global pickleUpdateRequired
        textboxValue = self.textbox.toPlainText()
        textboxValue = StringIO(textboxValue)
        orem3PerSec = float(self.oretextbox.toPlainText())
        icem3PerSec = float(self.icetextbox.toPlainText())
        mercoxitm3PerSec = float(self.mercoxittextbox.toPlainText())
        tableValue = pd.read_csv(textboxValue, sep="\t", lineterminator="\n",
                                 names=["Ore", "Compressed Units", "Volume", "Distance"])
        tableValue = tableValue.drop(columns=['Volume', 'Distance'])
        tableValue["Ore"] = tableValue["Ore"].map(lambda x: "Compressed " + x)
        try:
            tableValue["Compressed Units"] = tableValue["Compressed Units"].map(
                lambda x: x.replace(',', ''))
        except Exception as e:
            print(e)
        tableValue[["Compressed Units"]] = tableValue[["Compressed Units"]].apply(pd.to_numeric)
        tableValue = tableValue.groupby("Ore").agg({"Compressed Units": "sum"})
        for i in ["Unit Volume", "Total Volume", "Unit Value", "ISK/Hr", "Total Value"]:
            tableValue[i] = 0.00
        for i, row in tableValue.iterrows():
            tableValue.at[i, "Compressed Units"] = tableValue.at[i, "Compressed Units"] / ore_data_dict[i]["compression_ratio"]
            tableValue.at[i, "Unit Volume"] = ore_data_dict[i]["compressed_volume"]
            tableValue.at[i, "Total Volume"] = tableValue.at[i, "Compressed Units"] * tableValue.at[i, "Unit Volume"]
            try:
                if (date.today() - ore_data_dict[i]["date"]).days >= 5:
                    print(f"Market data for {i} too old")
                    raise Exception("market data too old")
                unitValue = ore_data_dict[i]["unit_value"]
            except Exception as e:
                print(e)
                print(f"Fetching market data for {i}")
                unitValue, dateObtained = getMarketValue(ore_data_dict[i]["type_id"])
                ore_data_dict[i]["unit_value"] = unitValue
                ore_data_dict[i]["date"] = dateObtained
                pickleUpdateRequired = True
            tableValue.at[i, "Unit Value"] = unitValue
            if ore_data_dict[i]["compression_ratio"] == 1:
                minedCompressedUnits = icem3PerSec / ore_data_dict[i]["volume"] * 3600
            elif "Mercoxit" in i:
                minedCompressedUnits = mercoxitm3PerSec / ore_data_dict[i]["volume"] * 36
            else:
                minedCompressedUnits = orem3PerSec / ore_data_dict[i]["volume"] * 36
            iskPerHour = minedCompressedUnits * unitValue
            tableValue.at[i, "ISK/Hr"] = iskPerHour
            tableValue.at[i, "Total Value"] = tableValue.at[i, "Compressed Units"] * unitValue
        tableValue = tableValue.round({"Unit Volume": 2, "Total Volume": 1, "Unit Value": 2,
                                       "ISK/Hr": 2, "Total Value": 2})
        tableValue = tableValue.sort_values(by=["Total Value"], ascending=False)
        totalValue = format(tableValue["Total Value"].sum(), ",.2f")
        tableValue["ISK/Hr"] = tableValue["ISK/Hr"].apply("{:,.2f}".format)
        tableValue["Unit Value"] = tableValue["Unit Value"].apply("{:,.2f}".format)
        tableValue["Total Value"] = tableValue["Total Value"].apply("{:,.2f}".format)
        tableValue = tableValue.reset_index()
        model = DataFrameModel(tableValue)
        self.table.setModel(model)
        self.totalValueLabel.setText("Total Value: " + totalValue + " ISK")
        self.totalValueLabel.setFixedWidth(500)
        self.header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            self.header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        if pickleUpdateRequired:
            with open("ore_data_dict.pkl", "wb") as f:
                pickle.dump(ore_data_dict, f, pickle.HIGHEST_PROTOCOL)
            pickleUpdateRequired = False


def getMarketValue(typeIdInput):
    request_string = (f"{requestBase}{regionId}{requestBridge}{typeIdInput}")
    result = requests.get(request_string, headers=requestHeaders).json()[-2]
    return result["average"], datetime.strptime(result["date"], "%Y-%m-%d").date()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
