# Drowsiness-prevention-system
----
This system is designed for individuals who frequently feel sleepy while driving, aiming to prevent accidents caused by drowsiness.

This system has several features :
A warning alert and video recording system activate if the driver nods off for more than 2 seconds. 
It also includes a calendar that allows recording on the calendar.

## How Can I Start ?
```python
python main.py --data your_video.mp4 --max_face 1 --min_detect 0.5 --min_track 0.5 --model 'yolov8n_face.pt'
```
+ data : Input video path
+ max_face : How many faces want to detect
+ min_detect : Minimum detection confidence score
+ min_track : Minimum tracking confidence score
+ model : YOLOv8 Model

## Let's Start
![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/0b9f6a42-a110-4e64-99a9-39da0764fde1)
After triggering the above code, you will see this image.

![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/6e8a7092-7709-49bb-a133-f56524bdca37)
Use the mouse to crop the image you want to detect and track.

After croped Press the Enter Key !

![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/465a2496-e31e-4ae9-949f-791b027b04e3)
The system uses the right eye as a reference to determine sleep/awake status. 
If the user sleeps for more than 2 seconds, a loud song is played. 
The system reverses the Judgment statement sleep and awake. Because it is difficult to find videos of people sleeping.

You can fix the code below
```python
if diff_x > 0 and diff_y < 0:
    is_close = False
else:
    is_close = True
```

# Calendar
![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/c46f035c-5afd-4e56-83c6-57fe87aa8355)
![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/2abfedde-56c8-48b9-8e45-ba0e13839b15)
![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/d2e8b587-aa1b-4b3d-8156-a382db94a03d)
Through the calendar, you can see how many times drowsy driving occurred on a specific date.
For example, once is indicated in green, twice in orange, and three or more times in red.

![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/9592f118-29a4-4273-a979-e5bb391118c7)
You can also double-click the date to view the recorded video.
![image](https://github.com/TCK2001/Drowsiness-prevention-system/assets/87925027/32fe3015-4bef-4522-9bea-e05d99309a6e)



