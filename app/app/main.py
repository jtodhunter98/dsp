
import csv
import os
from os import path

import shutil
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

cursor = conn.cursor()


@app.get("/")
def index(
    request: Request
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

@app.get("/uploadfile/")
def upload_csv(
    request: Request,
    file
):

    return templates.TemplateResponse(context={'request': request})

@app.post("/uploadfile/")
async def upload_csv_post(file: UploadFile = File(...)):
    file_location = f"csv/{file.filename}"
    with open(file_location, "r") as csv:
        shutil.copyfileobj(file.file, csv)

    url = str(file_location)

    return {"filename": file.filename, "url": url}

@app.get("/test_table/download")
def test_table_download():
    # os.remove('temp.csv')

    query_all = '''SELECT * FROM test_table'''
    users = cursor.execute(query_all)

    if os.path.exists('app/csv/temp.csv'):
        os.remove('app/csv/temp.csv')

    with open('app/csv/temp.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in users:
            writer.writerow([row.id, row.first_name, row.last_name, row.address, row.phone_number])
    
    return FileResponse('app/csv/temp.csv')