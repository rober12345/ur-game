from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
import sys
import os
import random


def resource_path(relative):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


class UrGame(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi(resource_path("ur_game.ui"), self)

        # ===== SIGNALS =====
        self.startButton.clicked.connect(self.start_game)
        self.rulesButton.clicked.connect(self.show_rules)
        self.rulesBackButton.clicked.connect(self.go_home)
        self.rollButton.clicked.connect(self.roll_dice)
        self.moveButton.clicked.connect(self.move_piece)
        self.quitButton.clicked.connect(self.close)
        self.playAgainButton.clicked.connect(self.go_home)

        # ===== GAME STATE =====
        self.current_player = 1
        self.positions = {1: 0, 2: 0}
        self.last_roll = 0

        # ===== BOARD TILES =====
        self.board_tiles = []
        i = 0
        while True:
            tile = getattr(self, f"tile_{i}", None)
            if tile is None:
                break

            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 🔴 FORCE VISIBILITY
            tile.setFixedSize(60, 60)
            tile.setStyleSheet("""
                QLabel {
                    background-color: #2c2c2c;
                    border: 2px solid #777;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)

            self.board_tiles.append(tile)
            i += 1

        self.board_size = len(self.board_tiles)
        if self.board_size == 0:
            raise RuntimeError("No board tiles found. Check tile_0 naming.")

        self.update_board()
        self.stackedWidget.setCurrentWidget(self.StartPage)

    # ===== NAVIGATION =====
    def start_game(self):
        self.positions = {1: 0, 2: 0}
        self.current_player = 1
        self.statusLabel.setText("Player 1 turn")
        self.diceLabel.setText("Roll the dice")
        self.update_board()
        self.stackedWidget.setCurrentWidget(self.GamePage)

    def show_rules(self):
        self.stackedWidget.setCurrentWidget(self.RulesPage)

    def go_home(self):
        self.stackedWidget.setCurrentWidget(self.StartPage)

    # ===== GAME LOGIC =====
    def roll_dice(self):
        self.last_roll = sum(random.choice([0, 1]) for _ in range(4))
        self.diceLabel.setText(f"Dice Roll: {self.last_roll}")

        if self.last_roll == 0:
            self.switch_player()
        else:
            self.statusLabel.setText(
                f"Player {self.current_player} rolled {self.last_roll}"
            )

    def move_piece(self):
        if self.last_roll == 0:
            return

        new_pos = self.positions[self.current_player] + self.last_roll

        if new_pos >= self.board_size:
            self.end_game(self.current_player)
            return

        self.positions[self.current_player] = new_pos
        self.last_roll = 0
        self.update_board()
        self.switch_player()

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.statusLabel.setText(f"Player {self.current_player} turn")

    def update_board(self):
        for tile in self.board_tiles:
            tile.setText("")

        for player, pos in self.positions.items():
            if 0 <= pos < self.board_size:
                current = self.board_tiles[pos].text()
                self.board_tiles[pos].setText(current + f"P{player}")

    def end_game(self, winner):
        self.winnerLabel.setText(f"🏆 Player {winner} Wins!")
        self.stackedWidget.setCurrentWidget(self.ResultPage)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UrGame()
    window.show()
    sys.exit(app.exec())