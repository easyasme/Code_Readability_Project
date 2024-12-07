# flask --app app.py --debug run


from flask import Flask, render_template, request, send_from_directory, redirect, url_for,send_file, abort
import streamlit as st
import socket
import os
from werkzeug.datastructures import FileStorage
from openpyxl import Workbook, load_workbook
from pyngrok import ngrok
from flask_ngrok import run_with_ngrok
# from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
import shutil
import re 
import string
import json
import PyPDF2
from io import BytesIO
import Levenshtein  
import openai
from openpyxl.utils import get_column_letter
from openpyxl.utils import column_index_from_string
from concurrent.futures import ThreadPoolExecutor
from PyPDF2 import PdfReader
import threading
import fitz
import os
import json
import pandas as pd
import pytesseract
from PyPDF2 import PdfReader
import csv
from urllib.parse import quote
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
import openai
from pdf2image import convert_from_path
from PIL import Image
import tabula
from manual_test import statement_to_xlsx
from manual_test import count_exported_csv_files,delete_exported_csv_files,extract_numbers_from_string,delete_temp_files
from manual_test import statement_to_csv, get_exported_files, run_ocr_to_csv, run_ocr_to_csv_multiple_times,improve_text_structure
from manual_test import generate_explanation,delete_thumbnails,pdf_to_csv_conversion,extract_text_from_page,convert_page_to_image,process_pdf
import ast
import PyPDF2
import signal
import sys
# from PyPDF2 import PdfFileMerger


