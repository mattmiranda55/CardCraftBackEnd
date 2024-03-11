import fitz  
from dotenv import load_dotenv
from openai import OpenAI

def openAIRequest(filepath):
    pdf = fitz.open(filepath)

    text = ""

    for page_num in range(pdf.page_count):
        page = pdf[page_num]
        text += page.get_text()
    
    pdf.close()

    query = """Using the following text data, make a series of question/answer pairs that cover all of the given material within the text data. 
            Format them as such in a Python dictionary: /{[ question-x: (question goes here), answer-x: (answer goes here) ]/}. Where x is the number of the question and 
            the corresponding answer. Here is the text data to pull these from: """ + text

    load_dotenv()
    
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": query}
        ]
    )

    return completion.choices[0].message.content

def buildCardSetFile(text):
    # use package vilkomir suggested
    pass