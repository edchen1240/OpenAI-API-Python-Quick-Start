"""
[OpenAi-API-0_FuncBank.py]
Purpose: Correct Ask Directory or select file.
Author: Meng-Chi Ed Chen
Date: 2023-07-07
Updates:
    1. 2024-03-11: Upgrade interation question to allow new topic, follow up, or the original select file.
    2.

Status: Complete.
"""

import sys, os, base64, tkinter, datetime, json, requests, subprocess, re, shutil
from tkinter import filedialog
from openai import OpenAI








#[1] Basic functions.




def datetime_stamp():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def datetime_filename():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m%d-%H%M")



#[2] Cool interaction questions.



def q1_new_file_or_followup():
    """
    [Opening question]
    """
    dt_file = datetime_filename()
    message = \
    f'Hello, how can I help you? {dt_file}\n\
    (a) Type a new name for the new topic. \n\
        This will create and open a new txt file named as "{dt_file}_Topic-1".\n\
    (b) Type "+" to followup with the latest question.\n\
        This will copy the latest txt file and create a "_n+1" version for it.\n\
    (c) Type nothing (just press enter) to choose an existing text file.\n'
    string_ques = input(message)
    if string_ques == '+':
        path_latest_txt = find_latest_txt()
        path_txt = increment_filename(path_latest_txt)
        basename_txt = os.path.basename(path_txt)
        print(f'--> (a) Followup the latest question: {basename_txt}')
        open_txt(path_txt)
        q2_let_me_know_when_question_is_ready(path_txt)
    elif string_ques == '':
        print('--> (b) Choose an existing question file.')
        path_txt, _ = tkinter_select_file(dialog_title = 'Choose an existing question file')
    else:
        print(f"--> (c) Let's start a new topic of {string_ques}.")
        filename = dt_file + '_' + string_ques + '_1.txt'
        path_txt = create_txt_file(filename)
        open_txt(path_txt)
        q2_let_me_know_when_question_is_ready(path_txt)
    return path_txt



def q2_let_me_know_when_question_is_ready(path_txt=""):
    basename_txt = os.path.basename(path_txt)
    message = (
        f"The file {basename_txt} has been created and is now open for you.\n"
        "Please save and close the program once you finish compiling the question.\n"
        "Press Enter to continue.\n"
    )
    _ = input(message)  # The input value is not used.
    print("The question is ready. Let's proceed.")





def q3_ask_the_next_question(path_txt):
    """
    Asks the user if they want to proceed with the next question.
    """
    open_txt(path_txt)
    message = (
        "The response has been saved and is now open for you. Would you like to ask the next question?\n"
        "To proceed, please close the text file and press Enter. I will then create a version incremented by one for you.\n"
        "To exit, simply close the program.\n"
    )
    _ = input(message)  # The input value is not used.
    print(f'Following up on this question: {path_txt}')
    path_txt = increment_filename(path_txt)
    open_txt(path_txt)
    message = (
        "A new file has been created and is open for you. Please let me know when you are ready.\n"
        "Type anything and press Enter to continue. To exit the program, press Enter without typing anything.\n"
    )
    _ = input(message)  # The input value is not used.
    print("The question is ready. Let's proceed.")
    return path_txt



#[2] Functions for cool interaction questions.


def filter_file_with_keywords(
    dir_folder, 
    list_keywords_select=None, 
    list_keywords_discard=None
    ):
    print('\n[filter_file_with_keywords]')
    if list_keywords_select is None:
        list_keywords_select = []
    if list_keywords_discard is None:
        list_keywords_discard = []
    # Check if directory exists
    if not os.path.isdir(dir_folder):
        raise FileNotFoundError(f"The directory '{dir_folder}' was not found.")
        sys.exit(1)
    # Get list of files in the directory
    list_file_names = [file for file in os.listdir(dir_folder)
                       if os.path.isfile(os.path.join(dir_folder, file))]
    # Filter names by keywords to select
    if list_keywords_select:
        list_file_names = [file for file in list_file_names 
                           if any(keyword in file for keyword in list_keywords_select)]
    # Filter names by keywords to discard
    if list_keywords_discard:
        list_file_names = [file for file in list_file_names 
                           if not any(keyword in file for keyword in list_keywords_discard)]
    # Generate file paths
    list_file_paths = [os.path.join(dir_folder, file) for file in list_file_names]
    # Print result
    print('--list_file_names:', list_file_names, end='\n\n')
    return list_file_paths, list_file_names






