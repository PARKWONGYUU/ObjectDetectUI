from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from sahi.utils.yolov5 import download_yolov5s6_model
import os
import cv2
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QMessageBox
import subprocess
import shutil

class LearningModel:
    _instance = None  # 싱글톤 인스턴스를 저장할 클래스 변수

    def __new__(cls, *args, **kwargs):
        # 이미 생성된 인스턴스가 있다면 그것을 반환
        if cls._instance is None:
            cls._instance = super(LearningModel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 초기화가 한 번만 실행되도록 방지
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True
                
        super().__init__()
        self.yolov5_model_path = "C:\\Users\\USER\\Desktop\\newprogram\\model\\fixed_best.pt"
        self.yolov5_repo_path = "C:/Users/USER/Desktop/newprogram/model/yolov5/content/yolov5"
        self.output_dir = "C:/Users/USER/Desktop/newprogram/model/captured_results"
        self.dataset_path = "C:/Users/USER/Desktop/newprogram/learning/dataset/data.yaml"
        self.learning_output_dir = "C:/Users/USER/Desktop/newprogram/learning"
        download_yolov5s6_model(destination_path=self.yolov5_model_path)
        self.epoch_progress_callback = None
        self.training_started_callback = None
        self.training_finished_callback = None
        self.training_error_callback = None

        self.predict_image_list = []
        self.predict_label_list = []

        self.on_train = False

        self.training_thread = TrainingThread(
            data_yaml_path=self.dataset_path,
            img_size=640,
            batch_size=16,
            epochs=50,
            pretrained_weights=self.yolov5_model_path,
            yolov5_repo_path=self.yolov5_repo_path,
            output_dir=self.learning_output_dir
        )

        self.training_thread.training_status_changed.connect(self.on_training_status_changed)

        # 모델 로드
        self.detection_model = AutoDetectionModel.from_pretrained(
            model_type='yolov5',
            model_path=self.yolov5_model_path,
            confidence_threshold=0.5,
            device='cuda:0'
        )
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("카메라를 열 수 없습니다.")
        
        # 결과 저장 디렉토리 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def on_training_status_changed(self, is_training):
        if is_training:
            self.on_train = True
        else:
            self.on_train = False

    def predict_input_image(self, image_path):
        image = cv2.imread(image_path)

        result = get_sliced_prediction(
            image,                # OpenCV 프레임을 입력
            self.detection_model,      # SAHI 모델
            slice_height=256,     # 슬라이스 높이
            slice_width=256,      # 슬라이스 너비
            overlap_height_ratio=0.2,  # 슬라이스 세로 겹침
            overlap_width_ratio=0.2,    # 슬라이스 가로 겹침
        )
            # 이미지 크기
        img_height, img_width, _ = image.shape

        # 결과 저장 경로 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # 결과 이미지 경로 및 저장
        image_file_name = f"prediction_{len(self.predict_image_list) + 1}"
        image_path = os.path.join(self.output_dir, image_file_name)
        result.export_visuals(export_dir=self.output_dir, file_name=image_file_name)

        # 결과 라벨 경로 및 저장
        label_file_name = f"prediction_{len(self.predict_label_list) + 1}.txt"
        label_path = os.path.join(self.output_dir, label_file_name)
        self.save_yolov5_labels(result.object_prediction_list, label_path, img_width, img_height)

        # 경로를 리스트에 저장
        self.predict_image_list.append(image_path)
        self.predict_label_list.append(label_path)

        return label_path

    def clear_output_files(self):
        # 이미지 파일 삭제
        for image_path in self.predict_image_list:
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"이미지 파일 삭제 완료: {image_path}")
                except Exception as e:
                    print(f"이미지 파일 삭제 실패: {image_path}, 오류: {e}")

        # 라벨 파일 삭제
        for label_path in self.predict_label_list:
            if os.path.exists(label_path):
                try:
                    os.remove(label_path)
                    print(f"라벨 파일 삭제 완료: {label_path}")
                except Exception as e:
                    print(f"라벨 파일 삭제 실패: {label_path}, 오류: {e}")

        # 리스트 초기화
        self.predict_image_list.clear()
        self.predict_label_list.clear()
        print("이미지 및 라벨 경로 리스트 초기화 완료.")

    def predict_capture_image(self):
        ret, frame = self.cap.read()
        if not ret:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            return None
        flipped_frame = cv2.flip(frame, -1)

        img_height, img_width, _ = frame.shape

        result = get_sliced_prediction(
            flipped_frame,                # OpenCV 프레임을 입력
            self.detection_model,      # SAHI 모델
            slice_height=256,     # 슬라이스 높이
            slice_width=256,      # 슬라이스 너비
            overlap_height_ratio=0.2,  # 슬라이스 세로 겹침
            overlap_width_ratio=0.2    # 슬라이스 가로 겹침
        )

        # 결과 시각화 저장
        result_path = os.path.join(self.output_dir, "prediction_visual.png")
        result.export_visuals(export_dir=self.output_dir)

        # 결과를 라벨 파일로 저장
        label_path = os.path.join(self.output_dir, "prediction_visual.txt")  # 저장할 라벨 파일 경로 - 폴더기반으로 바꾸기
        self.save_yolov5_labels(result.object_prediction_list, label_path, img_width, img_height)

        print(f"결과 라벨이 저장되었습니다: {label_path}")
        return result_path
    
    def save_yolov5_labels(self, object_prediction_list, label_path, img_width, img_height):
        with open(label_path, "w") as label_file:
            for obj in object_prediction_list:
                class_id = obj.category.id
                x_min, y_min, x_max, y_max = obj.bbox.minx, obj.bbox.miny, obj.bbox.maxx, obj.bbox.maxy

                # YOLOv5 형식의 좌표로 변환
                x_center = ((x_min + x_max) / 2) / img_width
                y_center = ((y_min + y_max) / 2) / img_height
                width = (x_max - x_min) / img_width
                height = (y_max - y_min) / img_height
                # 라벨 파일 작성
                label_file.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    def get_model_info(self):
        confidence_threshold = self.detection_model.confidence_threshold
        device = self.detection_model.device
        num_categories = self.detection_model.num_categories
        category_names = list(self.detection_model.category_mapping.values())

        info = (
            f"Device: {device}, "
            f"Confidence Threshold: {confidence_threshold}, "
            f"Number of Categories: {num_categories}, "
            f"Categories: {category_names}"
        )
        return info
    
    def get_labels(self, class_id=None):
        if class_id is not None:
            if self.detection_model.category_names:
                return self.detection_model.category_names[class_id]
            return f"ID {class_id} not found"
        else:
            labels = []
            if self.detection_model.category_mapping:
                for cid, label in self.detection_model.category_mapping.items():
                    labels.append(f"Class {cid}: {label}")
            return labels
    
    def release_camera(self):
        self.cap.release()
    
    
    def start_training(self):
        # 스레드 시그널 연결
        self.training_thread.training_started.connect(self.on_training_started)
        self.training_thread.training_finished.connect(self.on_training_finished)
        self.training_thread.training_error.connect(self.on_training_error)
        self.training_thread.epoch_progress.connect(self.emit_epoch_progress)

        # 스레드 시작
        self.training_thread.start()

    def emit_epoch_progress(self, current_epoch, total_epochs):
        if self.epoch_progress_callback:
            self.epoch_progress_callback(current_epoch, total_epochs)

    def set_epoch_progress_callback(self, callback):
        self.epoch_progress_callback = callback

    def on_training_started(self):
        print("Model training has started.")

    def on_training_finished(self, trained_model_path):
        print("Training Completed", f"Model saved at: {trained_model_path}")

    def on_training_error(self, error_message):
        print("Training Error", f"Error during training: {error_message}")
    
    def stop_training(self):
        if self.training_thread.isRunning():
            self.training_thread.request_stop()
            print("Training stop requested.")
    

