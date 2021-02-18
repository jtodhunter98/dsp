import csv
import os
from os import path


from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import session, sessionmaker
from fastapi.templating import Jinja2Templates
from sqlalchemy.sql.functions import user
from starlette.requests import Request

from . import random_gen

app = FastAPI()
templates = Jinja2Templates(directory="app/templates/")
engine = create_engine("mysql://root:password@db/test_db")

Base = declarative_base()
class User(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True)
    first_name = Column(VARCHAR(60))
    last_name = Column(VARCHAR(60))
    address = Column(VARCHAR(60))
    phone_number = Column(VARCHAR(60))


@app.get("/")
def index(request: Request):

    return templates.TemplateResponse('index.html', context={'request': request})


@app.get("/test_table")
def test_table(request: Request):

    Session = sessionmaker(bind=engine)

    session = Session()
    session.query(User).delete()
    session.commit()
    session.close()
    
    for i in range(5):
        session = Session()
        user = User(
            first_name = random_gen.person_entry().first_name,
            last_name = random_gen.person_entry().last_name,
            address = random_gen.person_entry().address,
            phone_number = random_gen.person_entry().phone_number
        )
        session.add(user)
        session.commit()
        session.close()

    session = Session()
    query_all = session.query(User)
    session.close()
    if path.exists('app/templates/temp.csv'):
        os.remove('app/templates/temp.csv')

    with open('app/templates/temp.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in query_all:
            writer.writerow([row.id, row.first_name, row.last_name, row.address, row.phone_number])

    return templates.TemplateResponse('test_table.html', context={
        'request': request,
        'users': query_all,
        })


@app.get("/test_table/download")
def test_table_download(request: Request):
    # os.remove('temp.csv')
    with open('temp.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        Session = sessionmaker(bind=engine)
        session = Session()

        query_all = session.query(User)
        for row in query_all:
            writer.writerow([row.id, row.first_name, row.last_name, row.address, row.phone_number])
    
    return templates.TemplateResponse('test_table.html', context={
        'request': request,
        'users': query_all,
        })