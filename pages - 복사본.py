from sahi import AutoDetectionModel
from runmodel import LearningModel
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Learning Model Manager")

        # LearningModel 객체 생성
        self.learning_model = LearningModel()

        # 서브 클래스에 LearningModel 전달
        self.sub_ui = SubUI(self.learning_model)

        # 버튼 생성
        self.train_button = QPushButton("Start Training")
        self.train_button.clicked.connect(self.start_training)

        # 메인 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.train_button)
        layout.addWidget(self.sub_ui)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_training(self):
        # 학습 시작
        self.learning_model.start_training()


from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton

class SubUI(QWidget):
    def __init__(self, learning_model):
        super().__init__()
        self.learning_model = learning_model  # MainUI에서 전달받은 LearningModel 객체

        # UI 구성
        self.status_label = QLabel("Status: Idle")
        self.train_button = QPushButton("Start Training from SubUI")
        self.train_button.clicked.connect(self.start_training)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.train_button)
        self.setLayout(layout)

        # 학습 이벤트 연결
        self.learning_model.training_started.connect(self.on_training_started)
        self.learning_model.training_finished.connect(self.on_training_finished)
        self.learning_model.training_error.connect(self.on_training_error)

    def start_training(self):
        self.learning_model.start_training()

    def on_training_started(self):
        self.status_label.setText("Status: Training Started")

    def on_training_finished(self, trained_model_path):
        self.status_label.setText(f"Status: Training Completed. Model saved at {trained_model_path}")

    def on_training_error(self, error_message):
        self.status_label.setText(f"Status: Training Error - {error_message}")


from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