import re
class TrainingThread(QThread):
    training_started = Signal()
    training_finished = Signal(str)
    training_error = Signal(str)
    training_status_changed = Signal(bool)
    epoch_progress = Signal(int, int)  # (현재 Epoch, 전체 Epoch)

    def __init__(self, data_yaml_path, img_size=640, batch_size=16, epochs=50, pretrained_weights="yolov5s.pt", yolov5_repo_path="", output_dir=""):
        super().__init__()
        self.data_yaml_path = data_yaml_path
        self.img_size = img_size
        self.batch_size = batch_size
        self.epochs = epochs
        self.pretrained_weights = pretrained_weights
        self.yolov5_repo_path = yolov5_repo_path
        self.output_dir = output_dir
        self.dir_name = "trained_model"
        self.last_epoch = -1
        self.stop_requested = False

    def run(self):
        self.training_started.emit()
        self.training_status_changed.emit(True)
        try:
            command = [
                "python", os.path.join(self.yolov5_repo_path, "train.py"),
                "--img", str(self.img_size),
                "--batch", str(self.batch_size),
                "--epochs", str(self.epochs),
                "--data", self.data_yaml_path,
                "--weights", self.pretrained_weights,
                "--project", self.output_dir,
                "--name", self.dir_name,
                "--exist-ok"
            ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            while process.poll() is None:
                if self.stop_requested:  # 중지 요청 확인
                    target_dir = os.path.join(self.output_dir, self.dir_name)
                    self.clear_directory(target_dir)
                    process.terminate()  # 프로세스 종료
                    self.stop_requested = False
                    print("Training stopped by user.")
                    return

                line = process.stdout.readline()
                if line:
                    print(line.strip())
                    epoch_info = self.extract_epoch_info(line)
                    if epoch_info:
                        current_epoch, total_epochs = epoch_info
                        self.epoch_progress.emit(current_epoch, total_epochs)

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command)

            trained_model_path = os.path.join(self.output_dir, "trained_model", "weights", "best.pt")
            self.training_finished.emit(trained_model_path)
        except subprocess.CalledProcessError as e:
            self.training_error.emit(str(e))
        finally:
            self.training_status_changed.emit(False)
            if self.last_epoch == self.epochs:
                self.on_training_finished()

    def extract_epoch_info(self, log_line):

        try:
            parts = log_line.strip().split()  # 공백 기준으로 분리
            if parts and '/' in parts[0]:  # 첫 번째 항목에 '/'가 있는지 확인
                current_epoch, total_epochs = map(int, parts[0].split('/'))
                if current_epoch != self.last_epoch:  # 이전 epoch와 비교
                    self.last_epoch = current_epoch  # 갱신
                    return current_epoch, total_epochs
        except ValueError:
            pass
        return None
    
    def request_stop(self):
        self.stop_requested = True
        self.wait()

    def clear_directory(self, directory_path):
        if not os.path.exists(directory_path):
            print(f"Directory {directory_path} does not exist.")
            return

        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)  # 파일 및 심볼릭 링크 삭제
                    print(f"Deleted file: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # 하위 폴더 삭제
                    print(f"Deleted folder: {item_path}")
            print(f"Cleared all contents in {directory_path}.")
        except Exception as e:
            print(f"Error clearing directory {directory_path}: {e}")

    def on_training_finished(self):
        try:
            # Backup 디렉토리로 기존 fixed_best.pt 이동
            backup_dir = "C:\\Users\\USER\\Desktop\\newprogram\\model\\backup"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # 기존 모델 백업
            if os.path.exists(self.pretrained_weights):
                backup_path = os.path.join(backup_dir, os.path.basename(self.pretrained_weights))
                shutil.move(self.pretrained_weights, backup_path)
                print(f"Previous model moved to backup: {backup_path}")

            # 새로운 fixed_best.pt 설정
            new_model_path = "C:\\Users\\USER\\Desktop\\newprogram\\learning\\trained_model\\weights\\best.pt"
            if os.path.exists(new_model_path):
                shutil.move(new_model_path, self.pretrained_weights)
                print(f"New fixed_best.pt moved to: {self.pretrained_weights}")
            else:
                print(f"Error: Trained model file not found at {new_model_path}")
        except Exception as e:
            print(f"Error during model management: {e}")