def find_latest_txt(dir=None):
    print('\n[find_latest_txt]')
    if dir is None:
        dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(dir, exist_ok=True)  # Ensure the directory exists.
    # Assuming filter_file_with_keywords returns a tuple of (list_of_full_paths, list_of_filenames)
    list_file_paths, list_file_names = filter_file_with_keywords(dir, list_keywords_select='.txt')
    # Now work with the full paths directly
    # Sort full paths by creation time, newest first
    list_file_paths.sort(key=lambda file_path: os.path.getctime(file_path), reverse=True)
    # Check if there are any .txt files
    if list_file_paths:
        # Get the most recently created file's path
        path_latest_txt = list_file_paths[0]  # Take the first element as it's the newest.
        print('--Latest .txt file: ', os.path.basename(path_latest_txt))
    else:
        print('--No .txt files found. Program exit.')
        path_latest_txt = None
        sys.esit()
    return path_latest_txt
    
    
    
    
def increment_filename(path_txt):
    """
    Increments the numerical part of a filename before the '.txt' extension.
    If the file is named 'example_1.txt', it will be changed to 'example_2.txt'.
    If no numerical part is found, '_1' will be added before the extension.
    Save a new cope of path_txt with a new filename in the same dir.
    """
    print('\n[increment_filename]')
    # Regular expression to find the "_{n}.txt" part of the filename
    pattern = re.compile(r"(_(\d+))\.txt$")
    # Search for the pattern in the filename
    match = pattern.search(path_txt)
    if match:
        # Extract the full matched pattern (_{n}) and the numerical part ({n})
        full_match, num_part = match.groups()
        # Increment the number
        num_incremented = int(num_part) + 1
        # Replace the original numerical part with the incremented value
        path_new_txt = path_txt.replace(full_match, f"_{num_incremented}")
    else:
        # If no numerical part is found, add '_1' before the '.txt' extension
        path_new_txt = path_txt.replace(".txt", "_1.txt")
    shutil.copy(path_txt, path_new_txt)
    print(f'--File created at: {path_new_txt}')
    return path_new_txt



def create_txt_file(path_txt, dir=None):
    """
    Create an empty .txt file at the specified directory (or in the current directory if not specified).
    Then open the txt file with the default system application for .txt files, and return the path to that file.
    """
    print('\n[create_txt_file]')
    if dir is None:
        dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(dir, exist_ok=True)  # Ensure the directory exists.
    path_txt = os.path.join(dir, path_txt)  # Create the full path for the file.
    # Create the file if it doesn't exist.
    with open(path_txt, 'w') as file:
        pass  # Just create the file, no need to write anything.
    print(f'--File created at: {path_txt}')
    return path_txt
    
    
    
def open_txt(path_txt):
    print('\n[open_txt]')
    # Open the file with the default application.
    if os.name == 'nt':             # For Windows
        os.startfile(path_txt)
    elif os.name == 'posix':        # For MacOS
        subprocess.run(['open', path_txt])
    else:                           # For Linux (xdg-open should work for most environments)
        subprocess.run(['xdg-open', path_txt])
    return path_txt




