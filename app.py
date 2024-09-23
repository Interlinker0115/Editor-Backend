from flask import Flask, request, jsonify, redirect, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime

from pdfdomd import doc_to_pdf, pdf_to_html
from htmlcontrol import html_control
# from web_driver import creat_driver

# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


config = load_dotenv(override=True)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class DocumentSuggestions(BaseModel):
    isTrue: str = Field(description="If all paragraph is good, true, if not, false")
    tags: str = Field(description="the list of text content string of the identified origin tags")
    reasons: str = Field(description="reason list according to the identified tags")

# Initialize the JSON output parser
document_parser = JsonOutputParser(pydantic_object=DocumentSuggestions)

class DocumentSuggestions(BaseModel):
    isTrue: str = Field(description="If all paragraph is good, true, if not, false")
    tags: str = Field(description="the list of text content string of the identified origin tags")
    reasons: str = Field(description="reason list according to the identified tags")

document_parser = JsonOutputParser(pydantic_object=DocumentSuggestions)

document_prompt = PromptTemplate(
    template="""
    As a publication checker, your task is to identify all unfinished or coherence lack paragraphs from the document. 
    You should focus on checking paragraphs enclosed within <div> and <li> tags, while ignoring any table, image, or math related tags present in the document.
    Please identify the unfinished or  seriously logic incomplete paragraphs(tags) and make the reason of this.
    you should allow some minor errors.
    you must ignore all math related errors and html tag related erros.
    you must ignore this error: 'The paragraph is incomplete and ends abruptly.'
    reasons must be spanish.
    This is example outputs:
    "isTrue": "true", "tags": [], "reasons": [],
    "isTrue": "false", "tags": ["example text content of the tag"], "reasons": ["your reason"]
    "isTrue": "false", "tags": ["example text content of the tag", "example text content of the tag"], "reasons": ["your reason", "your reason"]
    You muse use your own creative word for reason.
    This is the html string of the paper: {content}
    {format_instructions}
    """,
    input_variables=["content"],
    partial_variables={"format_instructions": document_parser.get_format_instructions()},
)
document_chain = document_prompt | model | document_parser


app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '<h1 style="text-align: center">Welcome to Adlyceum</h1>'
# Directory where uploaded files will be stored
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# driver = creat_driver()

@app.route('/filetohtml', methods = ['POST'])
def pdftohtml():
    try:
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'file' not in request.files:
                return "there is no file"
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return redirect(request.url)
            if file:
                # Check if the folder exists before deleting
                if os.path.exists(UPLOAD_FOLDER):
                    # Delete the uploads folder
                    shutil.rmtree(UPLOAD_FOLDER)
                else:
                    print("Upload Folder does not exist")
                # Format the current time as a string (e.g., "20240324190456")
                folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
                new_dir_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                # Create the directory (including any necessary intermediate directories)
                os.makedirs(new_dir_path, exist_ok=True)
                filename = secure_filename(file.filename)
                print('filename-->', filename)
                pdf_path = os.path.join(new_dir_path, filename)
                file.save(pdf_path)
                
                file_type = filename.split(".")[-1]
                # if file_type == "html":
                #     pdf_path = htmltopdf(pdf_path)
                
                if file_type != "pdf":
                    try:
                        #if document is doc, docx or rft, convert this document to pdf file
                        pdf_path = doc_to_pdf(pdf_path)
                    except: return "Invalid type of file"
                    
                # return "File converted to HTML successfully!"
                    
                #convert pdf file to html file(.html)
                html_path = pdf_to_html(pdf_path)
                #convert loaded html file to well structured html file and add a style to html file
                converted_html_path = pdf_path.replace(".pdf", ".html")
                print(converted_html_path,"-------->")
                output = html_control(html_path)
                print(output,"----->output")
                #  send final converted html file to frontend
                return send_file(output, as_attachment=True)
    except:
        return('server error')
    
@app.route('/documentCheck', methods = ["POST"])
def documentCheck():
    # try:
    data = request.get_json()
    # print(data,"----data")
    # print(type(data))
    # content = data.get("content")
    result = document_chain.invoke({"content": data})
    # print(result)
    return result
    
    # except KeyError as e:
    #     return f"KeyError: {str(e)}"
    # except Exception as e:
    #     return f"there: {str(e)}"
    
                     


if __name__ == "__main__":
    app.run(debug=True)