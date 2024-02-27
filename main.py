import argparse
import cv2
import tensorflow as tf
from ultralytics import YOLO
import mediapipe as mp
import time
import threading
import pygame

pygame.init()
# yolo output 
# C:\Users\TCK\anaconda3\envs\tck\lib\site-packages\ultralytics\engione\predictor.py\basePredictor\클래스에서 Logger.info마크 다운 해제 하면됨
# face landmark https://github.com/google/mediapipe/blob/a908d668c730da128dfa8d9f6bd25d519d006692/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png
# ignore the warning message
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

parser = argparse.ArgumentParser()
parser.add_argument('--data', help='Input Video path', type=str, required=True, default='./driver3.mp4')
parser.add_argument('--max_face', help='how many faces want to detect', type=int, default=1)
parser.add_argument('--min_detect', help='Minimum detection confidence', type=int, default=0.5)
parser.add_argument('--min_track', help='Minimum tracking confidence', type=int, default=0.5)
parser.add_argument('--model', help='Yolov8 model', type=str, default='yolov8n-face.pt')

args = parser.parse_args()

def resize_video(frame):
    return cv2.resize(frame, (new_width, new_height))

def crop_box(event, x, y, flags, param):
    global box_start, box_end, drawing
    try: 
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            box_start = (x, y)
            
            # Set box_end to the same as box_start initially
            box_end = (x, y)  
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                # Create a copy of the frame to draw the rectangle on
                frame_copy = frame.copy()
                cv2.rectangle(frame_copy, box_start, (x, y), (255, 0, 0), 2)
                cv2.imshow("main_frame", frame_copy)
                
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            box_end = (x, y)

        elif event == cv2.EVENT_KEYDOWN and flags == cv2.EVENT_FLAG_ALTKEY:
            if param == ord('p'):
                box_start = None
                box_end = None
                frame_copy = frame.copy()
                cv2.imshow("main_frame", frame_copy)
    except Exception as ex:
        pass
 
def play_alarm():
    pygame.mixer.music.load('alarm.mp3')
    pygame.mixer.music.play() 
            
def face_landmark():
    global frame, box_start, box_end, right_landmark_dict, is_close
    right_landmark_dict = {}
    # 녹화할 비디오의 설정
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None
    recording = False
    start_time = None
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            frame = resize_video(frame)
            face_frame = frame[box_start[1]:box_end[1], box_start[0]:box_end[0]]
            results = model.predict(source=face_frame, conf=0.3, classes=0, max_det=1, device="cuda:0")
            
            # classes = 0 => people
            for result in results:
                for box in result.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box[:4])
                    face_frame_crop = face_frame[y1:y2, x1:x2]
            
                    image_rgb = cv2.cvtColor(face_frame_crop, cv2.COLOR_BGR2RGB)
                    results_landmarks = face_mesh.process(image_rgb)

                    if results_landmarks.multi_face_landmarks:
                        for face_landmarks in results_landmarks.multi_face_landmarks:
                            # for idx in left_eye_landmarks:
                            #     landmark = face_landmarks.landmark[idx]
                            #     x = int(landmark.x * face_frame.shape[1])
                            #     y = int(landmark.y * face_frame.shape[0])
                            #     cv2.circle(face_frame, (x, y), 2, (0, 255, 0), -1)
                            
                            for idx in right_eye_landmarks:
                                landmark = face_landmarks.landmark[idx]
                                x = int(landmark.x * face_frame_crop.shape[1])
                                y = int(landmark.y * face_frame_crop.shape[0])
                                right_landmark_dict[idx] = (x, y)
                                cv2.circle(face_frame_crop, (x, y), 2, (0, 255, 0), -1)
                            # print(right_landmark_dict)
                            
                            for i in range(2, len(right_landmark_dict) - 4, 2):
                                diff_x = right_landmark_dict.get(right_eye_landmarks[i])[0] - right_landmark_dict.get(right_eye_landmarks[i + 1])[0]
                                diff_y = right_landmark_dict.get(right_eye_landmarks[i])[1] - right_landmark_dict.get(right_eye_landmarks[i + 1])[1]
                                print("DIFF : ",diff_x, diff_y)
                                ## need to fix
                                if diff_x > 0 and diff_y < 0:
                                    is_close = True
                                else:
                                    is_close = False
                                    
                            face_frame[y1:y2, x1:x2] = face_frame_crop
                            
                            if is_close:
                                cv2.putText(face_frame, 'Sleep!', (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
                            else:
                                cv2.putText(face_frame, 'GOOD', (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
                            
                            if is_close and not recording:
                                start_time = time.time()
                                recording = True
                                
                            if not is_close and recording:
                                recording = False
                                start_time = None
                                if pygame.mixer.music.get_busy():
                                    pygame.mixer.music.stop()
                                if out is not None:
                                    out.release()
                                    out = None
                                break
                            if is_close and time.time() - start_time >= 2:
                                # alarm.mp3 재생
                                if not pygame.mixer.music.get_busy():
                                    threading.Thread(target=play_alarm).start()
                                #     pygame.mixer.music.play()
                                # 비디오 녹화 시작
                                if out is None:
                                    now = time.strftime("%Y-%m-%d_%H-%M-%S")
                                    out = cv2.VideoWriter(f"./calendar/{now}.avi", fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                                    print("Writing............................")
                                out.write(frame)
                        
                    cv2.imshow("Cropped Frame", face_frame)
                    key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):

                # Pause the video and allow resetting the bounding box
                while True:
                    key = cv2.waitKey(0) & 0xFF
                    if key == ord('p'):
                        break
                    elif key == ord('q'):
                        cap.release()
                        cv2.destroyAllWindows()
                        exit()

                    # Reset box_start and box_end when 'r' key is pressed
                    elif key == ord('r'):
                        try:
                            box_start = None
                            box_end = None
                            frame_copy = frame.copy()
                            cv2.imshow("main_frame", frame_copy)
                            cv2.setMouseCallback("main_frame", crop_box, param=frame)
                        except Exception as ex:
                            pass

    except Exception as ex:
        pass
                
        
if __name__ == '__main__':
    font = cv2.FONT_HERSHEY_SIMPLEX
    is_close = False
    model = YOLO(args.model)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=args.max_face, min_detection_confidence=args.min_detect, min_tracking_confidence=args.min_track)
    
    cap = cv2.VideoCapture(args.data)
    
    drawing = False
    
    # Resize the video size
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    new_width = int(width // 3)
    new_height = int(height // 3)

    # define the left/right eye landmarks
    left_eye_landmarks = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
    right_eye_landmarks = [398, 382, 384, 381, 385, 380, 386, 374, 387, 373, 388, 390, 466, 249, 362, 263]
    
    cv2.namedWindow("main_frame")
    cv2.setMouseCallback("main_frame", crop_box)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        frame = resize_video(frame)
        
        cv2.imshow("main_frame", frame)
        
        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key == 13:  # Enter key
            face_landmark()
        
    cap.release()
    cv2.destroyAllWindows()