import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table,Column,Integer,String
import glob
import os
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper
from datetime import datetime
from app import app, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from time import time
import jwt
from datetime import datetime
from app.models import User, Policy, PolicyVote, Vote, Comment

#This function will create a separate table for csv file, if you have multiple csv files
#Name of table will be extracted from file name. File name contains product name.
#Each table will be identified by product name
# It will read each excel file in the folder and insert bom into table
def create_user_table(file_name):
  #Read file into dataframe
  csv_data=pd.read_csv(file_name)

  #Convert dataframe to list and store in same variable
  csv_data=csv_data.values.tolist()

  #Get table name from file name. This will be our table name.
  table_name_from_file=file_name.split('/')[8][:-4]

  for row in csv_data:
      #Each element in the list is an attribute for the table class
      #Iterating through rows and inserting into table
      user = User(admin=row[1], username=row[2], name=row[3], email=row[4], contributionPoints=row[6])
      user.set_password(row[5])
      db.session.add(user)
      db.session.commit()

def create_policy_table(file_name):
  #Read file into dataframe
  csv_data=pd.read_csv(file_name)

  #Convert dataframe to list and store in same variable
  csv_data=csv_data.values.tolist()

  #Get table name from file name. This will be our table name.
  table_name_from_file=file_name.split('/')[8][:-4]

  for row in csv_data:
      #Each element in the list is an attribute for the table class
      #Iterating through rows and inserting into table
      policy = Policy(
            id = row[0],
            user_id = row[1],
            title = row[2],

            economic_votes = row[3],
            death_votes = row[4],
            adherence_votes = row[5],
            total_votes = row[6],

            citation = row[7],
            description = row[8],
            tags = row[9]
      )
      db.session.add(policy)
      db.session.commit()

def create_policy_vote_table(file_name):
  #Read file into dataframe
  csv_data=pd.read_csv(file_name)

  #Convert dataframe to list and store in same variable
  csv_data=csv_data.values.tolist()

  #Get table name from file name. This will be our table name.
  table_name_from_file=file_name.split('/')[8][:-4]

  for row in csv_data:
    #Each element in the list is an attribute for the table class
    #Iterating through rows and inserting into table
    policy_vote = PolicyVote(
        id = row[0],
        policy_id = row[1],
        vote_id = row[2]
    )

    db.session.add(policy_vote)
    db.session.commit()

def create__vote_table(file_name):
  #Read file into dataframe
  csv_data=pd.read_csv(file_name)

  #Convert dataframe to list and store in same variable
  csv_data=csv_data.values.tolist()

  #Get table name from file name. This will be our table name.
  table_name_from_file=file_name.split('/')[8][:-4]

  for row in csv_data:
    #Each element in the list is an attribute for the table class
    #Iterating through rows and inserting into table
    vote = Vote(
        id = row[0],
        user_id = row[1],
        policy_id_1 = row[2],
        policy_id_2 = row[3],
        economic = row[4],
        death = row[5],
        adherence = row[6],
        conflict = row[7]
      )

    db.session.add(vote)
    db.session.commit()

def create__comment_table(file_name):
  #Read file into dataframe
  csv_data=pd.read_csv(file_name)

  #Convert dataframe to list and store in same variable
  csv_data=csv_data.values.tolist()

  #Get table name from file name. This will be our table name.
  table_name_from_file=file_name.split('/')[8][:-4]

  for row in csv_data:
    #Each element in the list is an attribute for the table class
    #Iterating through rows and inserting into table
    comment = Comment(
        id = row[0],
        policy_id = row[1],
        user_id = row[2],
        text = row[3],
        citation = row[4]
      )
    db.session.add(comment)
    db.session.commit()
