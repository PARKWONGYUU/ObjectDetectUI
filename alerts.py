from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QDialog

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

from PySide6.QtCore import Qt


class SimpleAlertPage(QDialog):
    def __init__(self, message="This is an alert.", parent=None):
        super().__init__(parent)
        self.message = message  # 표시할 메시지
        self.init_ui()

    def init_ui(self):
        # 메시지 라벨
        self.label = QLabel(self.message, self)
        self.label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            text-align: center;
        """)
        self.label.setAlignment(Qt.AlignCenter)

        # 확인 버튼
        self.ok_button = QPushButton("OK", self)
        self.ok_button.setStyleSheet("""
            padding: 10px 20px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addStretch()  # 위쪽 여백 추가
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addStretch()  # 라벨 아래 여백
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)
        layout.addStretch()  # 버튼 아래 여백

        self.setLayout(layout)
        self.setFixedSize(400, 200)
        self.setWindowTitle("Notice")


class AlertPage(QDialog):
    def __init__(self, message="Are you sure?", parent=None):
        super().__init__(parent)
        self.message = message  # 표시할 메시지
        self.init_ui()

    def init_ui(self):
        # 메시지 라벨
        self.label = QLabel(self.message, self)
        self.label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            text-align: center;
        """)
        self.label.setAlignment(Qt.AlignCenter)

        # Yes 버튼
        self.yes_button = QPushButton("Yes", self)
        self.yes_button.setStyleSheet("""
            padding: 10px 20px;
            font-size: 14px;
            background-color: gray;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)

        # No 버튼
        self.no_button = QPushButton("No", self)
        self.no_button.setStyleSheet("""
            padding: 10px 20px;
            font-size: 14px;
            background-color: gray;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.yes_button)
        button_layout.addSpacing(20)  # 버튼 간격
        button_layout.addWidget(self.no_button)
        button_layout.addStretch()

        # 전체 레이아웃 설정
        layout = QVBoxLayout()
        layout.addStretch()  # 위쪽 여백
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addStretch()  # 라벨 아래 여백
        layout.addLayout(button_layout)
        layout.addStretch()  # 버튼 아래 여백

        self.setLayout(layout)
        self.setFixedSize(400, 250)
        self.setWindowTitle("Notice")



class ControllPopup():
    def __init__(self):
        self.popup = None

    def show_popup(self, popup_type="normal", text = None, callback1=None, callback2=None):
        if popup_type == "simple":
            self.popup = SimpleAlertPage(text)
            self.popup.ok_button.clicked.connect(callback1)
            self.popup.exec()
        elif popup_type == "normal":
            self.popup = AlertPage(text)
            if callback1:
                self.popup.yes_button.clicked.connect(callback1)
            if callback2:
                self.popup.no_button.clicked.connect(callback2)
            self.popup.exec()
        else:
            raise ValueError(f"Invalid popup_type: {popup_type}")
        
    def close_popup(self):
        if self.popup:
            self.popup.close()
            self.popup = None
    