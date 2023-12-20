"""
[OpenAi-API-0_FuncBank.py]
Purpose: Correct Ask Directory or select file.
Author: Meng-Chi Ed Chen
Date: 2023-07-07
Reference:
    1. 
    2.

Status: Complete.
"""

import datetime
import sys, os, base64
import json, requests
from openai import OpenAI
import base64

#[1] Basic functions.


def datetime_string():
    #[] Get current datetime and create opening_of_append.
    now = datetime.datetime.now()       
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H%M%S")
    current_datetime = current_date + '_' + current_time
    return current_datetime

def tkinter_select_file(dialog_title = 'Open'):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title = dialog_title)
    print('file_path:', file_path)
    return file_path

def encode_image(image_path):
    import os
    # Check if the file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The file {image_path} does not exist.")
    # Extract the file extension
    _, file_extension = os.path.splitext(image_path)
    # Define acceptable image formats
    acceptable_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    # Check if the file is an acceptable image format
    if file_extension.lower() not in acceptable_formats:
        raise ValueError(f"Unsupported file format: {file_extension}. Please use one of the following formats: {', '.join(acceptable_formats)}")
    # If the file format is acceptable, proceed with encoding
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


#[2] Reading, saving, and handling txt files.

#[2-1] Read question from .txt file.
def read_text_from_txt(path_txt, char_preview):
    try:
        with open(path_txt, 'r') as file:
            content = file.read()
            print('[read_txt] content quick view:\n', content[:char_preview])
        return content
    except FileNotFoundError:
        print(f'[read_txt] File not found:\n {path_txt}')
        sys.exit()
    except Exception as e:
        print(f'[read_txt] An error occurred while reading the file:\n {str(e)}')
        sys.exit()

#[2-2] Append reply to .txt file and save.
def append_text_to_txt(path_txt, text_to_append, char_preview): # This code will not rename the file.
    #[] Check if the path_txt exists
    if not os.path.exists(path_txt):
        print(f'[append_txt] File not found:\n {path_txt}')
        sys.exit()
    #[] Get current datetime and create opening_of_append.
    current_datetime = datetime_string()
    opening_of_append = '\n\n--\n[' + current_datetime + ']\n\n'
    try:
        with open(path_txt, 'a') as file:  #a = append, w = write
            file.write(opening_of_append)
            file.write(text_to_append)
            print('[append_txt] content quick view:\n', text_to_append[:char_preview], '\n')
            file.close()
    except Exception as e:
        print(f'[append_txt] An error occurred while reading the file:\n {str(e)}')
        sys.exit()      




#[3] API functions

#[3-1] Ask text question. Used most frequent.
def OpenAI_GPT_API_short(model_name, openai_api_key, question_content, temperature):
    openai_api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "model": model_name,
        "messages": [{'role': 'user', 'content': question_content}],
        "temperature": temperature 
    }
    response = requests.post(openai_api_url, headers=headers, data=json.dumps(data))
    content = None
    if response.status_code == 200:
        response_data = response.json() 
        content = response_data["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text, sep='\n')
    return content

#[3-2] Ask text question. Use this if you prefer to include additional_info such as timestamp and token usage.
def OpenAI_GPT_API_long(model_callsigns, openai_api_key, question_content, temperature, additional_info=0):
    # API portle and header for autherization.
    openai_api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "model": model_callsigns,
        "messages": [{'role': 'user', 'content': question_content}],
        #"role" can be "system"(provide instructions or contextual information to the AI model) 
        # or "user"(normal human asking questions).
        "temperature": temperature 
        #"temperature" is the randomness of the response. 0 is very deterministic and 1 is very creative.
    }
    #[] Send the POST request to the OpenAI API
    response = requests.post(openai_api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        #[Dictionary] response_data were stored in a format of python dictionary with multiple "key:value" pairs.
        response_data = response.json() 
        content = response_data["choices"][0]["message"]["content"]
        if additional_info == 1:
            info_id = str(response_data["id"])
            info_object = str(response_data["object"])
            info_created = str(datetime.datetime.utcfromtimestamp(response_data["created"]))
            info_model = str(response_data["model"])
            usage_prompt = str(response_data["usage"]["prompt_tokens"])
            usage_completion = str(response_data["usage"]["completion_tokens"])
            usage_total = str(response_data["usage"]["total_tokens"])
            #[] Combine text (Change this part if you prefer other reporting format.)
            info_1st_row = '[ID | Object | Timestamp | Model]    ' + info_id + ' | ' + info_object + ' | ' + info_created + ' | ' + info_model  
            info_2nd_row = '[Token prompt | completion | total]  ' + usage_prompt + ' | ' + usage_completion + ' | ' + usage_total
            content = info_1st_row + '\n' + info_2nd_row + '\n\n' + content + '\n'
        print('[Response preview]\n', str(content)[:200])
    else:
        print("Error:", response.status_code, response.text, sep='\n')
    return content


#[3-3] Ask text and image question.
def OpenAI_GPT_API_image_path(model_callsigns, openai_api_key, question_content, path_image, additional_info):
    base64_image = encode_image(path_image)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    payload = {
        "model": model_callsigns,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if additional_info == 1:
            info_id = str(response_data["id"])
            info_object = str(response_data["object"])
            info_created = str(datetime.datetime.utcfromtimestamp(response_data["created"]))
            info_model = str(response_data["model"])
            usage_prompt = str(response_data["usage"]["prompt_tokens"])
            usage_completion = str(response_data["usage"]["completion_tokens"])
            usage_total = str(response_data["usage"]["total_tokens"])
            #[] Combine text
            info_1st_row = '[ID | Object | Timestamp | Model]    ' + info_id + ' | ' + info_object + ' | ' + info_created + ' | ' + info_model  
            info_2nd_row = '[Token prompt | completion | total]  ' + usage_prompt + ' | ' + usage_completion + ' | ' + usage_total
            content = info_1st_row + '\n' + info_2nd_row + '\n\n' + content + '\n'
    else:
        print("Error:", response.status_code, response.text, sep='\n')
        content = None

    return content



