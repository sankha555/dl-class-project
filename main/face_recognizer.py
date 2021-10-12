import cv2 as cv
import numpy as np
import os
from PIL import Image

from django.conf import settings
MAIN_DIR = settings.BASE_DIR / 'main'

IMAGE_DIRECTORY = MAIN_DIR / 'foreheadData'
TRAINING_IMAGES = IMAGE_DIRECTORY / 'train'
TEST_IMAGES = IMAGE_DIRECTORY / 'test'

def train_model():
    USERNAMES = [str(i) for i in os.listdir(TRAINING_IMAGES)]
    
    features = []
    labels = []

    for username in USERNAMES:
        if username == '.DS_Store':
            continue
        
        user_images = TRAINING_IMAGES / username
        
        for file in os.listdir(user_images):
            image_path = str(user_images / file)
            image = cv.imread(image_path)
            
            grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            features.append(grayscale_image)
            labels.append(int(username))
        # except:
        #     continue
            
    feature_vector = np.array(features, dtype='object')
    label_vector = np.array(labels)
    
    if feature_vector == [] or label_vector == []:
        feature_vector = np.load('feature_vector.npy', allow_pickle=True)
        label_vector = np.load('label_vector.npy')

    face_recognition_model = cv.face.LBPHFaceRecognizer_create()
    face_recognition_model.train(feature_vector, label_vector)


    face_recognition_model.save(str(MAIN_DIR / 'recognition_model/face_recognition.yml'))
    np.save(str(MAIN_DIR / 'recognition_model/feature_vector.npy'), feature_vector)
    np.save(str(MAIN_DIR / 'recognition_model/label_vector.npy'), label_vector)

def model_loaded():
    for file in ['feature_vector.npy', 'label_vector.npy', 'face_recognition.yml']:
        if file not in os.listdir(MAIN_DIR / 'recognition_model'):
            return False
    return True

def read_image(image_path):
    image_path = str(image_path)
    image = cv.imread(image_path, 1)
    return image

def prediction(image):
    while model_loaded() == False:
        train_model()
        
    face_recognition_model = cv.face.LBPHFaceRecognizer_create()
    face_recognition_model.read(str(MAIN_DIR / 'recognition_model/face_recognition.yml'))
    
    grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    label, confidence_complement = face_recognition_model.predict(grayscale_image)
    confidence = 100 - confidence_complement
    
    return (label, confidence)

