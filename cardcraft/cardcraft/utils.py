import fitz  
from dotenv import load_dotenv
from openai import OpenAI
from xhtml2pdf import pisa 
import re
import json
import os
import tempfile


def openAIRequest(filepath):
    pdf = fitz.open(filepath)
    text = ""
    for page_num in range(pdf.page_count):
        page = pdf[page_num]
        text += page.get_text()
    pdf.close()

    query = f"""Using the following text data, make a series of question/answer pairs that cover all of the given material within the text data. Format them as a JSON object where each key is "question-x" and "answer-x". Here is the text data to pull these from: {text}"""

    load_dotenv()
    
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": query}
        ]
    )

    cleaned_response = completion.choices[0].message.content
    try:
        # Directly parse the response to ensure it's valid JSON
        response_json = json.loads(cleaned_response)
        return response_json  # Return the parsed JSON object
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None  # Or handle the error as needed




def buildCardSetFile(text, username, cardsetName):
    with open("cardset.html", "r") as file:
        html_template = file.read()

    flashcard_data = json.loads(text)

    flashcard_content = ""
    for key, value in flashcard_data.items():
        question = value['question']
        answer = value['answer']
        flashcard_content += f"<div class=\"row\"><div class=\"question\"><h3>Question:</h3><p>{question}</p></div><div class=\"answer\"><h3>Answer:</h3><p>{answer}</p></div></div>"

    # Combine the HTML template and flashcard content
    html_content = html_template.replace("<!-- Flash cards added here -->", flashcard_content)
    html_content = html_content.replace("<!-- send username in footer -->", f'<p>Username: {username}</p>')
    html_content = html_content.replace("<!-- send cardset name -->", f"<h1>{cardsetName}</h1>")
    print("html_content: " + html_content)

    pdf_file_path = "flashcards.pdf"
    with open(pdf_file_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)

    return pdf_file_path