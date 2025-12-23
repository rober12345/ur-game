from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import sys
import os
import random

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------
TILE_SIZE = 40
DICE_MIN = 1
DICE_MAX = 6

# --------------------------------------------------
# PATH HANDLING
# --------------------------------------------------
def resource_path(relative):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)

# --------------------------------------------------
# MAIN GAME CLASS
# --------------------------------------------------
class UrGame(QMainWindow):
    def __init__(self):
        super().__init__()

        # LOAD UI
        loadUi(resource_path("ur_game.ui"), self)

        # SIGNALS
        self.startButton.clicked.connect(self.start_game)
        self.rulesButton.clicked.connect(self.show_rules)
        self.rulesBackButton.clicked.connect(self.go_home)
        self.rollButton.clicked.connect(self.roll_dice)
        self.moveButton.clicked.connect(self.move_piece)
        self.quitButton.clicked.connect(self.close)
        self.playAgainButton.clicked.connect(self.go_home)

        # GAME STATE
        self.current_player = 1
        self.positions = {1: 0, 2: 0}
        self.last_roll = 0

        # LOAD HORSE IMAGES
        self.horses = {
            1: QPixmap(resource_path("src/assets/horse_white.png")),
            2: QPixmap(resource_path("src/assets/horse_blue.png")),
        }

        # BOARD TILES (QLabel)
        self.board_tiles = []
        index = 0
        while True:
            tile = getattr(self, f"tile_{index}", None)
            if tile is None:
                break

            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile.setScaledContents(True)
            tile.clear()

            tile.setStyleSheet("""
                QLabel {
                    background-color: #2c2c2c;
                    border: 2px solid #777;
                }
            """)

            self.board_tiles.append(tile)
            index += 1

        self.board_size = len(self.board_tiles)
        if self.board_size == 0:
            raise RuntimeError("No board tiles found (tile_0, tile_1...)")

        self.update_board()
        self.stackedWidget.setCurrentWidget(self.StartPage)

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------
    def start_game(self):
        self.positions = {1: 0, 2: 0}
        self.current_player = 1
        self.last_roll = 0
        self.statusLabel.setText("Player 1 turn")
        self.diceLabel.setText("Roll the dice")
        self.update_board()
        self.stackedWidget.setCurrentWidget(self.GamePage)

    def show_rules(self):
        self.stackedWidget.setCurrentWidget(self.RulesPage)

    def go_home(self):
        self.stackedWidget.setCurrentWidget(self.StartPage)

    # --------------------------------------------------
    # GAME LOGIC — REAL DICE (1–6)
    # --------------------------------------------------
    def roll_dice(self):
        self.last_roll = random.randint(DICE_MIN, DICE_MAX)
        self.diceLabel.setText(f"🎲 Dice Roll: {self.last_roll}")
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

    # --------------------------------------------------
    # BOARD RENDER — IMAGES ONLY
    # --------------------------------------------------
    def update_board(self):
        for tile in self.board_tiles:
            tile.clear()

        for player, pos in self.positions.items():
            if 0 <= pos < self.board_size:
                pixmap = self.horses[player].scaled(
                    TILE_SIZE,
                    TILE_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.board_tiles[pos].setPixmap(pixmap)

    # --------------------------------------------------
    # END GAME — IMAGE + TEXT
    # --------------------------------------------------
    def end_game(self, winner):
        horse_image = (
            "src/assets/horse_white.png"
            if winner == 1
            else "src/assets/horse_blue.png"
        )

        img_path = resource_path(horse_image).replace("\\", "/")

        html = f"""
        <div style="
            display:flex;
            align-items:center;
            justify-content:center;
            gap:16px;
            font-size:24px;
            font-weight:bold;
        ">
            <img src="{img_path}" width="70" height="70">
            <span>🏆 Player {winner} Wins!</span>
        </div>
        """

        self.winnerLabel.setTextFormat(Qt.TextFormat.RichText)
        self.winnerLabel.setText(html)
        self.winnerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stackedWidget.setCurrentWidget(self.ResultPage)

# --------------------------------------------------
# RUN APP
# --------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UrGame()
    window.show()
    sys.exit(app.exec())
