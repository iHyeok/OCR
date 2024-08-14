import gradio as gr
import firebase_admin
from firebase_admin import credentials, storage
import os
import tempfile

# Initialize Firebase
cred = credentials.Certificate("nsbs-first-firebase-adminsdk-z4rr4-ae523c4d88.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'nsbs-first.appspot.com'
})

bucket = storage.bucket()

def upload_image(image):
    if image is not None:
        # Generate a unique filename
        print(image)
        filename = f"uploaded_image__{os.urandom(8).hex()}.jpg"
        
        # Save the image locally
        image.save(filename)
        
        # Upload to Firebase Storage
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Remove the local file
        os.remove(filename)
        
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
        with gr.Row():
            input_image = gr.Image(type="pil")
            output_text = gr.Textbox()
        upload_button = gr.Button("Upload")
        upload_button.click(fn=upload_image, inputs=input_image, outputs=output_text)
    
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