import librosa
import os
import numpy as np
from datetime import datetime
from django.core.files.storage import default_storage
from .keras_yamnet import params
from .keras_yamnet.yamnet import YAMNet, class_names
from .keras_yamnet.preprocessing import preprocess_input
from pathlib import Path

from data_process.prediction_entity import updatePrediction, getLastPrediction
from data_process.device_entity import getUserInfo

global sound_model

def load_sound_model():
    mypath = Path().absolute()
    global sound_model
    sound_model = YAMNet(weights=mypath/'server/sound_process/keras_yamnet/yamnet.h5')
    # run_sound_predict(mypath/'file.wav')


def save_sound_file(firebaseToken, file, time):
    get = getUserInfo(firebaseToken)
    userId = get[1]
    now = datetime.now()
    directory = 'storage/' + str(userId) + '/' + time.strftime("%Y%m%d") + '/'
    filename = time.strftime("%H%M%S") + ".wav"
    
    mypath = Path().absolute()
    file_name = default_storage.save(mypath/directory/filename, file)
    return file_name

def save_sound_prediction(predictions, record):
    print('\n', predictions, '\n')
    # return predictions
    soundArr = list(set(predictions))
    
    soundStr = ""
    index = 0
    for ele in soundArr:
        if index == len(soundArr) - 1:
            soundStr += ele
        else:
            soundStr += ele + ', '
        index = index + 1
    
    # record = getLastPrediction(firebaseToken)
    
    
    print(record)
    
    avg_heartbeat = record[0]
    date_time = record[1]
    # latitude = record[3]
    # longitude = record[4]
    deviceId = record[4]
    userId = record[5]
    prediction = record[6]
    recordId = record[7]
        
    if len(soundStr) > 0:
        prediction = prediction + " In audio has: " + soundStr + '.'
    else:
        prediction = prediction + " No dangerous predicted in audio."

    updatePrediction(recordId, prediction)
    
    return [avg_heartbeat, date_time, deviceId, prediction, userId]

def run_sound_predict(file, firebaseToken):
    RATE = params.SAMPLE_RATE
    WIN_SIZE_SEC = 0.975
    CHUNK = int(WIN_SIZE_SEC * RATE)
    
    plt_classes = [10, 11, 19, 20, 68, 69, 70, 81, 103, 292, 304, 316, 317, 318, 319, 393, 394, 420, 421, 422, 463, 464]
    # print(plt_classes)
    mypath = Path().absolute()
    yamnet_classes = class_names(mypath/'server/sound_process/keras_yamnet/yamnet_class_map.csv')
 
    # file = 'test4.mp3'
    y, sr = librosa.load(file, sr=None)
    print("\nFile loaded successfully\n")
    frames = librosa.util.frame(y, frame_length=CHUNK, hop_length=CHUNK)
    frames = frames.T  # Chuyển vị ma trận

    predictions = []
    # Chia dữ liệu âm thanh thành các khung có kích thước phù hợp
    for frame in frames:
        data = preprocess_input(frame, sr)
        prediction = sound_model.predict(np.expand_dims(data, 0))[0]
        # get the highest probability class and its name
        prediction = np.argmax(prediction)
        print (prediction, yamnet_classes[prediction])
        check = prediction in plt_classes
        if check == True:
            predictions.append(yamnet_classes[prediction])
    return predictions