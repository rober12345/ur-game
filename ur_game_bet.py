from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import sys
import os
import random

TILE_SIZE = 40
DICE_MIN = 1
DICE_MAX = 6


# 🔹 NEW: helper that also works inside a PyInstaller .exe
def resource_path(relative):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


class UrGame(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load correct UI file
        loadUi(resource_path("ur_game_bet.ui"), self)

        # -------------------------
        # NAVIGATION BUTTONS
        # -------------------------
        self.startButton.clicked.connect(self.go_betting_page)
        self.rulesButton.clicked.connect(self.show_rules)
        self.rulesBackButton.clicked.connect(self.go_home)
        self.quitButton.clicked.connect(self.close)
        self.playAgainButton.clicked.connect(self.go_betting_page)

        self.rollButton.clicked.connect(self.roll_dice)
        self.moveButton.clicked.connect(self.move_piece)

        # -------------------------
        # BETTING BUTTONS
        # -------------------------
        self.bet_buttons = [
            self.betBtn_1, self.betBtn_5, self.betBtn_10,
            self.betBtn_100, self.betBtn_200, self.betBtn_500,
            self.betBtn_800, self.betBtn_900, self.betBtn_1000
        ]

        for btn in self.bet_buttons:
            btn.clicked.connect(self.handle_bet)

        self.placeBetButton.clicked.connect(self.confirm_bet)

        # -------------------------
        # GAME STATE
        # -------------------------
        self.current_player = 1
        self.positions = {1: 0, 2: 0}
        self.last_roll = 0

        # -------------------------
        # BETTING STATE
        # -------------------------
        self.player_coins = {1: 1000, 2: 1000}
        self.player_bets = {1: 0, 2: 0}
        self.current_bet = 0

        # Horses
        self.horses = {
            1: QPixmap(resource_path("src/assets/horse_white.png")),
            2: QPixmap(resource_path("src/assets/horse_blue.png")),
        }

        # Build tiles
        self.board_tiles = []
        i = 0
        while True:
            tile = getattr(self, f"tile_{i}", None)
            if tile is None:
                break

            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile.setScaledContents(True)
            tile.clear()

            self.board_tiles.append(tile)
            i += 1

        self.board_size = len(self.board_tiles)

        self.update_coin_labels()
        self.update_bet_display()

        # DEFAULT PAGE
        self.statusLabel_2.setText("Welcome! Click START")
        self.stackedWidget.setCurrentWidget(self.StartPage)

    # ------------------------------
    # NAVIGATION
    # ------------------------------
    def go_home(self):
        self.stackedWidget.setCurrentWidget(self.StartPage)

    def show_rules(self):
        self.stackedWidget.setCurrentWidget(self.RulesPage)

    def go_betting_page(self):
        self.current_player = 1
        self.player_bets = {1: 0, 2: 0}
        self.current_bet = 0

        self.update_bet_display()
        self.update_coin_labels()

        self.statusLabel_2.setText("Player 1 — choose your bet")
        self.stackedWidget.setCurrentWidget(self.bettingPage)

    # ------------------------------
    # LABEL UPDATES
    # ------------------------------
    def update_coin_labels(self):
        self.coinsLabelP1.setText(str(self.player_coins[1]))
        self.coinsLabelP2.setText(str(self.player_coins[2]))

    def update_bet_display(self):
        self.betLCD.display(self.current_bet)

        for btn in self.bet_buttons:
            value = int(btn.text())
            btn.setEnabled(self.player_coins[self.current_player] >= value)

    # ------------------------------
    # BETTING LOGIC
    # ------------------------------
    def handle_bet(self):
        value = int(self.sender().text())

        if value > self.player_coins[self.current_player]:
            self.statusLabel_2.setText("Not enough coins")
            return

        self.current_bet = value
        self.betLCD.display(self.current_bet)

        self.statusLabel_2.setText(
            f"Player {self.current_player} selected bet {value}"
        )

    def confirm_bet(self):
        if self.current_bet == 0:
            self.statusLabel_2.setText("Select a bet first")
            return

        self.player_bets[self.current_player] = self.current_bet
        self.statusLabel_2.setText(f"Player {self.current_player} bet locked")

        if self.current_player == 1:
            self.current_player = 2
            self.current_bet = 0
            self.betLCD.display(0)
            self.update_bet_display()
            self.statusLabel_2.setText("Player 2 — choose your bet")
            return

        self.start_race()

    # ------------------------------
    # START GAME
    # ------------------------------
    def start_race(self):
        self.positions = {1: 0, 2: 0}
        self.last_roll = 0
        self.current_player = 1

        self.statusLabel.setText("Race started! Player 1 roll the dice")
        self.diceLabel.setText("Roll the dice")

        self.update_board()
        self.stackedWidget.setCurrentWidget(self.GamePage)

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

        self.current_player = 2 if self.current_player == 1 else 1
        self.statusLabel.setText(f"Player {self.current_player} turn")

    def update_board(self):
        for tile in self.board_tiles:
            tile.clear()

        for player, pos in self.positions.items():
            if 0 <= pos < self.board_size:
                pixmap = self.horses[player].scaled(
                    TILE_SIZE,
                    TILE_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.board_tiles[pos].setPixmap(pixmap)

    def end_game(self, winner):
        loser = 2 if winner == 1 else 1

        win_amount = self.player_bets[winner]
        lose_amount = self.player_bets[loser]

        self.player_coins[winner] += win_amount
        self.player_coins[loser] -= lose_amount

        self.update_coin_labels()

        self.winnerLabel.setText(f"🏆 Player {winner} Wins!")
        self.statusLabel.setText(f"Player {winner} wins the race!")

        if self.player_coins[1] <= 0 or self.player_coins[2] <= 0:
            self.playAgainButton.setText("GAME OVER")
        else:
            self.playAgainButton.setText("NEXT RACE")

        self.stackedWidget.setCurrentWidget(self.ResultPage)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UrGame()
    window.show()
    sys.exit(app.exec())
