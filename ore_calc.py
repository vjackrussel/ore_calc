from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, QLabel,
                             QPlainTextEdit, QTableView, QHeaderView, QStyledItemDelegate)
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, Qt, QVariant, QModelIndex, pyqtProperty
from PyQt5.QtGui import QIcon
from datetime import date, datetime, timedelta
from pprint import pprint
from io import StringIO
import pandas as pd
import requests
import json
import sys

requestHeaders = {"User-Agent": "Asteroid appraiser by vjackrussel@gmail.com"}
requestBase = "https://esi.evetech.net/latest/markets/"
requestBridge = "/history/?datasource=tranquility&type_id="
theForgeRegionId = 10000002
delveRegionId = 10000060
regionId = theForgeRegionId

try:
    with open("updatedOreData.json", "r") as f:
        baseOreDataDict = json.loads(f.read())
except Exception as e:
    print(e, "No updatedOreData, loading baseOreData")
    with open("baseOreData.json", "r") as f:
        baseOreDataDict = json.loads(f.read())
jsonUpdateRequired = False


class AlignDelegate(QStyledItemDelegate):

    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter


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
        # self.table.setSortingEnabled(True) # Sorting doesn't seem to work yet

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
        global jsonUpdateRequired
        textboxValue = self.textbox.toPlainText()
        textboxValue = StringIO(textboxValue)
        orem3PerSec = float(self.oretextbox.toPlainText())
        icem3PerSec = float(self.icetextbox.toPlainText())
        mercoxitm3PerSec = float(self.mercoxittextbox.toPlainText())
        df = pd.read_csv(textboxValue, sep="\t", lineterminator="\n",
                         names=["Ore / Ice / Goo", "Compressed Units", "Volume", "Distance"])
        df = df.drop(columns=['Volume', 'Distance'])
        try:
            df["Compressed Units"] = df["Compressed Units"].map(
                lambda x: x.replace(',', ''))
        except Exception as e:
            print(e)
        df[["Compressed Units"]] = df[["Compressed Units"]].apply(pd.to_numeric)
        df = df.groupby("Ore / Ice / Goo").agg({"Compressed Units": "sum"})
        for i in ["Unit Volume", "Total Volume", "Unit Value", "ISK/Hr", "Total Value"]:
            df[i] = 0.00
        for i, row in df.iterrows():
            if baseOreDataDict[i]["unit_type"] == "ice":
                minedCompressedUnits = icem3PerSec / baseOreDataDict[i]["volume"] * 3600
            elif baseOreDataDict[i]["unit_type"] == "mercoxit":
                minedCompressedUnits = mercoxitm3PerSec / baseOreDataDict[i]["volume"] * 36
                df.at[i, "Compressed Units"] = df.at[i, "Compressed Units"] / 100
            elif baseOreDataDict[i]["unit_type"] == "moon_goo":
                minedCompressedUnits = orem3PerSec / baseOreDataDict[i]["volume"] * 3600
            else:
                minedCompressedUnits = orem3PerSec / baseOreDataDict[i]["volume"] * 36
                df.at[i, "Compressed Units"] = df.at[i, "Compressed Units"] / 100
            df.at[i, "Unit Volume"] = baseOreDataDict[i]["compressed_volume"]
            df.at[i, "Total Volume"] = df.at[i, "Compressed Units"] * df.at[i, "Unit Volume"]
            try:
                dateObject = datetime.strptime(baseOreDataDict[i]["date"], "%Y-%m-%d").date()
                if (date.today() - dateObject).days >= 5:
                    print(f"Market data for {i} too old")
                    raise Exception("market data too old")
                unitValue = baseOreDataDict[i]["compressed_unit_value"]
            except Exception as e:
                print(e)
                print(f"Fetching market data for {i}")
                unitValue, dateObtained = getMarketValue(baseOreDataDict[i]["compressed_type_id"])
                baseOreDataDict[i]["compressed_unit_value"] = unitValue
                baseOreDataDict[i]["date"] = dateObtained
                jsonUpdateRequired = True
            df.at[i, "Unit Value"] = unitValue
            iskPerHour = minedCompressedUnits * unitValue
            df.at[i, "ISK/Hr"] = iskPerHour
            df.at[i, "Total Value"] = df.at[i, "Compressed Units"] * unitValue
        df = df.round({"Unit Volume": 2, "Total Volume": 1, "Unit Value": 2,
                       "ISK/Hr": 2, "Total Value": 2})
        df = df.sort_values(by=["Total Value"], ascending=False)
        totalValue = format(df["Total Value"].sum(), ",.2f")
        for i in ["Compressed Units", "Unit Volume", "Total Volume",
                  "Unit Value", "ISK/Hr", "Total Value"]:
            if "Units" in i:
                df[i] = df[i].apply("{:,.0f}".format)
            else:
                df[i] = df[i].apply("{:,.2f}".format)
        df = df.reset_index()
        model = DataFrameModel(df)
        self.table.setModel(model)
        self.totalValueLabel.setText("Total Value: " + totalValue + " ISK")
        self.totalValueLabel.setFixedWidth(500)
        self.header = self.table.horizontalHeader()
        self.header.setSectionResizeMode(0, QHeaderView.Stretch)
        delegate = AlignDelegate(self.table)
        for i in range(1, 7):
            self.header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            self.table.setItemDelegateForColumn(i, delegate)
        if jsonUpdateRequired:
            with open("updatedOreData.json", "w") as f:
                json.dump(baseOreDataDict, f)
            jsonUpdateRequired = False


def getMarketValue(typeIdInput):
    request_string = (f"{requestBase}{regionId}{requestBridge}{typeIdInput}")
    result = requests.get(request_string, headers=requestHeaders).json()[-2]
    return result["average"], result["date"]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
