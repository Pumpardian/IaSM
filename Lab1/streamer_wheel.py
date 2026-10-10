import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QListWidget,
    QLineEdit, QDialog, QDialogButtonBox, QFormLayout, QMessageBox,
    QHeaderView
)

from tasks import task_4


class AddGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add game")
        self.setModal(True)
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.rating_edit = QLineEdit()
        self.rating_edit.setPlaceholderText("Amount (for example, 75")

        layout.addRow("Name:", self.name_edit)
        layout.addRow("Amount:", self.rating_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        try:
            rating = int(self.rating_edit.text())
        except ValueError:
            rating = 0
        return self.name_edit.text().strip(), rating


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Streamer wheel")
        self.setGeometry(100, 100, 800, 600)

        self.games = []
        self.history = []

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Amount", "Probability"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add game")
        self.btn_add.clicked.connect(self.add_game)
        self.btn_remove = QPushButton("Delete selected")
        self.btn_remove.clicked.connect(self.remove_game)
        self.btn_clear_all = QPushButton("Clear list")
        self.btn_clear_all.clicked.connect(self.clear_games)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_clear_all)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("Result:"))
        self.result_label = QLabel("—")
        self.result_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: #2a82da;")
        result_layout.addWidget(self.result_label)
        result_layout.addStretch()
        main_layout.addLayout(result_layout)

        self.btn_spin = QPushButton("SPIN")
        self.btn_spin.setStyleSheet("font-size: 16pt; padding: 10px;")
        self.btn_spin.clicked.connect(self.spin_wheel)
        main_layout.addWidget(self.btn_spin)

        main_layout.addWidget(QLabel("Game history:"))
        self.history_list = QListWidget()
        main_layout.addWidget(self.history_list)

        btn_hist_layout = QHBoxLayout()
        self.btn_clear_history = QPushButton("Clear history")
        self.btn_clear_history.clicked.connect(self.clear_history)
        btn_hist_layout.addStretch()
        btn_hist_layout.addWidget(self.btn_clear_history)
        main_layout.addLayout(btn_hist_layout)

        self.default_games()
        self.update_table()

    def default_games(self):
        self.games = [
            ("Witcher 3", 90),
            ("Cyberpunk 2077", 70),
            ("Hades", 85),
            ("Stardew Valley", 75),
            ("Doom Eternal", 80),
        ]

    def update_table(self):
        self.table.setRowCount(len(self.games))
        if not self.games:
            return

        ratings = [r for _, r in self.games]
        total = sum(ratings)
        if total == 0:
            probs = [0] * len(self.games)
        else:
            probs = [r / total for r in ratings]

        for i, (name, rating) in enumerate(self.games):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(str(rating)))
            self.table.setItem(i, 2, QTableWidgetItem(f"{probs[i]*100:.2f}%"))

    def add_game(self):
        dialog = AddGameDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, rating = dialog.get_data()
            if not name:
                QMessageBox.warning(self, "Error", "Name cannot be empty")
                return
            if rating < 0:
                rating = 0

        name_norm = name.strip()
        found = None
        for i, (n, r) in enumerate(self.games):
            if n.lower() == name_norm.lower():
                found = i
                break
        if found is not None:
            new_rating = self.games[found][1] + rating
            self.games[found] = (self.games[found][0], new_rating)
        else:
            self.games.append((name_norm, new_rating))
        self.update_table()

    def remove_game(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Select game to delete")
            return
        self.games.pop(row)
        self.update_table()

    def clear_games(self):
        if not self.games:
            return
        reply = QMessageBox.question(
            self, "Confirmation", "Delete every game?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.games.clear()
            self.update_table()
            self.result_label.setText("—")
            self.history.clear()
            self.history_list.clear()

    def spin_wheel(self):
        if len(self.games) < 2:
            QMessageBox.warning(self, "Warning", "Add at least 2 games")
            return

        ratings = [r for _, r in self.games]
        total = sum(ratings)
        if total == 0:
            QMessageBox.warning(self, "Error", "Amount sum is 0")
            return
        probs = [r / total for r in ratings]

        idx = task_4(probs, 1)[0]

        game_name = self.games[idx][0]
        self.result_label.setText(game_name)

        self.history.append(idx)
        self.history_list.addItem(f"{len(self.history)}. {game_name}")

    def clear_history(self):
        self.history.clear()
        self.history_list.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())