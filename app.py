import os
import time
import gradio as gr
import base64
import requests
import json

from openai import OpenAI

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise EnvironmentError("API key for OpenAI not found in environment variables.")

shopper_assistant_client = OpenAI(api_key=api_key)

shopper_assistant_client.log = "debug"
def analyse_image(base64_image):
    response = shopper_assistant_client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are a professional shopping assistant with expertise in identifying products from images. Analyze the provided image and perform the following tasks:"},
                    {"type": "text", "text": "1. Identify and list all products shown in the image, including detailed descriptions."},
                    {"type": "text", "text": "2. Recognize and include brand names where applicable."},
                    {"type": "text", "text": "3. Describe the shape and fabric/material of each product."},
                    {"type": "text", "text": "4. Provide associated search queries for Google Shopping that include these details to improve search accuracy."},
                    {"type": "text", "text": "Your goal is to give a comprehensive overview of the products in the image, making it easier for users to find similar items online."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
    max_tokens=300,
    )
    return response.choices[0].message.content

shopping_assistant = shopper_assistant_client.beta.assistants.create(
    name="Shopping Guide",
    instructions="As a Shopping Guide, you assist users in making informed purchasing decisions. You ask about their preferences, budget, and the type of product they are looking for, offering options that best match their criteria. You provide comparisons between products, highlighting features, advantages, and disadvantages. You are knowledgeable about a wide range of products and provide guidance on choosing the best option according to the user's needs. You maintain a friendly and helpful tone, ensuring the user feels supported throughout their decision-making process. Avoid suggesting products outside the user's budget or preferences. Instead, focus on finding the best fit within their specified parameters.",
    model="gpt-4-1106-preview",
    tools=[{
        "type": "function",
        "function": {
            "name": "search_google_shopping",
            "description": "Retrieve Google Shopping search results for a given query.",
            "parameters": {
                "type": "object",
                "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query for finding products on Google Shopping."
                }
                },
                "required": ["query"]
            }
        }
    }]
)

def get_products(query):
    api_key = os.getenv("SERPAPI")
    if not api_key:
        print("SERPAPI environment variable is not set.")
        return

    base_url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
        "gl": "CH" 
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        top_3_results = data.get("shopping_results", [])[:3]

        markdown_output = ""
        for result in top_3_results:
            title = result.get("title")
            price = result.get("price")
            link = result.get("link")
            image = result.get("thumbnail")
            markdown_output += f"- **Title:** [{title}]({link})\n"
            markdown_output += f"  - **Price:** {price}\n"
            markdown_output += f"  - **Link:** [View Product]({link})\n"
            markdown_output += f"  - **Image:** ![Image]({image})\n\n"
        return markdown_output
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return
 

conversation_thread = shopper_assistant_client.beta.threads.create()

def process_query(user_query, interaction_history):
    interaction_history=interaction_history
    user_message = shopper_assistant_client.beta.threads.messages.create(
        thread_id=conversation_thread.id,
        role="user",
        content=user_query
    )

    assistant_response = shopper_assistant_client.beta.threads.runs.create(
        thread_id=conversation_thread.id,
        assistant_id=shopping_assistant.id,
        instructions="The user needs help making a purchase decision."
    )

    while True:
        # Brief pause to allow processing
        time.sleep(0.5)

        # Checking the status of the assistant's response
        response_status = shopper_assistant_client.beta.threads.runs.retrieve(
            thread_id=conversation_thread.id,
            run_id=assistant_response.id
        )

        if response_status.status == 'requires_action':
            call_functions(response_status.required_action.submit_tool_outputs.model_dump(), assistant_response.id)
        
        if response_status.status == 'completed':
            response_messages = shopper_assistant_client.beta.threads.messages.list(
                thread_id=conversation_thread.id
            )
            
            data = response_messages.data
            final_response = data[0]
            content = final_response.content
            response = content[0].text.value
            return response

        else:
            continue


textbox = gr.Textbox(placeholder="input", container=False, scale=7)

def call_functions(required_actions, run_id):
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])

            if func_name == "search_google_shopping":
                output = get_products(arguments['query'])
                print(output)
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output 
                })
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        shopper_assistant_client.beta.threads.runs.submit_tool_outputs(
            thread_id=conversation_thread.id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )

def upload_file(file):
    file_path = file.name
    with open(file_path, 'rb') as file:
        file_content = file.read()
    
    encoded_content = base64.b64encode(file_content)
    product_list = analyse_image(encoded_content.decode('utf-8'))
    print(product_list)
    new_value = "The following products were found in this image:" + product_list

    return new_value, file.name

css = """
#chat {
    height:500px
}
#upload .unpadded_box {
    min-height: 50px;
}
"""


with gr.Blocks(css=css, title="Shopping Assistant") as demo:
    with gr.Row(elem_id = "chat"):
        with gr.Column():
            chat = gr.ChatInterface(
            textbox=textbox,
            fn=process_query,
            title="🛍️ Your Shopping Guide",
            undo_btn = None,
            stop_btn = None,
            retry_btn = None,
            clear_btn = None,
            )

    with gr.Row(elem_id = "upload"):
        with gr.Column():
            file_output = gr.File()
            upload_button = gr.UploadButton("Click to Upload a File", file_types=["image"], file_count="single", scale=0)
            upload_button.upload(upload_file, upload_button, outputs=[textbox, file_output])

if __name__ == "__main__":
    demo.launch()

