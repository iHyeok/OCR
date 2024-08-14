import gradio as gr
import openai
from PIL import Image
import io
import base64
import requests

# Set your OpenAI API key
openai.api_key = ""

# Function to encode the image
def encode_image(image):
  #with open(image_path, "rb") as image_file:
  return base64.b64encode(image.read()).decode('utf-8')

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def process_image(image):
    # Convert image to bytes
    # Getting the base64 string
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
              "text": "You are a helpful assistant that creates new multiple-choice questions based on given text. and give an answer the question. and don't response any other say. only response question and answer. the multiple choices is use ① ② ③ ④ ⑤ "
            }            
          ]
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": f"Create a new multiple-choice question and answer similar to below one. the answer response is last line add blank line between question and answer. answer format is *Answer*:② \n\n{ocr_text}."
            }            
          ]
        }
      ],
      "max_tokens": 2000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json()['choices'][0]['message']['content'])
    new_question = response.json()['choices'][0]['message']['content']

    # Parse the new question and choices
    lines = new_question.strip().split('\n')
    question = ""
    choices = []
    answer = ""
    for line in lines:
        if '*Answer*' in line:
            answer = line.split(':')[1].replace(" ","")
        elif '①' in line:
            choices.append(line)
        elif '②' in line:
            choices.append(line)
        elif '③' in line:
            choices.append(line)
        elif '④' in line:
            choices.append(line)
        elif '⑤' in line:
            choices.append(line)
        
        else:
            question += line
            question += '\n'
            

    return ocr_text, question, choices, answer

def check_answer(choice, answer):
    # Assume the first choice is always correct for this example
    print(choice, answer)
    if choice is None:
        return "Select the Choice"
    return "Correct!" if answer in choice else "Incorrect. Try again!"

def gradio_interface(image):
    ocr_text, question, choices, answer = process_image(image)
    
    return gr.update(value=ocr_text), gr.update(value=question), gr.update(value=None, choices=choices, label="select Choice"), gr.update(value=answer)

def on_select(choice, answer):
    return check_answer(choice, answer)

with gr.Blocks() as demo:
    gr.Markdown("Upload an image of a multiple-choice English question")
    
    with gr.Row():
        image_input = gr.Image(type="pil")
        ocr_output = gr.Textbox(label="OCR Text")
    
    submit_btn = gr.Button("Process Image")
    
    new_question = gr.Textbox(label="New Question")
    multiple_choice = gr.Radio(label="select Choice")
    result_output = gr.Textbox(label="Result")
    
    answer_output = gr.Textbox(visible=False)
    
    submit_btn.click(gradio_interface, inputs=[image_input], outputs=[ocr_output, new_question, multiple_choice, answer_output])
    #new_question.change(on_select, inputs=[multiple_choice, answer_output], outputs=[result_output])
    multiple_choice.change(on_select, inputs=[multiple_choice, answer_output], outputs=[result_output])

demo.launch(share=True)