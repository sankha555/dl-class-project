from django.shortcuts import render, redirect
from main.face_recognizer import prediction, read_image, train_model
from django.conf import settings
from django.contrib import messages

import os

MAIN_DIR = settings.BASE_DIR / 'main'

def save_image(captured_image, filename = None, directory = (MAIN_DIR / 'temp')):
    image_path = directory / filename if filename is not None else directory
    if filename is None:    
        temp_name = 'temp_user'
        i = 0
        while temp_name + str(i) + '.jpg' in os.listdir(directory):
            i += 1
        filename = temp_name + str(i) + '.jpg'
        
        image_path = directory / filename

    if filename in os.listdir(directory):
        temp_name = filename
        i = 0
        while temp_name + str(i) + '.jpg' in os.listdir(directory):
            i += 1
        filename = temp_name + str(i) + '.jpg'
        
        image_path = directory / filename
    
    with open(image_path, 'wb+') as image:
        for chunk in captured_image.chunks():
            image.write(chunk)
        
    return image_path

def get_image_directory(username):
    if username not in os.listdir(MAIN_DIR / 'foreheadData/train'):
        os.mkdir(MAIN_DIR / ('foreheadData/train/' + username))
    return MAIN_DIR / ('foreheadData/train/' + username)
    

def verify_user(request):
    if request.method == "POST":
        data = request.POST
        files = request.FILES
        
        claimed_username = str(data["username"])
        captured_image = files['file']
        
        image_path = save_image(captured_image)
        image = read_image(image_path)
        
        challenge_result = prediction(image)
        
        identified_user_username = str(challenge_result[0])
        confidence = challenge_result[1]
        
        if identified_user_username != claimed_username:
            context = {
                "result": "failed",
                "message": "Sorry, but you don't seem to be the user with username " + claimed_username,
                "config": {
                    "identified_username": identified_user_username,
                    "confidence": confidence
                }
            }
        else:
            context = {
                "result": "passed",
                "message": "Verification successful! Welcome, user " + claimed_username + "! Have a nice day.",
                "config": {
                    "identified_username": identified_user_username,
                    "confidence": confidence
                }
            }
            
        os.remove(image_path)
        
        return render(request, 'main/challenge_result.htm', context)
    
    return render(request, 'main/verify_user.htm')
    
def challenge_result(request, context):
    return render(request, 'main/challenge_result.htm', context)

def register_user(request):
    if request.method == "POST":
        data = request.POST
        files = request.FILES
        
        username = data['username']
        
        user_images_directory = get_image_directory(username)
        
        for i in range(12):
            try:
                filename = files['file'+str(i+1)].name
                image = files['file'+str(i+1)]
                _ = save_image(image, filename, user_images_directory)
            except:
                continue
            
        train_model()
        
        messages.success(request, "Image uploaded successfully!", fail_silently=True)
        
        return redirect('verify_user')
            
    return render(request, 'main/register_user.htm')