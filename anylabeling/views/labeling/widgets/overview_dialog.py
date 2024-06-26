import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QTableWidget,
    QProgressDialog,
    QTableWidgetItem,
)


class OverviewDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent,
        label_file_list,
        available_shapes,
    ):
        super().__init__(parent)
        self.parent = parent
        self.label_file_list = label_file_list
        self.available_shapes = available_shapes

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.tr("Overview"))
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        layout = QVBoxLayout(self)
        table = QTableWidget(self)

        label_infos = self.load_label_infos()
        total_infos = self.calculate_total_infos(label_infos)
        self.populate_table(table, total_infos)

        layout.addWidget(table)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents
        )
        layout.addWidget(table)
        self.exec_()

    def load_label_infos(self):
        label_infos = {}
        initial_nums = [0 for _ in range(len(self.available_shapes))]

        progress_dialog = QProgressDialog(
            self.tr("Loading..."),
            self.tr("Cancel"),
            0,
            len(self.label_file_list),
        )
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Progress")
        progress_dialog.setStyleSheet("""
        QProgressDialog QProgressBar {
            border: 1px solid grey;
            border-radius: 5px;
            text-align: center;
        }
        QProgressDialog QProgressBar::chunk {
            background-color: orange;
        }
        """)

        for i, label_file in enumerate(self.label_file_list):
            with open(label_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            shapes = data.get("shapes", [])
            for shape in shapes:
                label = shape.get("label", "_empty")
                if label not in label_infos:
                    label_infos[label] = dict(
                        zip(self.available_shapes, initial_nums)
                    )
                shape_type = shape.get("shape_type", "")
                label_infos[label][shape_type] += 1
            progress_dialog.setValue(i)
            if progress_dialog.wasCanceled():
                break

        progress_dialog.close()
        return label_infos

    def calculate_total_infos(self, label_infos):
        total_infos = [["Label"] + self.available_shapes + ["Total"]]
        shape_counter = [0 for _ in range(len(self.available_shapes) + 1)]

        for label, infos in label_infos.items():
            counter = [
                infos[shape_type] for shape_type in self.available_shapes
            ]
            counter.append(sum(counter))
            row = [label] + counter
            total_infos.append(row)
            shape_counter = [x + y for x, y in zip(counter, shape_counter)]

        total_infos.append(["Total"] + shape_counter)
        return total_infos

    def populate_table(self, table, total_infos):
        rows = len(total_infos) - 1
        cols = len(total_infos[0])
        table.setRowCount(rows)
        table.setColumnCount(cols)
        table.setHorizontalHeaderLabels(total_infos[0])

        data = [list(map(str, info)) for info in total_infos[1:]]

        for row, info in enumerate(data):
            for col, value in enumerate(info):
                item = QTableWidgetItem(value)
                table.setItem(row, col, item)