def tkinter_select_file(dialog_title='Select a file'):
    print('\n[tkinter_select_file]')
    root = tkinter.Tk() # Creat a window (or container) for tkinter GUI (Graphical User Interface) toolkit
    root.withdraw() # Hide the main window since we don't need to see it.
    try:
        file_path = filedialog.askopenfilename(title=dialog_title)
        if file_path:
            file_basename = os.path.basename(file_path)
            file_path = os.path.normpath(file_path) # Clean the path
            print('--file_path:', file_path)
            return file_path, file_basename
        else:
            print('--No file selected. Exit code.')
            sys.exit()
    except Exception as e:
        print(f'--An error occurred: {e}')
        return None, None
    finally:
        root.destroy() # Release resources.

def encode_image(image_path):
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
    print('\n[read_text_from_txt]')
    try:
        with open(path_txt, 'r') as file:
            content = file.read()
            print('--Start content quick view:\n', content[:char_preview], '\n--End content quick view.')
        return content
    except FileNotFoundError:
        print(f'--File not found:\n {path_txt}')
        sys.exit()
    except Exception as e:
        print(f'--An error occurred while reading the file:\n {str(e)}')
        sys.exit()

#[2-2] Append reply to .txt file and save.
def append_text_to_txt(path_txt, text_to_append, char_preview): # This code will not rename the file.
    #[] Check if the path_txt exists
    if not os.path.exists(path_txt):
        print(f'[append_txt] File not found:\n {path_txt}')
        sys.exit()
    #[] Get current datetime and create opening_of_append.
    current_datetime = datetime_stamp()
    opening_of_append = '\n\n--\n[' + current_datetime + ']\n\n'
    try:
        with open(path_txt, 'a') as file:  #a = append, w = write
            file.write(opening_of_append)
            file.write(text_to_append)
            print('[append_txt] content quick view:\n', text_to_append[:char_preview].replace('\n', '\n>> '), '\n')
            file.close()
    except Exception as e:
        print(f'[append_txt] An error occurred while reading the file:\n {str(e)}')
        sys.exit()      


# This function is no longer in use.
def do_you_want_to_open_txt(message, path_txt):
    message = message + ' [Y/N]'
    string_ques = input(message)
    string_ques = string_ques.lower()
    if ('yes' in string_ques) or ('ye' in string_ques) or ('y' in string_ques) or ('ok' in string_ques) \
        or ('sure' in string_ques) or ('go' in string_ques):
        print('User agreed to proceed.', string_ques)
        try:
            # Attempt to open the text file
            with open(path_txt, 'r') as file:
                print(f"Contents of {path_txt}:\n")
                print(file.read())
            # Exit the program after displaying the file content
            sys.exit()
        except FileNotFoundError:
            print(f"The file at {path_txt} was not found.")
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
    elif ('no' in string_ques) or ('n' in string_ques):
        print('User chose to stop.', string_ques)
        sys.exit()
    else:
        print('[Invalid Input] I will just keep moving on.\n', string_ques)








#[3] API functions

def check_API_key(openai_api_key):
    if openai_api_key == None or openai_api_key == 'put-your-api-key-here':
        print('--API key not provided. Please put your API key at "put-your-api-key-here" in the code. Exit program.')
        sys.exit(1)
    return


#[3-1] Ask text question. Used most frequent.
def OpenAI_GPT_API_short(model_name, openai_api_key, question_content, temperature):
    print('\n[OpenAI_GPT_API_short]')
    check_API_key(openai_api_key)
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
    #[] Send the POST request to the OpenAI API
    print('--Sending API request. Please wait for HTTP request-response cycle.\n')
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
    print('\n[OpenAI_GPT_API_long]')
    check_API_key(openai_api_key)
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
    print('--Sending API request. Please wait for HTTP request-response cycle.\n')    
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
    print('\n[OpenAI_GPT_API_image_path]')
    check_API_key(openai_api_key)
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
    #[] Send the POST request to the OpenAI API
    print('--Sending API request. Please wait for HTTP request-response cycle.\n')
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



