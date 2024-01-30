"""
[OpenAI-API-2_text+image.py]
Purpose: Correct Ask Directory or select file.
Author: Meng-Chi Ed Chen
Date: 2023-11-07
Reference:
    1. 
    2.

Status: Complete.
"""


#[1] Import library.
import OpenAI_API_0_module as oaapi #type: ignore
openai_api_key = 'your-openai-api-key'  #  Put your API key here.

#[] Read question from txt file
path_txt, basename_txt = oaapi.tkinter_select_file(dialog_title = 'Choose a question .txt file')
question_content = oaapi.read_text_from_txt(path_txt, 300)
path_image, basename_image = oaapi.tkinter_select_file(dialog_title = 'Choose a image file')


#[] Assign model and API key
model_name = 'gpt-4-vision-preview'
reply = oaapi.OpenAI_GPT_API_image_path(model_name
                                        , openai_api_key
                                        , question_content
                                        , path_image
                                        , additional_info=1)
oaapi.append_text_to_txt(path_txt, reply, 300)
print('[Complete]')
message = 'Do you want to open the txt file and close the program?'
oaapi.do_you_want_to_open_txt(message, path_txt)
