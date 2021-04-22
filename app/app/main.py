
import csv
import os
from os import path, read
import re
from fastapi import requests
import pandas as pd
import sys
from io import StringIO


import shutil
from typing import Optional
from fastapi import FastAPI, File, UploadFile
from fastapi.requests import Request
from fastapi.responses import Response, FileResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import pyodbc

from . import random_gen

app = FastAPI()
templates = Jinja2Templates(directory="app/templates/")

connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:todjord-db.database.windows.net,1433;Database=dsp_db;Uid=todjord;Pwd=20fvoqf:;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
conn = pyodbc.connect(connection_string)

csv.field_size_limit(sys.maxsize)

cursor = conn.cursor()

@app.get("/")
def index(
    request: Request,
    ):
    return templates.TemplateResponse('index.html', context={'request': request})

@app.get("/test_table")
def test_table(request: Request):
    
    create_query = '''
    DROP TABLE IF EXISTS test_table;
    CREATE TABLE test_table (
    id INT NOT NULL IDENTITY,
    first_name VARCHAR(60),
    last_name VARCHAR(60),
    address VARCHAR(60),
    phone_number VARCHAR(60),
    PRIMARY KEY (id)
    );
    '''
    cursor.execute(create_query)
    for i in range(5):
        first_name = f"'{random_gen.person_entry().first_name}',"
        last_name = f"'{random_gen.person_entry().last_name}',"
        address = f"'{random_gen.person_entry().address}',"
        phone_number = f"'{random_gen.person_entry().phone_number}'"

        insert_query = '''
        INSERT INTO test_table(first_name, last_name, address, phone_number) values(
        ''' + first_name + last_name + address + phone_number +''');
        '''
        cursor.execute(insert_query)

    query_all = '''SELECT * FROM test_table'''
    users = cursor.execute(query_all)

    return templates.TemplateResponse('test_table.html', context={
        'request': request,
        'users': users,
        })

@app.get("/dataset_browser")
async def datasets(
    request: Request
):
    query_tables = '''
    SELECT table_name [dbo]
    FROM INFORMATION_SCHEMA.TABLES
    WHERE table_type = 'BASE TABLE';
    '''
    tables = cursor.execute(query_tables).fetchall()

    return templates.TemplateResponse('dataset_browser.html', context={'request': request, 'tables': tables})

@app.get("/view_dataset")
async def view_dataset(
    request: Request,
    table_name
):
    columns_query = f'''SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}';'''
    query_all = f'''SELECT TOP 50 * FROM {table_name};'''
    

    columns = cursor.execute(columns_query).fetchall()
    data = cursor.execute(query_all)
    
    return templates.TemplateResponse('view_dataset.html', context={
        'request': request, 
        'data': data, 
        'columns': columns,
        'table_name': table_name})

@app.get("/view_dataset/download")
def test_table_download(table_name):

    query_all = f'''SELECT * FROM {table_name}'''
    columns_query = f'''SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{table_name}';'''
   
    

    if os.path.exists('app/csv/temp.csv'):
        os.remove('app/csv/temp.csv')

    columns = cursor.execute(columns_query)
    headers = []
    for column in columns:
        headers.append(column[0])
    with open('app/csv/temp.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headers)

    data = cursor.execute(query_all)
    with open('app/csv/temp.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        row_list = []
        for row in data:
            row_list = []
            for cell in row:
                row_list.append(cell)
            writer.writerow(row_list)
    
    file.close()
            
    return FileResponse(path='app/csv/temp.csv', filename=f'{table_name}.csv')

@app.get("/upload/")
async def upload_csv(
    request: Request,
):
    return templates.TemplateResponse('upload.html', context={'request': request})

@app.post("/uploadfile/")
async def upload_csv_post(
    request: Request,
    file: UploadFile = File(...)   
    ):
    
    data = await file.read()
    data = data.decode()

    f = StringIO(data)
    csv_list = []
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        csv_list.append(row)
    headers = csv_list[0]
    header_query = ""

    for header in headers:
        header_query = f'''{header_query}{header} NVARCHAR(MAX),'''
    
    
    table_name = str(file.filename).split('.')[0]
    create_query = f'''
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE {table_name} (
    {header_query}
    );'''

    cursor.execute(create_query)
    conn.commit()

    header_string = ""
    header_count = 0
    for header in headers:
        header_string = f"{header_string}, {header}"
        header_count = header_count + 1
    header_string = header_string[2:]

    first = True
    
    values_list = []
    for row in csv_list:
        
        if first == True:
            first = False
            continue    
        else:
            insert_list = []
            for i in row:
                #TODO simplify replacing of these characters that cause issues
                entry = str(i).replace(" ", "_").replace(":","-").replace("'","")
                insert_list.append(entry)
            values_list.append(insert_list)

    placeholders = ''

    for i in range(header_count):
        placeholders = f'{placeholders}, ?'
    placeholders = placeholders[2:]

    insert_query = f'''INSERT INTO {table_name} VALUES ({placeholders})'''
    cursor.fast_executemany = True
    cursor.executemany(insert_query, values_list)

    conn.commit()

    return templates.TemplateResponse('upload_success.html', context={'request': request, 'table_name': table_name})
    # return insert_list