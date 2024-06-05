from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import Photo, Audio
import base64
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import os
import librosa

image_model = load_model('D:\\YapayZekaProje\\emotion_detection_cnn_model.h5')

audio_model = load_model('D:\\YapayZekaProje\\emotion_detection_model.h5')

def index(request):
    return render(request, 'camera/index.html')

def upload(request):
    if request.method == 'POST':
        existing_file_path = 'D:\\Myproject2\\myproject\\media\\photos\\' + "temp.png"
        if os.path.exists(existing_file_path):
            os.remove(existing_file_path)
        
        imagedizi = []
        data = request.body.decode('utf-8')
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        
        photo = Photo.objects.create(image=image)
        image_path = photo.image.path  # Path al

        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized_image = cv2.resize(gray_image, (48, 48))
        imagedizi.append(resized_image)
        imgarr = np.array(imagedizi)
        imgarr = imgarr.reshape((1, 48, 48, 1))  # Düzenleme

        result = image_model.predict(imgarr)
        result_list = result.tolist()[0]  #arrayse liste ekle

        emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        max_index = np.argmax(result_list)  # en yüksek duyguyu bul
        predicted_emotion = emotion_labels[max_index]  #label ver
        
        return JsonResponse({'status': 'success', 'result': result_list})
    
    return JsonResponse({'status': 'fail'})

def extract_features(file_path):
    audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
    return np.mean(mfccs.T, axis=0)

def upload_audio(request):
    if request.method == 'POST':
        ses = []
        audio_file = request.FILES['audio']
        existing_file_path = 'D:\\Myproject2\\myproject\\media\\audio\\' + "recording.wav"
        
        # ses upload
        with open(existing_file_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        
        # düzen + arry
        mfccs = extract_features(existing_file_path)
        ses.append(mfccs)
        sesarr = np.array(ses)
        
        # tahmin
        result = audio_model.predict(sesarr)
        result_list = result.tolist()[0]  #list
        
        # Emotion labels
        emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
        max_index = np.argmax(result_list)  #en yüksek ses al
        predicted_emotion = emotion_labels[max_index]  # label var

        return JsonResponse({'status': 'success', 'result': result_list})
    
    return JsonResponse({'status': 'fail'})


def gallery(request):
    photos = Photo.objects.all()
    return render(request, 'camera/gallery.html', {'photos': photos})
