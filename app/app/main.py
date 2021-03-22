
import csv
import os
from os import path, read
import re
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

def numbers(number):
    array = []
    for i in range (3):
        array.append(number * 2)

    return array

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
    conn.commit()
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

    # if os.path.exists('app/csv/temp.csv'):
    #     os.remove('app/csv/temp.csv')

    # with open('app/csv/temp.csv', 'w', newline='') as file:
    #     writer = csv.writer(file)
    #     for row in users:
    #         writer.writerow([row.id, row.first_name, row.last_name, row.address, row.phone_number])

    return templates.TemplateResponse('test_table.html', context={
        'request': request,
        'users': users,
        })

@app.get("/upload/")
async def upload_csv(
    request: Request,
):

    return templates.TemplateResponse('upload.html', context={'request': request})

@app.post("/uploadfile/")
async def upload_csv_post(file: UploadFile = File(...)):
    
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
        header_query = f'''{header_query}{header} VARCHAR(1500),'''
    
    
    table_name = str(file.filename).split('.')[0]
    create_query = f'''
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE {table_name} (
    {header_query}
    );'''

    cursor.execute(create_query)
    conn.commit()

    header_string = ""
    for header in headers:
        header_string = f"{header_string}, {header}"
    header_string = header_string[2:]


    first = True
    for row in csv_list:
        insert_query = ''''''
        insert_string = ""
        if first == True:
            first = False
            continue    
        else:
            for i in row:
                #TODO simplify replacing of these characters that cause issues
                entry = str(i).replace(" ", "_").replace(":","-").replace("'","")
                entry = f"'{entry}'"
                insert_string = f'''{insert_string}, {entry}'''
            insert_string = insert_string[2:]
            insert_query = f'''INSERT INTO {table_name} VALUES ({insert_string});'''
            cursor.execute(insert_query)
            
    conn.commit()

    return insert_query

@app.get("/test_table/download")
def test_table_download():

    query_all = '''SELECT * FROM test_table'''
    users = cursor.execute(query_all)

    if os.path.exists('app/csv/temp.csv'):
        os.remove('app/csv/temp.csv')

    with open('app/csv/temp.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in users:
            writer.writerow([row.id, row.first_name, row.last_name, row.address, row.phone_number])
    
    return FileResponse('app/csv/temp.csv')

