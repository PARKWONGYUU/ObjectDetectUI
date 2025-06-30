import os
import shutil
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QLabel, QPushButton, QListWidget, QFileDialog, QListWidgetItem, QProgressBar, QComboBox
from PySide6.QtGui import QPixmap, QWheelEvent, QImage, QMouseEvent, QPainter, QPen
from PySide6.QtCore import Qt, QTimer, QRect
from alerts import ControllPopup
import cv2
from runmodel import LearningModel
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


pixmap1 = None
pixmap2 = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global pixmap1, pixmap2

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)
        
        self.logo1 = "C:\\Users\\USER\\Desktop\\newprogram\\source\\emCT3.png"
        self.logo2 = "C:\\Users\\USER\\Desktop\\newprogram\\source\\hongik.png"

        pixmap1 = self.load_logo(self.logo1)
        pixmap2 = self.load_logo(self.logo2)

        self.page1 = Page1(self.stack)
        self.page2 = Page2(self.stack)
        self.page3 = Page3(self.stack)
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)

        self.stack.setCurrentWidget(self.page1)

    def handle_page_change(self, index):
        current_page = self.stack.widget(index)
        if current_page == self.page1:
            self.page1.start_timer()
        else:
            self.page1.stop_timer()

    def load_logo(self, logo_path):
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            return pixmap
        else:
            print(f"Error: Unable to load logo from {logo_path}")
            return None
        
