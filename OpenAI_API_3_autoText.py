"""
[OpenAI-API-1_text.py]
Purpose: Correct Ask Directory or select file.
Author: Meng-Chi Ed Chen
Date: 2023-11-07
Reference:
    1. 
    2.

Status: Complete.
"""

#[1] Import library.
import sys
import OpenAI_API_0_module as oaapi #type: ignore
openai_api_key = 'your-openai-api-key'  #  Put your API key here.
max_loop = 10 # The program will run for 10 times before we need to start it again.



for loop in range(1, max_loop + 1):
    print(f'[Question Round {loop}]')
    path_txt = oaapi.q1_new_file_or_followup()
    #[2] Read question from txt file.
    question_content = oaapi.read_text_from_txt(path_txt = path_txt, 
                                                char_preview = 300)
    #[3] Assign model. View more model and pricing here: https://openai.com/pricing
    model_name = 'gpt-4-1106-preview'
    #model_name = "gpt-3.5-turbo"
    reply = oaapi.OpenAI_GPT_API_short(model_name = model_name
                                    , openai_api_key = openai_api_key
                                    , question_content = question_content
                                    , temperature = 0.9)
    oaapi.append_text_to_txt(path_txt = path_txt
                            , text_to_append = reply
                            , char_preview = 300)
    print('[Complete]')
    oaapi.open_txt(path_txt)
    #path_txt = oaapi.q3_ask_the_next_question(path_txt)



