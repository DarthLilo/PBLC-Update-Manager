from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from ..Assets import Assets
from ..Game import Game

class GameRunning(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modpack Update")
        self.setWindowIcon(QIcon(Assets.getResource(Assets.ResourceTypes.app_icon)))

        Buttons = (
            QDialogButtonBox.StandardButton.Ok
        )
        self.button_box = QDialogButtonBox(Buttons)
        self.button_box.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        self.message = QLabel(f"{Game.game_id} is running, please close the game first!")
        layout.addWidget(self.message)
        layout.addWidget(self.button_box)