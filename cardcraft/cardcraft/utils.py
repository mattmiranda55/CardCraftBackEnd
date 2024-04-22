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

    query = f"""Using the following text data, make a series of question/answer pairs that cover all of the given material within the text data. Format them as a JSON object where each key is "question-x" and "answer-x". Here is the text data to pull these from: {text}. Here is an example of how you should return things. ONLY RETURN JSON IN THIS FORMAT, and only json or it will break my application: {{
        "question-1": "What is the capital of France?",
        "answer-1": "Paris.",
        "question-2": "Who wrote the famous play 'Romeo and Juliet'?",
        "answer-2": "William Shakespeare.",
        "question-3": "What is the chemical symbol for water?",
        "answer-3": "H2O.",
        "question-4": "What is the tallest mountain in the world?",
        "answer-4": "Mount Everest.",
        "question-5": "Who painted the Mona Lisa?",
        "answer-5": "Leonardo da Vinci.",
        "question-6": "What is the currency of Japan?",
        "answer-6": "Japanese Yen.",
        "question-7": "What is the chemical symbol for gold?",
        "answer-7": "Au.",
        "question-8": "Who was the first person to step on the moon?",
        "answer-8": "Neil Armstrong.",
        "question-9": "Which planet is known as the 'Red Planet'?",
        "answer-9": "Mars.",
        "question-10": "What is the main ingredient in guacamole?",
        "answer-10": "Avocado.",
        "question-11": "Who is known as the father of modern physics?",
        "answer-11": "Albert Einstein.",
        "question-12": "What is the largest mammal in the world?",
        "answer-12": "Blue whale.",
        "question-13": "What is the national animal of Australia?",
        "answer-13": "Kangaroo.",
        "question-14": "Who is the author of 'Harry Potter' series?",
        "answer-14": "J.K. Rowling.",
        "question-15": "What is the chemical symbol for oxygen?",
        "answer-15": "O2.",
        "question-16": "What is the longest river in the world?",
        "answer-16": "Nile River.",
        "question-17": "Who painted the 'Starry Night'?",
        "answer-17": "Vincent van Gogh.",
        "question-18": "Which element is a primary component of the Earth's atmosphere?",
        "answer-18": "Nitrogen.",
        "question-19": "Who discovered penicillin?",
        "answer-19": "Alexander Fleming.",
        "question-20": "What is the smallest country in the world?",
        "answer-20": "Vatican City."
        }}"""

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

    print(text)


    flashcard_content = ""
    i = 1
    while f"question-{i}" in text:
        question = f"question-{i}"
        answer = f"answer-{i}"
        flashcard_content += f"<div class=\"row\"><div class=\"question\"><h3>Question:</h3><p>{text[question]}</p></div><div class=\"answer\"><h3>Answer:</h3><p>{text[answer]}</p></div></div>"
        i += 1

    # Combine the HTML template and flashcard content
    html_content = html_template.replace("<!-- Flash cards added here -->", flashcard_content)
    html_content = html_content.replace("<!-- send username in footer -->", f'<p>Username: {username}</p>')
    html_content = html_content.replace("<!-- send cardset name -->", f"<h1>{cardsetName}</h1>")
    print("html_content: " + html_content)

    pdf_file_path = f'{username}-{cardsetName}.pdf'
    with open(pdf_file_path, "w+b") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)

    return pdf_file_path