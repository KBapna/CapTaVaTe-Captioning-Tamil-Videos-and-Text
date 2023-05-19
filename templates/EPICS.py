#!/usr/bin/env python
# coding: utf-8

# In[1]:


import whisper
import sys
import torch
from deep_translator import GoogleTranslator
import ffmpeg
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
import pandas as pd
import os
import moviepy.editor as mp
from moviepy.editor import *
import cv2
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings
from PIL import ImageFont, ImageDraw, Image
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(DEVICE)
global argument
if len(sys.argv)>1:
    argument = sys.argv[1]
model = whisper.load_model("medium",download_root=r"D:\College\EPICS\WHISPER MODELS")


# In[2]:


class Transcriptor:
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    def __init__(self,audio):
        self.audio=whisper.pad_or_trim(audio)
        self.mel=whisper.log_mel_spectrogram(self.audio).to(DEVICE)
    def detect_language(self):
        mel=self.mel
        _, probs = model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
        return(max(probs, key=probs.get))
    def transcribe(self):
        mel=self.mel
        self.detect_language()
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model,mel, options)
        print(result.text)


# In[3]:


class Custom_Translator:
    def __init__(self):
        self.name="captions"
        global argument
        self.uploaded_vid=argument
        name_of_file="storage"
        self.input_file=name_of_file+".mp4"
        self.audio_file=name_of_file+".mp3"
        self.output_name=name_of_file+".mp4"
        path=f"D:/College/EPICS/captiontesting/{self.name}"
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"{self.name} created.")
        my_clip = mp.VideoFileClip(self.uploaded_vid)
        my_clip.write_videofile(f'D:/College/EPICS/captiontesting/{self.name}/{self.input_file}')
        audio_file_path=f"D:/College/EPICS/captiontesting/{self.name}/{self.audio_file}"
        my_clip.audio.write_audiofile(audio_file_path)
        print("Starting Transcription")
        self.result=model.transcribe(audio_file_path,task='translate',fp16=False)
        self.untranslated=self.result['text']
        self.language=""
        self.translated=""
        print("Transcription done successfully!")
    def find_language(self):
        temp=whisper.load_audio(f"D:/College/EPICS/captiontesting/{self.name}/{self.audio_file}")
        test1=Transcriptor(temp)
        self.language=test1.detect_language()
    def convert_to_tamil(self):
        if self.language=="ta":
            print("Already in Tamil")
        else:
            self.language="ta"
            self.translated=GoogleTranslator(source="en", target="ta").translate(self.untranslated)
    def caption(self):
        name=self.name
        input_file=self.input_file
        dict1 = {'start':[], 'end':[], 'text':[]}
        for i in self.result['segments']:
            dict1['start'].append(int(i['start']))
            dict1['end'].append(int(i['end']))
            dict1['text'].append(GoogleTranslator(source="en", target="ta").translate(i['text']))
        captions=dict1
        cap = cv2.VideoCapture(self.uploaded_vid)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f'D:/College/EPICS/captiontesting/{self.name}/{self.output_name}', fourcc, fps, (width, height))
        font_path = r"C:\Users\Kartik Bapna\EPICS\Latha.ttf"
        font = ImageFont.truetype(font_path, size=20)
        caption_index = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000        
            if caption_index >= len(captions['start']):
                break    
            caption_start = captions['start'][caption_index]
            caption_end = captions['end'][caption_index]        
            if current_time >= caption_start and current_time < caption_end:
                text = captions['text'][caption_index]
                text_image = Image.new('RGBA', (1000, 100), color=(0, 0, 0, 0))
                text_draw = ImageDraw.Draw(text_image)
                text_draw.text((0, 0), text, font=font, fill=(255, 255, 255, 255))
                frame = Image.fromarray(frame)
                frame.paste(text_image, (50, height - 150), text_image)
                frame = np.array(frame)
            elif current_time >= caption_end - 1:
                caption_index += 1
            out.write(frame)
        cap.release()
        out.release()
        audio_file = f'D:/College/EPICS/captiontesting/{self.name}/{self.audio_file}'
        ffmpeg_extract_audio(self.uploaded_vid, audio_file)
        video_clip = VideoFileClip(f'D:/College/EPICS/captiontesting/{self.name}/{self.output_name}')
        audio_clip = AudioFileClip(audio_file)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(f'D:/College/EPICS/captiontesting/{self.name}/captioned_{self.output_name}', codec='libx264', audio_codec='aac')
        video_clip.close()
        audio_clip.close()


# In[4]:


ct2=Custom_Translator()


# In[5]:


ct2.caption()


# In[ ]:




