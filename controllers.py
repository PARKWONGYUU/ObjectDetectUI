from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget
from pages import Page1, Page2
from alerts import SimpleAlertPage, AlertPage


class Controller:
    def __init__(self):
        self.pages = {}

    def init_pages(self, stack):
        """페이지 초기화 및 추가"""
        self.pages["page1"] = Page1()
        self.pages["page2"] = Page2()

        stack.addWidget(self.pages["page1"])  # 페이지 1 추가
        stack.addWidget(self.pages["page2"])  # 페이지 2 추가

    def init_navigation(self, stack):
        """네비게이션 버튼 초기화"""
        nav_layout = QVBoxLayout()

        # 페이지 전환 버튼
        page1_button = QPushButton("Go to Page 1")
        page1_button.clicked.connect(lambda: stack.setCurrentIndex(0))
        nav_layout.addWidget(page1_button)

        page2_button = QPushButton("Go to Page 2")
        page2_button.clicked.connect(lambda: stack.setCurrentIndex(1))
        nav_layout.addWidget(page2_button)

        # 팝업 띄우기 버튼
        simple_popup_button = QPushButton("Show Simple Alert")
        simple_popup_button.clicked.connect(self.show_simple_popup)
        nav_layout.addWidget(simple_popup_button)

        alert_popup_button = QPushButton("Show Alert Page")
        alert_popup_button.clicked.connect(self.show_alert_popup)
        nav_layout.addWidget(alert_popup_button)

        # 네비게이션 위젯 생성
        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)
        nav_widget.setFixedWidth(200)
        return nav_widget

    def show_simple_popup(self):
        """SimpleAlertPage 팝업 띄우기"""
        popup = SimpleAlertPage("This is a simple alert!")
        popup.exec()

    def show_alert_popup(self):
        """AlertPage 팝업 띄우기"""
        popup = AlertPage("Are you sure?")
        popup.exec()
