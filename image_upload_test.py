import gradio as gr
import firebase_admin
from firebase_admin import credentials, storage, db
import os
import tempfile
from datetime import datetime
import base64

import openai
from PIL import Image
import io
import requests
import json
import re

# Set your OpenAI API key
openai.api_key = ""

# Initialize Firebase
cred = credentials.Certificate("nsbs-first-firebase-adminsdk-z4rr4-ae523c4d88.json")
#cred2 = credentials.Certificate("nsbs-first-firebase-adminsdk-z4rr4-ae523c4d88.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'nsbs-first.appspot.com',
'databaseURL':'https://nsbs-first-default-rtdb.firebaseio.com/'
})

#firebase_admin.initialize_app(cred2, {'databaseURL':'https://nsbs-first-default-rtdb.firebaseio.com/'})

dir = db.reference()
bucket = storage.bucket()

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_image(image_path):
    # Convert image to bytes
    # Getting the base64 string
    image = Image.open(image_path)

    base64_image = image_to_base64(image)

    # Step 2: OCR using OpenAI API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "can you OCR this image? only response OCR Result please. Don't add 'OCR Result:' text"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 2000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json()['choices'][0]['message']['content'])
    ocr_text = response.json()['choices'][0]['message']['content']

    # Step 3: Output OCR Text
    print("OCR Text:", ocr_text)

    # Step 4: Analyze OCR Text and create a new question
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a helpful assistant that creates new multiple-choice questions based on given text. and give an answer, multiple-choices and solution the question. and don't response any other say. only response question, answer, multiple-choices and solution as json format. when you response json format, please use double quotes carefully by json rules. the multiple choices is use ① ② ③ ④ ⑤ "
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": 'Create a new multiple-choice question and answer similar to below one. and then make solution about your maked question. response format is json like this {"question": , "answer": , "multiple-choices":, "solution": } \n\n'+ocr_text
                    }
                ]
            }
        ],
        "max_tokens": 2000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json()['choices'][0]['message']['content'])
    new_question = response.json()['choices'][0]['message']['content']
    match = re.search(r'{.*}', new_question, re.DOTALL)
    print(match)
    if match:
        # Extract the matched JSON string
        json_str = match.group(0)
        print(json_str)

        # Attempt to parse the JSON string
        try:
            # Convert single quotes to double quotes for JSON compatibility
            json_str = json_str.replace("'", '"')
            json_data = json.loads(json_str)
            return json_data, ocr_text
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
            return None, None
    else:
        print("No JSON found")
        return None, None

    # Parse the new question and choices
    #json_dict = json.loads(new_question)
    question = ""
    choices = []
    answer = ""


    #return json_dict, ocr_text


def get_base64(original_string):
    # Convert the string to bytes
    string_bytes = original_string.encode('utf-8')

    # Encode the bytes to Base64
    base64_bytes = base64.b64encode(string_bytes)

    # Convert the Base64 bytes back to a string
    base64_string = base64_bytes.decode('utf-8')

    return base64_string


def get_ntp_created():
    return int(datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3])

def upload_image(image, id_text):
    if image is not None:
        # Generate a unique filename
        print(image)
        print(os.path.basename(image))
        file_name, file_ext = os.path.splitext(os.path.basename(image))
        filename = f"{file_name}__{os.urandom(8).hex()}{file_ext}"
        # Save the image locally
        #image.save(filename)
        
        # Upload to Firebase Storage
        blob = bucket.blob(filename)
        blob.upload_from_filename(image)
        
        # Make the blob publicly accessible
        blob.make_public()

        dir.update({f"{id_text}/{get_base64(filename)}":{"image_name":file_name+file_ext}})
        
        # Remove the local file
        #os.remove(filename)

        print("test process image")
        json_dict, ocr_text = process_image(image)

        dir.update({f"{id_text}/{get_base64(filename)}":
                        {"ocr_text":ocr_text, "question_text":json_dict["question"],
                         "choice1":json_dict["multiple-choices"]["①"],
                         "choice2": json_dict["multiple-choices"]["②"],
                         "choice3": json_dict["multiple-choices"]["③"],
                         "choice4": json_dict["multiple-choices"]["④"],
                         "choice5": json_dict["multiple-choices"]["⑤"],
                         "solution":json_dict["solution"], "answer":json_dict["answer"]}})


        return f"Image uploaded successfully. URL: {blob.public_url}"
    return "No image uploaded"

def list_images():
    blobs = bucket.list_blobs()
    #print(blobs)
    return gr.Dropdown(choices=[str(blob.name) for blob in blobs])

def display_image(image_name):
    if image_name:
        blob = bucket.blob(image_name)
        _, temp_local_filename = tempfile.mkstemp()
        
        # Download the file to a temporary location
        blob.download_to_filename(temp_local_filename)
        
        return temp_local_filename
    return None

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Image Upload and Display")
    
    with gr.Tab("Upload"):
        id_text = gr.Textbox(label="input user id")
        with gr.Row():
            input_image = gr.Image(type="filepath")
            output_text = gr.Textbox()
        upload_button = gr.Button("Upload")
        upload_button.click(fn=upload_image, inputs=[input_image, id_text], outputs=output_text)
    
    with gr.Tab("View Uploads"):
        with gr.Row():
            image_list = gr.Dropdown(label="Select an image", choices=[], allow_custom_value=True)
            output_image = gr.Image()
        refresh_button = gr.Button("Refresh List")
        refresh_button.click(fn=list_images, outputs=image_list)
        image_list.select(fn=display_image, inputs=image_list, outputs=output_image)

    # Update the image list when the page loads
    demo.load(fn=list_images, outputs=image_list)

# Launch the server
demo.launch(server_name="0.0.0.0", server_port=8080)