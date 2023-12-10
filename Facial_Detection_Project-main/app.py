# Importing Necessary Libraries
# <a target="_blank" href="https://github.com/MausmiSinha/Facial_Detection_Project" style="font-size:36px"> <i class="fa-brands fa-github"></i> </a>

import cv2
import gspread.exceptions
import numpy as np
from keras.models import model_from_json
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer, VideoTransformerBase
from PIL import Image
import time
import gspread
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import pandas as pd

Gsheet = "emotion"
tabname ="emotionss"

def get_sheet_data(Gsheet,tabname):
    gc = gspread.service_account(filename='C:\\Users\\HP\\Downloads\\Facial_Detection_Project-main\\Facial_Detection_Project-main\\emotions-407707-7145e7492a4f.json')
    sh = gc.open(Gsheet)
    ws = sh.worksheet(tabname)
    df = pd.DataFrame(ws.get_all_records())
    return df

df = get_sheet_data(Gsheet,tabname)










logo = Image.open('images/logo.png')
st.set_page_config(page_title="Emotion Detection",page_icon=logo , initial_sidebar_state = 'auto')

css_example = '''                                           
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">    
    
    <style>
        .bodyP1{
            font-size: 20px;
        }
        .footer{
            display: flex;
            justify-content:center;
            align-items: center;
            font-size: 20px;
            font-weight: 300;
            margin-top: 50px;
        }
        .aboutUs p{
            font-size: 18px;
            text-align: justify;
        }
        .header{
            display: flex;
            flex-direction:column;
            justify-content: center;
            align-items: center;
        }
    </style>
'''
st.write(css_example, unsafe_allow_html=True)

# Declaring Classes
emotion_classes = {
    0: "Angry", 
    1: "Disgust", 
    2: "Fear", 
    3: "Happy", 
    4: "Neutral", 
    5: "Sad", 
    6: "Surprise"}

# Loading Trained Model:
json_file = open(r"model/model_v2.json", 'r')

# Loading model.json file into model
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

# Loading Weights:
model.load_weights(r"model/new_model_v2.h5")

print("Model lodded scussesfully")

# Loading Face Cascade
try: 
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
except Exception:
    st.error("Unable to load Cascade Classifier", icon="⚠️")


class EmotionDetector(VideoTransformerBase):
    def __init__(self):
        super().__init__()
        self.emotion_log = []
        self.start_time = None  # Track the start time when the first face is detected
        self.gc = gspread.service_account(filename='C:\\Users\\HP\\Downloads\\Facial_Detection_Project-main\\Facial_Detection_Project-main\\emotions-407707-7145e7492a4f.json')
        self.sh = self.gc.open(Gsheet)
        self.ws = self.sh.worksheet(tabname)

       



    def transform(self, frame):
        stop_button = st.button("Stop")
        img = np.array(frame.to_ndarray(format="bgr24"))
        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        num_face = face_detector.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in num_face:
            if self.start_time is None:
                self.start_time = time.time()  # Set the start time when the first face is detected
            cv2.rectangle(img, (x, y - 50), (x + w, y + h + 10), (0, 255, 0), 4)
            roi_gray_frame = gray_frame[y:y + h, x: x + w]
            cropped_img = np.expand_dims(cv2.resize(roi_gray_frame, (48, 48), -1), 0)

            if np.sum([roi_gray_frame]) != 0:
                emotion_prediction = model.predict(cropped_img)
                maxindex = int(np.argmax(emotion_prediction))
                label_position = (x, y)
                output = str(emotion_classes[maxindex])
                cv2.putText(img, output, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Record the detected emotion
                self.emotion_log.append(output)

        return img
    def write_emotions_to_sheet(self):
        if self.start_time is not None:
            elapsed_time = int(time.time() - self.start_time)
            # Add the current elapsed time to the first column
            self.emotion_log.insert(0, elapsed_time)
            # Append the log to the Google Sheet
            self.ws.append_row(self.emotion_log)
            self.start_time = None  # Reset the start time for the next recording session

    def on_stop_button_click(self):
        self.stop_button_clicked = True
        st.stop()  # Stop the Streamlit app after writing to the sheet



def main():
    activiteis = ["Home", "About Us"]
    choice = st.sidebar.selectbox("Select Activity", activiteis)    
    html_sidebar =  """
        <div align="center" style="text-align:center">
            <h2>Developed By: Pallavi Sharma</h2>
            <strong>Email:</strong> <a target="_blank" href="mailto:sharmapallavi63481@gmail.com"> sharmapallavi63481@gmail.com</a>
            <br>
        </div> 
    """
    st.sidebar.markdown(html_sidebar, unsafe_allow_html=True)


    if choice == "Home":
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write('')

        with col2:
            st.image(logo, width=200)

        with col3:
            st.write('')
        header = """
                    <div class = "header">
                        <h1>Emotion Detector</h1>
                    </div>
                """
        st.markdown(header,unsafe_allow_html=True)
        html_temp_home1 = """
                            <div>
                                <p class="bodyP1">Welcome to Emotion Detector. This is an emotion recognition web application! My advanced technology combines OpenCV and Convolutional Neural Networks to accurately identify emotions in real-time. </p>
                                <p class="bodyP1">My application is user-friendly and easy to use. Simply use your computer's camera to capture a live video feed, and our advanced algorithms will quickly analyze the facial expressions to detect the emotion displayed. My application can recognize a wide range of emotions, including happiness, sadness, anger, surprise, fear, and disgust.</p>
                                <h2>Try Now</h2>
                                <p>Click on start to use webcam and detect your face emotion</p>
                            </div>
                            """
        st.markdown(html_temp_home1, unsafe_allow_html=True)
        webrtc_streamer(key="example", video_transformer_factory=EmotionDetector)
        html_home2  = """
            <div class="footer">
                <p>&copy; 2023 by Pallavi Sharma. All rights reserved.</p>
            </div>
        """
        st.write(html_home2, unsafe_allow_html=True)
    elif choice == "About Us":
        st.title("About Us:")
        html_temp_about1= """
                            <div class="aboutUs">
                                <p>
                                    Emotion Detector is an Web Application created by Pallavi Sharma. The application uses OpenCV and Convolutional Neural Network model to accurately detect emotions in real-time.
                                </p>
                                <p>
                                    I worked on this project to create an easy-to-use web application that can accurately detect a wide range of emotions. I hope that this application can be useful for researchers, educators, and anyone interested in exploring the field of emotion detection.
                                </p>
                                <p>
                                    If you have any questions or feedback about this project, please feel free to contact us at <a target="_blank" href="mailto:sharmapallavi63481@gmail.com"> sharmapallavi63481@gmail.com</a>
                                </p>
                            </div>
                                    """
        st.markdown(html_temp_about1, unsafe_allow_html=True)
        # st.title("Authors:")
        # st.image(['images/Aman Singh Bhogal.jpg','images/mausmi.jpg'], caption=["Aman Singh Bhogal", "Mausmi Sinha"], width=350)
    else:
        pass


if __name__ == "__main__":
    main()