class BasePage(QWidget):
    def __init__(self, stack, parent=None):
        super().__init__(parent)
        
        self.learning_model = LearningModel()
        self.controll_popup = ControllPopup()
        self.stack = stack
        self.init_ui()

    def page_change(self, page=1):
        self.stack.setCurrentIndex(page-1)

    def init_ui(self):
        self.background_color = QLabel("", self)
        self.background_color.setGeometry(0, 0, 1280, 840)
        self.background_color.setStyleSheet("background-color: white;")
        self.setFixedSize(1280, 840)
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 상단: 제목
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 중단: 배너, 로고, 버튼
        self.banner_label = QLabel("", self)
        self.banner_label.setGeometry(0, 0, 1280, 100)
        self.banner_label.setStyleSheet("background-color: blue; font-size: 18px; text-align: left;")
        self.banner_label.setAlignment(Qt.AlignCenter)
        
        self.title_label = QLabel("", self)
        self.title_label.setGeometry(220, 0, 1280, 100)  # (x, y, width, height)
        self.title_label.setStyleSheet("background-color: transparent; font-size: 30px; font-weight: bold; color: white; font-family: times new roman;")

        self.logo1_label = QLabel("", self)
        self.logo1_label.setGeometry(10, 0, 150, 100)
        self.logo1_label.setPixmap(pixmap1)  # QLabel에 QPixmap 설정
        self.logo1_label.setScaledContents(False)  # QLabel 크기에 맞게 이미지 조정
        self.logo2_label = QLabel("", self)
        self.logo2_label.setGeometry(100, 0, 150, 100)
        self.logo2_label.setPixmap(pixmap2)  # QLabel에 QPixmap 설정
        self.logo2_label.setScaledContents(True)  # QLabel 크기에 맞게 이미지 조정
    
        self.action_button1 = QPushButton("", self)
        self.action_button1.setGeometry(1040, 30, 200, 50)
        self.action_button1.setStyleSheet("""
                                QPushButton {
                                    background-color: blue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                    border: 2px solid black;
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)

        self.action_button2 = QPushButton("", self)
        self.action_button2.setGeometry(840, 30, 200, 50)
        self.action_button2.setStyleSheet("""
                                QPushButton {
                                    background-color: blue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                    border: 2px solid black;
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)

    def ActionDef(self, bool=False, action1=None, action2=None):
        if bool:
            action1()
        else:
            action2()

class Page1(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_custom_ui()

    def add_custom_ui(self):
#---------------------------------------------------------------------------------------------------------------------------------------------------
        #제목
        self.title_label.setText("  Real-time Monitoring")
#---------------------------------------------------------------------------------------------------------------------------------------------------
        #중단: 버튼 기능 정의 bool값 세팅 필요
        self.action_button1.setText("Check the Learning Process")
        self.action_button1.clicked.connect(lambda: self.ActionDef(
            bool= self.learning_model.on_train, action1=lambda: self.page_change(3), action2=lambda: self.controll_popup.show_popup(
                popup_type="simple", text="There is no ongoing learning currently.",
                callback1=lambda: self.controll_popup.close_popup())))
        
        self.action_button2.setText("Learning New Device")
        self.action_button2.clicked.connect(lambda: self.ActionDef(
            bool= self.learning_model.on_train, action1=lambda: self.controll_popup.show_popup(
                popup_type="simple", text="Learning is currently in progress.",
                callback1=lambda: self.controll_popup.close_popup()),
                action2=lambda: self.page_change(2)))
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 하단: 이미지 영역
        self.image_display = QLabel(self)
        self.image_display.setGeometry(40, 170, 1200, 650)
        self.image_display.setStyleSheet("background-color: lightgray; border: 2px solid black;")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setText("Image Area")  # 이미지 대체 텍스트

        self.real_display = QLabel(self.image_display)
        self.real_display.setGeometry(0, 0, 1200, 650)
        self.real_display.setStyleSheet("background-color: transparent;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_prediction)
        self.start_timer(3000)

    def start_timer(self, sec):
        self.timer.start(sec) #ms

    def stop_timer(self):
        self.timer.stop()

    def process_prediction(self):
        result_path = self.learning_model.predict_capture_image()
        if result_path:
            self.update_real_display(result_path)

    def update_real_display(self, result_path):
        if os.path.exists(result_path):
            pixmap = QPixmap(result_path)
            self.real_display.setPixmap(pixmap)
            self.real_display.setScaledContents(True)
        else:
            self.real_display.setText("No prediction image available.")

    def closeEvent(self, event):
        self.learning_model.release_camera()
        super().closeEvent(event)

class Page2(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_files = []
        self.text_files = []
        self.image_scale = 1.0
        self.labels = []
        self.selected_label = None
        self.current_image_path = None
        self.current_label_path = None
        self.rects = []
        self.class_ids = set()

        self.start_pos_x = None
        self.start_pos_y = None
        self.end_pos_x = None
        self.end_pos_y = None

        self.dragging = False
        self.mouse_ckick_mode = True
        self.add_custom_ui()

    def add_custom_ui(self):
        self.init_slider()
#---------------------------------------------------------------------------------------------------------------------------------------------------
        #제목
        self.title_label.setText("  Learning New Device")        
#---------------------------------------------------------------------------------------------------------------------------------------------------
        #중단: 버튼 기능 정의
        self.action_button1.setText("Check the Learning Process")
        self.action_button1.clicked.connect(lambda: self.ActionDef(
            bool=True, action1=lambda: self.controll_popup.show_popup(
                popup_type="normal", text="Would you like to proceed with training using the added data?",
                callback1=lambda: (self.page_change(3), self.learning_model.start_training(), self.controll_popup.close_popup()),
                callback2=lambda: self.controll_popup.close_popup())))

        self.action_button2.setText("Real-Time Detecting")
        self.action_button2.clicked.connect(lambda: self.ActionDef(
            bool=True, action1=lambda: self.controll_popup.show_popup(
                popup_type="normal", text="The current progress will not be saved.",
                callback1=lambda: (self.page_change(1), self.controll_popup.close_popup(), self.reset_page()),
                callback2=lambda: self.controll_popup.close_popup())))
    
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 하단 좌측: 이미지 출력부
        self.image_display = QLabel(self)
        self.image_display.setGeometry(10, 120, 700, 700)
        self.image_display.setStyleSheet("background-color: lightgray; border: 2px solid black;")
        self.image_display.setAlignment(Qt.AlignCenter)
        #부모 마스킹
        self.real_display = QLabel(self.image_display)
        self.real_display.setGeometry(0, 0, 700, 700)
        self.real_display.setStyleSheet("background-color: transparent;")
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 하단 좌측 버튼
        self.deleted_labels = []

        self.button1 = QPushButton("Delete Label", self)
        self.button1.setGeometry(720, 120, 140, 40)
        self.button1.setStyleSheet("""
                                QPushButton {
                                    background-color: skyblue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)
        self.button1.clicked.connect(lambda: self.delete_selected_label())
    
        self.button2 = QPushButton("return Label", self)
        self.button2.setGeometry(720, 200, 140, 40)
        self.button2.setStyleSheet("""
                                QPushButton {
                                    background-color: skyblue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)
        self.button2.clicked.connect(lambda: self.undo_last_deletion())
    
        self.button3 = QPushButton("Create Label", self)
        self.button3.setGeometry(720, 280, 140, 40)
        self.button3.setStyleSheet("""
                                QPushButton {
                                    background-color: skyblue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)

        self.button3.clicked.connect(self.button3_clicked)
        
        self.class_id_text = QLabel(self)
        self.class_id_text.setGeometry(720, 320, 140, 40)
        self.class_id_text.setText("Class_id")
        self.class_id_text.setAlignment(Qt.AlignCenter)

        self.combo_box = QComboBox(self)
        self.combo_box.setGeometry(720, 360, 140, 40)
#--------------------------------------------------------------------------
        #하단 좌측 버튼 기능 추가
    
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 하단 우측: 이미지 목록 + 라벨 목록
        top_list = QListWidget(self)
        top_list.setGeometry(870, 120, 400, 20)
        top_item = QListWidgetItem("Image File Path")
        top_item.setFlags(Qt.NoItemFlags)
        top_list.addItem(top_item)
        
        self.image_list = QListWidget(self)
        self.image_list.setGeometry(870, 137, 400, 683)
        self.image_list.itemClicked.connect(self.display_image)

        #self.label_list = QListWidget(self)
        #self.label_list.setGeometry(937, 220, 0, 0)
        #self.label_list.itemClicked.connect(lambda: self.draw_yolov5_labels(self.current_image_path, self.current_label_path))
    
        # 팝업 버튼
        self.btn = QPushButton("Load Image", self)
        self.btn.setGeometry(720, 780, 140, 40)  # 버튼 위치 조정
        self.btn.setStyleSheet("""
                                QPushButton {
                                    background-color: skyblue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)
        self.btn.clicked.connect(self.upload_image)

        # 팝업 버튼
        self.btn = QPushButton("Delete Image", self)
        self.btn.setGeometry(720, 700, 140, 40)  # 버튼 위치 조정\
        self.btn.setStyleSheet("""
                                QPushButton {
                                    background-color: skyblue;  /* 버튼 배경색 */
                                    color: white;              /* 글자 색 */
                                    border-radius: 15px;       /* 둥근 모서리 설정 (15px) */
                                    padding: 10px;             /* 내부 여백 */
                                }
                                QPushButton:hover {
                                    background-color: #2980b9; /* 마우스 오버 시 색상 */
                                }
                                """)
        self.btn.clicked.connect(self.delete_selected_item)

#-----------------------------------------------------------------------------------------------------------------------------------------------------
    #기능 구현
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            # 중복 경로 확인
            if any(file[1] == file_path for file in self.image_files):
                print(f"이미 추가된 이미지 경로: {file_path}")
                return
            file_name = os.path.basename(file_path)
            self.image_files.append((file_name, file_path))
            self.current_image_path = file_path
            self.current_label_path = self.learning_model.predict_input_image(file_path)
            self.text_files.append((file_name, self.current_label_path))
            self.update_image_list()
        
            self.class_ids = self.extract_class_ids_from_label(self.current_label_path)

            self.combo_box.clear()
            self.combo_box.addItems('0')
            self.combo_box.addItems('1')
            #self.combo_box.addItems(sorted(self.class_ids))
            
    def extract_class_ids_from_label(self, label_path):
        class_ids = set()
        if os.path.exists(label_path):
            with open(label_path, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) >= 1:  # 최소 class_id가 있는 경우
                        class_ids.add(parts[0])  # class_id를 추가
        return class_ids

    def update_image_list(self):
        self.image_list.clear()
        for _, file_path in self.image_files:
            self.image_list.addItem(file_path)

    def display_image(self, item):
        self.current_image_path = item.text()
        label_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        self.get_labels_for_image(label_name)
        pixmap = self.draw_yolov5_labels(self.current_image_path, self.current_label_path)

        if not pixmap.isNull():
            self.real_display.resize(pixmap.width(), pixmap.height())

            self.real_display.setPixmap(pixmap)
            self.real_display.setScaledContents(False)

            self.update_real_display_position()
        else:
            self.image_display.setText("Unable to load image")



    def get_labels_for_image(self, image_name):
        matching_text_files = [
            file[1] for file in self.text_files if os.path.splitext(file[0])[0] == image_name
        ]
        for text_file_path in matching_text_files:
            with open(text_file_path, "r") as file:
                self.labels.extend(file.readlines())
        self.current_label_path = matching_text_files[0]

    def init_slider(self):
        self.scale_slider = QLabel(self)
        self.scale_slider.setGeometry(710, 820, 100, 20)
        self.scale_slider.raise_()
        self.scale_slider.setStyleSheet(
            "background-color: lightgray; color: black; border-radius: 5px; text-align: center; font-size: 14px; border: 2px solid black;"
        )
        self.scale_slider.setAlignment(Qt.AlignCenter)
        self.scale_slider.hide()

        self.slider_timer = QTimer(self)
        self.slider_timer.setInterval(2000)
        self.slider_timer.timeout.connect(self.hide_slider)

#---------------------------------------------------------------------------------------------------------------------------------------------
    #좌측 하단 버튼 함수
    def delete_selected_label(self):
        """선택된 라벨을 삭제"""
        if self.selected_label != None:
            # 삭제된 라벨 데이터를 기록
            deleted_label = self.labels[self.selected_label].strip()
            self.deleted_labels.append(deleted_label)
            print(f"Deleted label: {deleted_label}")

            # label_list에서 해당 라벨 삭제
            #self.label_list.takeItem(selected_row)

            # 텍스트 파일에서 삭제된 라벨 제거
            for file in self.text_files:
                with open(file[1], "r") as f:
                    lines = f.readlines()

                # 해당 라벨 제거 후 다시 저장
                updated_lines = [line for line in lines if line.strip() != deleted_label]
                with open(file[1], "w") as f:
                    f.writelines([line if line.endswith("\n") else line + "\n" for line in updated_lines])  # 개행 처리

            # 라벨 삭제 후 선택 상태 초기화
            self.selected_label = None

            # 이미지에 다시 라벨을 그림
            self.redraw_labels()


    def undo_last_deletion(self):
        """삭제된 마지막 라벨을 되돌림"""
        if self.deleted_labels:
            # 삭제된 마지막 라벨 가져오기
            last_deleted_label = self.deleted_labels.pop()
            print(f"Restoring label: {last_deleted_label}")

            # label_list에 라벨 복원
            self.labels.append(last_deleted_label)

            # 복원된 라벨을 텍스트 파일에 다시 추가
            for file in self.text_files:
                with open(file[1], "a") as f:
                    if not last_deleted_label.endswith("\n"):
                        last_deleted_label += "\n"  # 개행 보장
                    f.write(last_deleted_label)

            # 이미지에 다시 라벨을 그림
            self.redraw_labels()
        else:
            print("No labels to restore!")

    def redraw_labels(self):
        """이미지 위의 라벨을 다시 그림"""
        if self.current_image_path and self.current_label_path:
            # 이미지와 라벨 데이터를 사용해 새로 그림
            updated_pixmap = self.draw_yolov5_labels(self.current_image_path, self.current_label_path)
            if not updated_pixmap.isNull():
                self.real_display.setPixmap(updated_pixmap)
                self.real_display.setScaledContents(True)
                print("Redrew labels on the image.")
            else:
                print("Failed to redraw labels.")



#---------------------------------------------------------------------------------------------------------------------------------------------
    #마우스 이벤트
    def mousePressEvent(self, event):
        click_x = event.pos().x() - self.image_display.geometry().x()
        click_y = event.pos().y() - self.image_display.geometry().y()
        # 클릭 좌표가 image_display 범위 안에 있는지 확인
        if 0 <= click_x <= self.image_display.width() and 0 <= click_y <= self.image_display.height():
            if self.real_display.pixmap():
                # 원본 이미지 크기
                pixmap_width = self.real_display.pixmap().width()
                pixmap_height = self.real_display.pixmap().height()
                # real_display의 크기와 위치 계산 (image_display 기준)
                display_width = self.image_display.width()
                display_height = self.image_display.height()
                real_x_offset = (display_width - pixmap_width) / 2
                real_y_offset = (display_height - pixmap_height) / 2
                # 클릭 좌표를 real_display 내부 좌표로 변환
                relative_x = click_x - real_x_offset
                relative_y = click_y - real_y_offset    
                
            if self.mouse_ckick_mode:
                self.selected_label = None
                # 클릭 좌표가 real_display 범위 안에 있는지 확인
                if 0 <= relative_x <= pixmap_width and 0 <= relative_y <= pixmap_height:
                    # 클릭 좌표를 원본 이미지 좌표로 변환
                    image_x = int(relative_x / self.image_scale)
                    image_y = int(relative_y / self.image_scale)
                    print(image_x, image_y)
                    # 클릭한 좌표가 라벨 영역에 포함되는지 확인
                    self.selected_label = None
                    for i in range(len(self.labels)):
                        # YOLOv5 라벨 데이터 가져오기
                        line = self.labels[i].strip()
                        parts = line.split()
                        if len(parts) == 5:
                            class_id, center_x, center_y, width, height = map(float, parts)
                            # YOLO 좌표를 픽셀 좌표로 변환 (원본 이미지 기준)
                            x1 = int((center_x - width / 2) * pixmap_width /self.image_scale)
                            y1 = int((center_y - height / 2) * pixmap_height /self.image_scale)
                            x2 = int((center_x + width / 2) * pixmap_width /self.image_scale)
                            y2 = int((center_y + height / 2) * pixmap_height /self.image_scale)
                            # 클릭 좌표가 라벨 영역에 포함되는지 확인
                            if x1 <= image_x <= x2 and y1 <= image_y <= y2:
                                # label_list에서 해당 라벨 선택
                                self.selected_label = i
                                break
                    self.update_image_and_labels()
            else:
                self.dragging = True
                self.start_pos_x = int(relative_x / self.image_scale)
                self.start_pos_y = int(relative_y / self.image_scale)
                self.end_pos_x = None
                self.end_pos_y = None
                return

    def mouseMoveEvent(self, event: QMouseEvent):
       if self.dragging:
           click_x = event.pos().x() - self.image_display.geometry().x()
           click_y = event.pos().y() - self.image_display.geometry().y()
           # 클릭 좌표가 image_display 범위 안에 있는지 확인
           if 0 <= click_x <= self.image_display.width() and 0 <= click_y <= self.image_display.height():
               if self.real_display.pixmap():
                    # 원본 이미지 크기
                    pixmap_width = self.real_display.pixmap().width()
                    pixmap_height = self.real_display.pixmap().height()
                    # real_display의 크기와 위치 계산 (image_display 기준)
                    display_width = self.image_display.width()
                    display_height = self.image_display.height()
                    real_x_offset = (display_width - pixmap_width) / 2
                    real_y_offset = (display_height - pixmap_height) / 2
                    # 클릭 좌표를 real_display 내부 좌표로 변환
                    relative_x = click_x - real_x_offset
                    relative_y = click_y - real_y_offset
                    self.end_pos_x = int(relative_x / self.image_scale)
                    self.end_pos_y = int(relative_y / self.image_scale)
           self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging:
            self.dragging = False
            if self.start_pos_x and self.end_pos_x:
                # 드래그 영역 계산
                x1 = min(self.start_pos_x, self.end_pos_x)
                y1 = min(self.start_pos_y, self.end_pos_y)
                x2 = max(self.start_pos_x, self.end_pos_x)
                y2 = max(self.start_pos_y, self.end_pos_y)
                rect = QRect(x1, y1, x2 - x1, y2 - y1)
                self.rects.append(rect)

                # 라벨 데이터 생성
                img_width = self.real_display.pixmap().width()
                img_height = self.real_display.pixmap().height()
                class_id = int(self.combo_box.currentText())
                x_center = ((x1 + x2) / 2) / img_width * self.image_scale
                y_center = ((y1 + y2) / 2) / img_height * self.image_scale
                width = (x2 - x1) / img_width * self.image_scale
                height = (y2 - y1) / img_height * self.image_scale

                label = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                self.labels.append(label)

                # 라벨 파일에 기록
                self.save_label(label)
                self.update_image_and_labels()

            self.start_pos = None
            self.end_pos = None
            self.update()

    def paintEvent(self, event):
        if not self.dragging:
            return
        
        painter = QPainter(self)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        # 드래그 중인 영역 표시
        if self.start_pos_x and self.end_pos_x:
            x1 = min(self.start_pos_x, self.end_pos_x)
            y1 = min(self.start_pos_y, self.end_pos_y)
            x2 = max(self.start_pos_x, self.end_pos_x)
            y2 = max(self.start_pos_y, self.end_pos_y)
            painter.drawRect(QRect(x1, y1, x2 - x1, y2 - y1))

        self.update_image_and_labels()
    
    def wheelEvent(self, event):
        if not self.mouse_ckick_mode:
            return
        
        if self.current_image_path:
            delta = event.angleDelta().y()
            if delta > 0:
                self.image_scale += 0.05
            elif delta < 0 and self.image_scale > 0.1:
                self.image_scale -= 0.05

            # 이미지 크기 및 해상도 업데이트
            self.update_image_and_labels()
            self.update_slider()

    def button3_clicked(self):
        if self.current_image_path == None:
            return
        
        if self.mouse_ckick_mode:
            self.disable_mouse_event()
        else:
            self.enable_mouse_event()
        print(self.mouse_ckick_mode)

    def disable_mouse_event(self):
        self.mouse_ckick_mode = False

    def enable_mouse_event(self):
        self.mouse_ckick_mode = True
#---------------------------------------------------------------------------------------------------------------------------------------------
    def save_label(self, label):
        with open(self.current_label_path, "a") as file:
            file.write(label)


    def update_image_and_labels(self):
        if not self.current_image_path:
            return
        # 원본 이미지를 로드하여 QPixmap 생성
        original_pixmap = QPixmap(self.current_image_path)
    
        # 이미지의 새로운 크기 계산
        new_width = int(original_pixmap.width() * self.image_scale)
        new_height = int(original_pixmap.height() * self.image_scale)
    
        # QPixmap을 새로운 크기로 스케일링
        resized_pixmap = original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
    
        # QLabel에 확대된 이미지 설정
        self.real_display.setPixmap(resized_pixmap)
        self.real_display.resize(resized_pixmap.size())
    
        # 라벨을 다시 그려서 확대된 이미지 위에 추가
        if self.current_label_path:
            labeled_pixmap = self.draw_yolov5_labels(self.current_image_path, self.current_label_path)
            if not labeled_pixmap.isNull():
                self.real_display.setPixmap(labeled_pixmap.scaled(
                    new_width, new_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
    
        # QLabel의 위치를 중앙으로 조정
        self.update_real_display_position()
     

    def update_image_with_resolution(self):
        if not self.current_image_path:
            return

        original_pixmap = QPixmap(self.current_image_path)

        new_width = int(original_pixmap.width() * self.image_scale)
        new_height = int(original_pixmap.height() * self.image_scale)

        resized_pixmap = original_pixmap.scaled(
            new_width, new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.real_display.setPixmap(resized_pixmap)
        self.real_display.resize(resized_pixmap.size())

        self.update_real_display_position()

    def update_real_display_position(self):
        if not self.current_image_path:
            return

        real_pixmap = self.real_display.pixmap()
        if not real_pixmap:
            return

        pixmap_width = real_pixmap.width()
        pixmap_height = real_pixmap.height()

        display_width = self.image_display.width()
        display_height = self.image_display.height()

        x_offset = (display_width - pixmap_width) / 2
        y_offset = (display_height - pixmap_height) / 2

        self.real_display.move(int(x_offset), int(y_offset))


    def update_slider(self):
        self.scale_slider.setText(f"Scale: {self.image_scale:.2f}")
        self.scale_slider.raise_()
        self.scale_slider.show()
        self.slider_timer.start()

    def hide_slider(self):
        self.scale_slider.hide()

    def delete_selected_item(self):
        """좌측 목록에서 선택한 이미지와 해당 라벨을 삭제"""
        # 선택된 아이템 가져오기
        selected_item = self.image_list.currentItem()

        if selected_item:
            # 선택된 이미지 경로
            selected_image_path = selected_item.text()

            # 이미지 파일 목록에서 제거
            self.image_files = [
                file for file in self.image_files if file[1] != selected_image_path
            ]

            # 텍스트 파일 목록에서 해당 라벨 제거
            selected_image_name = os.path.splitext(os.path.basename(selected_image_path))[0]
            self.text_files = [
                file for file in self.text_files if os.path.splitext(file[0])[0] != selected_image_name
            ]

            # 목록에서 아이템 제거
            self.image_list.takeItem(self.image_list.row(selected_item))
            self.selected_label = None

            # 이미지 영역 초기화
            self.real_display.clear()
            self.real_display.setGeometry(0, 0, 700, 700)
            self.real_display.setStyleSheet("background-color: transparent;")  # 초기 상태로 설정
            self.current_image_path = None
            self.image_scale = 1.0
            self.hide_slider()

    def reset_page(self):
        # 내부 데이터 초기화
        self.image_files = []  # 이미지 파일 리스트 초기화
        self.text_files = []   # 텍스트 파일 리스트 초기화
        self.current_image_path = None  # 현재 이미지 경로 초기화
        self.image_scale = 1.0  # 이미지 스케일 초기화
        self.learning_model.clear_output_files()

        # UI 컴포넌트 초기화
        self.image_list.clear()  # 왼쪽 목록 초기화
        self.selected_label = None
        self.real_display.clear()  # 이미지 출력 초기화
        self.real_display.setStyleSheet("background-color: transparent;")  # 배경 투명
        self.real_display.resize(700, 700)  # 초기 크기로 복원
        self.real_display.move(0, 0)  # 초기 위치로 복원

    def draw_yolov5_labels(self, image_path, label_path):
        """YOLOv5 라벨을 이미지 위에 그립니다."""
        # 이미지 로드
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Unable to load image from {image_path}")
            return QPixmap()

        # 이미지 크기 가져오기
        img_height, img_width, _ = image.shape

        # 선택된 라벨 가져오기
        selected_label = None
        if self.selected_label != None:
            selected_label = self.labels[self.selected_label].strip()
        # 라벨 정보를 저장할 리스트 초기화
        self.label_boxes = []  # 라벨 영역 저장

        # 라벨 파일 읽기 및 시각화
        try:
            with open(label_path, "r") as file:
                lines = file.readlines()

            for line in lines:
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id, x_center, y_center, width, height = map(float, parts)

                    # YOLO 좌표를 픽셀 좌표로 변환
                    x1 = int((x_center - width / 2) * img_width)
                    y1 = int((y_center - height / 2) * img_height)
                    x2 = int((x_center + width / 2) * img_width)
                    y2 = int((y_center + height / 2) * img_height)

                    # 클래스 이름 가져오기
                    class_name = self.learning_model.get_labels(int(class_id))

                    # 선택된 라벨인지 확인
                    current_label = f"{int(class_id)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                    if current_label == selected_label:
                        box_color = (0, 255, 255)  # 노란색
                        cv2.putText(image, class_name, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.4, color=box_color, thickness=1)
                    else:
                        box_color = (0, 0, 255) if class_name.lower() == "ledon" else (0, 255, 0)

                    # 라벨 영역 저장
                    self.label_boxes.append({"class_id": class_id, "name": class_name, "bbox": (x1, y1, x2, y2)})

                    # 사각형 그리기
                    cv2.rectangle(image, (x1, y1), (x2, y2), color=box_color, thickness=2)

                    # 클래스 이름 텍스트 추가
                    #cv2.putText(image, class_name, (x1, y1 - 10),
                    #            cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=box_color, thickness=1)

        except FileNotFoundError:
            print(f"Error: Label file not found at {label_path}")
            return QPixmap()

        # OpenCV 이미지를 QPixmap으로 변환
        height, width, channel = image.shape
        bytes_per_line = channel * width
        qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(qimage)

        # 이미지 스케일 반영
        scaled_pixmap = pixmap.scaled(
            int(pixmap.width() * self.image_scale),
            int(pixmap.height() * self.image_scale),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        return scaled_pixmap





class Page3(BasePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_custom_ui()

    def add_custom_ui(self):
#---------------------------------------------------------------------------------------------------------------------------------------------------
        #상단: 버튼 기능 정의
        self.title_label.setText("  Learning Process")
        self.action_button1.setText("Back to Real-Time Detecting")
        self.action_button1.clicked.connect(lambda: self.ActionDef(
            bool= True, action1=lambda: self.page_change(1)))
        
        self.action_button2.setText("Stop Learning")
        self.action_button2.clicked.connect(lambda: self.ActionDef(
            bool= True, action1=lambda: self.controll_popup.show_popup(
                popup_type="normal", text="Would you like to stop learning and revert to the previous state?",
                callback1=lambda: (self.page_change(1), self.controll_popup.close_popup(), self.learning_model.stop_training()), #학습 중단도 여기에 연결
                callback2=lambda: self.controll_popup.close_popup())))
        
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 중단
        self.msg_label = QLabel(self)
        self.msg_label.setText("Learning Process..")
        self.msg_label.setGeometry(0, 120, 1280, 30)  # 텍스트가 중단 바로 아래 배치
        self.msg_label.setStyleSheet("background-color: white; font-size: 24px; font-weight: bold; text-align: center; font-family: times new roman;")
        self.msg_label.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(40, 165, 1200, 40)
        self.progress_bar.setStyleSheet("""
                                            QProgressBar {
                                                border: 2px solid grey;
                                                border-radius: 5px;
                                                text-align: center;
                                                height: 40px;
                                            }

                                            QProgressBar::chunk {
                                                background-color: blue;  /* 채워지는 부분의 색상 */
                                                width: 10px;  /* 채워지는 속도 */
                                            }
                                        """)
        self.progress_bar.setMaximum(100)
        self.learning_model.set_epoch_progress_callback(self.update_progress)
#----------------------------------------------------------------------------------------------------------------------------------------------------
        # 하단: 이미지 영역
        self.image_display = QLabel(self)
        self.image_display.setGeometry(40, 220, 1200, 600)
        self.image_display.setStyleSheet("background-color: lightgray; border: 2px solid black;")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setText("Graph")  # 이미지 대체 텍스트

        self.real_display = QLabel(self.image_display)
        self.real_display.setGeometry(0, 0, 1200, 600)
        self.real_display.setStyleSheet("background-color: transparent;")

    def display_graph(self):
        graph_path = "C:/Users/USER/Desktop/newprogram/learning/trained_model/results.png"

        if os.path.exists(graph_path):
            pixmap = QPixmap(graph_path)
            self.real_display.setPixmap(pixmap)
            self.real_display.setScaledContents(True)
           
    def update_progress(self, current_epoch, total_epochs):
        progress = int((current_epoch / total_epochs) * 100)
        self.msg_label.setText(f"Learning Process.. {current_epoch}/{total_epochs}")
        self.progress_bar.setValue(progress)
        self.plot_with_reference_layout()
        self.display_graph()

    def plot_with_reference_layout(self):
        # Load the CSV file
        data_path = "C:/Users/USER/Desktop/newprogram/learning/trained_model/results.csv"
        if not os.path.exists(data_path):
            return
        
        data = pd.read_csv(data_path)
        data.columns = data.columns.str.strip()  # Clean up column names

        # Define the columns to plot and their titles
        columns_to_plot = [
            ('train/box_loss', 'Train Box Loss'),
            ('train/obj_loss', 'Train Obj Loss'),
            ('train/cls_loss', 'Train Class Loss'),
            ('metrics/precision', 'Precision'),
            ('metrics/recall', 'Recall'),
            ('val/box_loss', 'Validation Box Loss'),
            ('val/obj_loss', 'Validation Obj Loss'),
            ('val/cls_loss', 'Validation Class Loss'),
            ('metrics/mAP_0.5', 'mAP 0.5'),
            ('metrics/mAP_0.5:0.95', 'mAP 0.5:0.95')
        ]

        # Create a figure with a grid layout for 2 rows and 5 columns
        fig = plt.figure(figsize=(15, 8))
        spec = gridspec.GridSpec(2, 5, figure=fig, wspace=0.4, hspace=0.4)

        for i, (column, title) in enumerate(columns_to_plot):
            if column in data:
                ax = fig.add_subplot(spec[i // 5, i % 5])  # 2 rows, 5 columns layout
                ax.plot(data['epoch'], data[column], label='Results', marker='o')
                ax.set_title(title, fontsize=10)
                ax.set_xlabel('Epoch', fontsize=8)
                ax.set_ylabel(column, fontsize=8)
                ax.grid(True)
                ax.legend(fontsize=8)

        # Save the figure
        plt.tight_layout()
        plt.savefig("C:/Users/USER/Desktop/newprogram/learning/trained_model/results.png")
        plt.close()

    def clear_directory(directory_path):
        """
        Deletes all files and subfolders in the specified directory.

        Args:
            directory_path (str): The path of the directory to clear.

        Returns:
            None
        """
        if not os.path.exists(directory_path):
            print(f"The directory {directory_path} does not exist.")
            return

        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # Delete file or symbolic link
                    print(f"Deleted file: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Delete folder and its contents
                    print(f"Deleted folder: {item_path}")
            print(f"All contents of {directory_path} have been cleared.")
        except Exception as e:
            print(f"An error occurred while clearing the directory: {e}")