import cv2
import mediapipe as mp
import numpy as np
import math
from datetime import datetime
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

class ArrowGame:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils
        self.score = 0
        self.hearts = []
        self.arrows = []
        self.is_drawing_bow = False
        self.last_shot_time = datetime.now()
        self.cooldown = 1.0
        self.heart_img = cv2.imread('heart.png', cv2.IMREAD_UNCHANGED)
        self.heart_img = cv2.resize(self.heart_img, (50, 50))
    
    def spawn_heart(self):
        if len(self.hearts) < 5:
            heart = {
                'x': np.random.randint(100, 540),
                'y': np.random.randint(100, 380),
                'speed': np.random.randint(2, 5)
            }
            self.hearts.append(heart)
    
    def draw_bow(self, frame, right_elbow, right_wrist):
        if right_elbow and right_wrist:
            bow_center = (int(right_elbow[0]), int(right_elbow[1]))
            bow_radius = 150
            cv2.ellipse(frame, bow_center, (bow_radius, bow_radius), 0, -45, 45, (255, 0, 255), 12)
            cv2.ellipse(frame, bow_center, (bow_radius+5, bow_radius+5), 0, -45, 45, (200, 0, 200), 8)
            cv2.line(frame, (int(right_elbow[0]), int(right_elbow[1])), (int(right_wrist[0]), int(right_wrist[1])), (200, 200, 255), 12)
            cv2.line(frame, (int(right_elbow[0]), int(right_wrist[1])), (int(right_wrist[0]), int(right_wrist[1])), (255, 255, 255), 6)
            distance = math.dist(right_elbow, right_wrist)
            draw_percentage = min(distance / 100.0, 1.0)
            return draw_percentage
        return 0
    
    def shoot_arrow(self, start_pos, direction):
        arrow = {
            'x': start_pos[0],
            'y': start_pos[1],
            'dx': direction[0] * 10,
            'dy': direction[1] * 10
        }
        self.arrows.append(arrow)
    
    def update_game_objects(self):
        for heart in self.hearts[:]:
            heart['x'] += math.sin(datetime.now().timestamp()) * heart['speed']
            if heart['x'] < 0 or heart['x'] > 640:
                self.hearts.remove(heart)
        
        for arrow in self.arrows[:]:
            arrow['x'] += arrow['dx']
            arrow['y'] += arrow['dy']
            
            for heart in self.hearts[:]:
                if math.dist([arrow['x'], arrow['y']], [heart['x'], heart['y']]) < 25:
                    self.hearts.remove(heart)
                    self.arrows.remove(arrow)
                    self.score += 10
                    break
            
            if (arrow['x'] < 0 or arrow['x'] > 640 or arrow['y'] < 0 or arrow['y'] > 480):
                self.arrows.remove(arrow)
    
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        overlay = frame.copy()
        
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                h, w, c = frame.shape
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                cv2.circle(overlay, (cx, cy), 5, (0, 255, 0), -1)
            
            right_shoulder = (
                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x * 640,
                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * 480
            )
            right_elbow = (
                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x * 640,
                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y * 480
            )
            right_wrist = (
                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].x * 640,
                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST].y * 480
            )
            
            draw_percentage = self.draw_bow(frame, right_elbow, right_wrist)
            
            if (draw_percentage > 0.8 and not self.is_drawing_bow and 
                (datetime.now() - self.last_shot_time).total_seconds() > self.cooldown):
                direction = np.array([right_wrist[0] - right_elbow[0],
                                   right_wrist[1] - right_elbow[1]])
                direction = direction / np.linalg.norm(direction)
                self.shoot_arrow(right_shoulder, direction)
                self.last_shot_time = datetime.now()
            
            self.is_drawing_bow = draw_percentage > 0.8
        
        if np.random.random() < 0.02:
            self.spawn_heart()
        
        self.update_game_objects()
        
        for heart in self.hearts:
            x, y = int(heart['x']), int(heart['y'])
            size = 40
            cv2.circle(overlay, (x-size//4, y), size//2, (0, 0, 255), -1)
            cv2.circle(overlay, (x+size//4, y), size//2, (0, 0, 255), -1)
            pts = np.array([[x-size//2, y+size//4], 
                            [x, y+size], 
                            [x+size//2, y+size//4]], np.int32)
            cv2.fillPoly(overlay, [pts], (0, 0, 255))
            cv2.circle(overlay, (x, y), size+10, (0, 0, 255), 4)
        
        for arrow in self.arrows:
            x, y = int(arrow['x']), int(arrow['y'])
            cv2.line(overlay,
                    (int(x - arrow['dx']*5), int(y - arrow['dy']*5)),
                    (x, y),
                    (0, 255, 255), 8)
            cv2.circle(overlay, (x, y), 10, (0, 255, 0), -1)
        
        alpha = 0.7
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        score_text = f'Score: {self.score}'
        cv2.rectangle(frame, (10, 10), (400, 100), (0, 0, 0), -1)
        cv2.putText(frame, score_text, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 4)
        
        return frame

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.game = ArrowGame()
    
    def transform(self, frame):
        frame = self.game.process_frame(frame.to_ndarray(format="bgr24"))
        return frame

# Streamlit App
st.title("Arrow Game - Streamlit Version")
st.write("Raise your right arm, draw back to shoot, and aim for the hearts!")

webrtc_streamer(key="arrow-game", video_transformer_factory=VideoTransformer)
