from sahi.utils.yolov5 import (
    download_yolov5s6_model,
)
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
import cv2
import warnings
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
import os
import sys

warnings.filterwarnings("ignore", category=FutureWarning)

# YOLOv5 모델 경로
yolov5_model_path = "C:\\Users\\USER\\Desktop\\yoloprogram\\fixed_best.pt"
download_yolov5s6_model(destination_path=yolov5_model_path)

# 모델 로드
detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov5',
    model_path=yolov5_model_path,
    confidence_threshold=0.5,
    device='cuda:0'
)

# 결과 저장 디렉토리
output_dir = "C:\\Users\\USER\\Desktop\\yoloprogram\\captured_results\\"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# PySide6 GUI 클래스 정의
class PredictionViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-time Prediction Viewer")
        self.setGeometry(100, 100, 800, 600)

        # QLabel로 이미지 표시
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 타이머 설정: 주기적으로 이미지 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(1000)  # 1초마다 업데이트

    def update_image(self):
        image_path = os.path.join(output_dir, "prediction_visual.png")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.label.setPixmap(pixmap)
        else:
            self.label.setText("예측 이미지가 아직 생성되지 않았습니다.")

# YOLOv5와 카메라 연결 및 예측 수행
def start_prediction():
    cap = cv2.VideoCapture(0)  # 기본 카메라
    if not cap.isOpened():
        raise Exception("카메라를 열 수 없습니다.")

    frame_count = 0  # 프레임 카운터

    print("50프레임마다 슬라이스 기반 예측을 수행합니다. ESC를 눌러 종료하세요.")
    while True:
        ret, frame = cap.read()  # 카메라에서 프레임 읽기
        if not ret:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            break

        # 화면에 표시
        #cv2.imshow("Camera", frame)

        # 50프레임마다 예측 수행
        if frame_count % 50 == 0:
            print(f"{frame_count}번째 프레임 슬라이스 기반 예측 중...")

            # 슬라이스 기반 예측
            result = get_sliced_prediction(
                frame,
                detection_model,
                slice_height=256,  # 슬라이스 높이
                slice_width=256,   # 슬라이스 너비
                overlap_height_ratio=0.2,  # 슬라이스 세로 겹침
                overlap_width_ratio=0.2    # 슬라이스 가로 겹침
            )

            # 결과 시각화 저장
            result.export_visuals(export_dir=output_dir)
            print(f"결과 이미지가 저장되었습니다: {output_dir}")

        frame_count += 1

        # ESC 키를 누르면 종료
        if cv2.waitKey(1) == 27:
            print("종료합니다.")
            break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()

# PySide6 GUI 실행 및 예측 시작
if __name__ == "__main__":
    # PySide6 애플리케이션 초기화
    app = QApplication(sys.argv)

    # 예측 뷰어 실행
    viewer = PredictionViewer()
    viewer.show()

    # 예측 시작
    start_prediction()

    sys.exit(app.exec())