app = Flask(__name__, static_url_path='/static')
run_with_ngrok(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
UPLOAD_FOLDER = os.path.join('static', 'img_photo')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# from current chatgpt4 openapi API key access
# open.api_key = "${{ secrets.OPENAI_KEY }}"
# open.api_key = "${os.getenv('api_key')}"
# open.api_key = os.environ['api_key']
openai.api_key = os.environ['api_key']
auth_token = os.environ['auth_token']

# port_no=5000
# public_url = ngrok.connect(port_no).public_url
# print('accessing global link, click: ',public_url)

current_dir = os.getcwd()

# global variables for transferring important terms
global_excel_file = None
exported_files = None
partners = {}

@app.route('/favicon.ico')
def favicon():
    abort(404)

# def run_ngrok():
#     auth_token = os.environ['api_key']
#     port_no=5000
#     public_url=ngrok.connect(port_no).public_url

@app.route('/failed')
def failed():
    return render_template('failed.html')



def configure():
    load_dotenv()

# @app.route('/are_you_sure')
# def are_you_sure():
    
#     output_dir = os.path.join(current_dir, 'output')
#     count = count_exported_csv_files(current_dir+'/output/')
    
#     output_dir = os.path.join(current_dir, 'output')

#     count = count_exported_csv_files(output_dir)
    
#     # opening each csv file for the user to check
#     for file_index in range(count):
#         file_name = f'exported{file_index}.csv'
#         file_path = os.path.join(output_dir, file_name)
#         os.system(f'open {file_path}') 

#     # deleting thumbnail images for a cleaner directory
#     delete_thumbnails()
#     global exported_files
#     exported_files = get_exported_files()

#     global global_excel_file
#     print('GLOBAL EXCEL FILE:',global_excel_file)
#     flag = True if global_excel_file=='uploads/' else False
#     # rendering are_you_sure html with the exported files included for the user to either re-extract or not
#     return render_template('are_you_sure.html',exported_files=exported_files,excel_file=flag)

@app.route('/are_you_sure')
def are_you_sure():
    output_dir = os.path.join(current_dir, 'output')
    count = count_exported_csv_files(output_dir)

    # List to store download links for CSV files
    download_links = {}

    for file_index in range(count):
        file_name = f'exported{file_index}.csv'
        file_path = os.path.join(output_dir, file_name)
        
        # appending download link for the CSV file
        # download_link = f'/download/{file_name}'
        download_link = '/download/'+file_name
        download_links[file_name] = download_link
    print('DOWNLOAD LINKS: ',download_links)
    # deleting thumbnail images for a cleaner directory
    delete_thumbnails()

    exported_files = get_exported_files()
    print('download_links: ',download_links)
    # Zip exported_files and download_links together
    # files_with_links = zip(exported_files, download_links)
    sorted_download_links = dict(sorted(download_links.items()))
    print('sorted download links: ',sorted_download_links)
    # determining if an excel file was uploaded
    flag = True if global_excel_file == 'uploads/' else False
    # sorted_files_with_links = sorted(list(files_with_links), key=lambda x: x[0])
    # print('files with links: ',files_with_links)
    return render_template('are_you_sure.html', files_with_links=sorted_download_links, download_links=download_links, exported_files=exported_files, excel_file=flag)

@app.route('/download/<filename>')
def download_file(filename):
    output_dir = os.path.join(current_dir, 'output')
    file_path = os.path.join(output_dir, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/run_extract', methods=['POST'])
def run_extract():
    selectedFiles = request.form.getlist('files_to_include')
    print('SELECTED FILES FOR REEXTRACTION: ', selectedFiles)

    global partners
    global exported_files
    each_results_per_page = {}
    
    for x in selectedFiles:
        
        original_image_text = pytesseract.image_to_string(Image.open(partners[x]))
        page_number = extract_numbers_from_string(x)
        temp_page_number=extract_numbers_from_string(partners[x])
        
        results = run_ocr_to_csv_multiple_times(original_image_text, temp_page_number,num_iterations=6)
        each_results_per_page[page_number] = results[1]
        
    for key,value in each_results_per_page.items():
        # re-extract selected pdf files to csv
        statement_to_csv(value['csv_data'],key)
    return are_you_sure()
    

@app.route('/run_again', methods=['POST'])
def run_again():
    # if request.method == 'POST':
    textarea_content = request.form.get('dictionaryTextbox')  
    
    
    # find indexes
    start_index = textarea_content.find('{')
    end_index = textarea_content.rfind('}')
    dictionary_str = textarea_content[start_index:end_index+1]

    # parsing the string and making it into a dictionary
    my_dict = ast.literal_eval(dictionary_str.strip())
    
    count = count_exported_csv_files(current_dir+'/output/')
    the_url = transfer_to_excel(count,my_dict)
    
    delete_exported_csv_files(current_dir+'/output/')
    delete_temp_files()
    
    # source_file = 'uploads/new_version.xlsx'
    # destination_file = os.path.join(current_dir, 'output', 'new_version.xlsx')

    # shutil.copyfile(source_file, destination_file)

    return render_template('complete.html',download_link=the_url)

@app.route('/go_back',methods=['POST'])
def back_to_home():
    # clear variables and extracted files
    delete_exported_csv_files(current_dir+'/output/')
    delete_temp_files()
    delete_thumbnails()
    
    # redirect back to the main page
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    
    global global_excel_file
    global selected_results
    pdf_text = None
    search_words = None

    if request.method == 'POST':
        if request.files['file'].filename != '':
            
            file = request.files['file']
            second_file = request.files['second_file']

            # global_excel_file = request.files['excel_file']
            # temp_filename = 'new_version.xlsx'
            # global_excel_file = str('output/')+str(global_excel_file.filename)
            global_excel_file = str('output/')+'new_version.xlsx'
            # global_excel_file = str('uploads/')+temp_filename
            
            if file.filename == '':
                return render_template('index.html', error='No selected file')


            search_words = request.form.get('search_words')
            if not search_words:
                return render_template('index.html', error='Please enter search words')
            

            pdf_text = process_pdf(file,second_file,search_words)

            selected_results = []  #reset

    return render_template('index.html', pdf_text=pdf_text, search_words=search_words)


@app.route('/view_pdf', methods=['POST'])
def view_pdf():
    if 'bs_file' in request.files:
        bs_file = request.files['bs_file']
        # Save the uploaded PDF file temporarily
        pdf_path = 'temp.pdf'
        bs_file.save(pdf_path)
        # process_pdf_bs(pdf_path)
        image_paths_b = []
        each_results_per_page_b = []
        global partners
        # Open the PDF file
        with open(os.path.join(current_dir,'temp.pdf'), 'rb') as pdf_file:
            
            pdf_reader = PdfReader(pdf_file)
            
            # getting the number of pages in the PDF file
            num_pages = pdf_reader.numPages
            print("Number of pages:", num_pages)
        # pdf_to_csv_conversion('temp_pdf.pdf',num_pages)
        
            for i in range(num_pages):
                
                pdf_reader = PdfReader(pdf_file)

                # converting pdf to image
                images = convert_from_path(pdf_file.name, first_page=i, last_page=i, single_file=True)
                print("IMAGES: ",images)
                print("pdf_file.NAME: ",pdf_file.name)
                
                image = images[0]

                image_path = os.path.join(current_dir, f"bank_statement_page{i}.png")
                image.save(image_path)
                


                # pdf_to_csv_conversion(pdf_path,i)
                # image_path = os.path.join(current_dir, f"bank_statement_page{i}.png")

                # performing OCR on the image
                image_paths_b.append(image_path)
                original_image_text = pytesseract.image_to_string(Image.open(image_path))
                partners['exported'+str(i)+'.csv'] = image_path

                # # running conversion multiple times for each result
                results = run_ocr_to_csv_multiple_times(original_image_text, i,num_iterations=6)
                
                each_results_per_page_b.append(results[1])
            for x in range(len(each_results_per_page_b)):
                statement_to_csv(each_results_per_page_b[x]['csv_data'],x)
            
        
    return are_you_sure()



@app.route('/extract', methods=['POST'])
def extract_csv():
    # search_words = request.form.get('search_words')
    selected_results = request.form.getlist('selected_results[]')
    if not selected_results:
        return "No results selected for CSV extraction"
    each_results_per_page = []
    image_paths = []
    global partners
    for i in range(len(selected_results)):
        image_path = os.path.join(current_dir, f"temp_page_{selected_results[i]}.png")

        # performing OCR on the image
        image_paths.append(image_path)
        original_image_text = pytesseract.image_to_string(Image.open(image_path))
        partners['exported'+str(i)+'.csv'] = image_path

        # # running conversion multiple times for each result
        results = run_ocr_to_csv_multiple_times(original_image_text, selected_results[i],num_iterations=6)
        
        each_results_per_page.append(results[1])
    
    for x in range(len(each_results_per_page)):
        statement_to_csv(each_results_per_page[x]['csv_data'],x)
    
    return are_you_sure()


def transfer_to_excel(each_results_per_page,dictionary):
    print("EACH RESULTS PER PAGE: ",each_results_per_page)
    for x in range((each_results_per_page)):
        try:
            with open(current_dir+'/output/exported'+str(x)+'.csv', 'r') as file:
                csv_data = file.read()
                the_url=statement_to_xlsx(csv_data,global_excel_file,dictionary)
        
        except:
            return failed()
    # return "CSV extraction successful"
    return the_url

@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_dir, 'static', 'images'), filename)

def send_url():
    return public_url

# if __name__ == '__main__':
#     app.run()

if __name__ == '__main__':
# print('accessing global link, click: ',public_url)
    # app.run(port=port_no)
    # Define the URL of your Flask app
    # flask_app_url = public_url
    app.run(port=80)
    
    # st.markdown(f'<iframe src="{flask_app_url}" width="100%" height="1000px" scrolling="yes"></iframe>', unsafe_allow_html=True)