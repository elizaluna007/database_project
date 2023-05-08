import pandas as pd
import os
import time
import re
from database import Database as db

# ①密码错误
account = 12345
password = "11111111"
database_name = "db_1"
mydb = db(account, password, database_name)
# # mydb.instruction("create database db_test")
# print("_________________________________________________________________________")
# account = 12345
# password = "datsddsdasa"
# database_name = "db_1"
# mydb = db(account,password)
# # mydb.instruction("create database db_test")
# print("_________________________________________________________________________")
# account = 54321
# password = "sdasfdasa"
# database_name = "db_1"
# mydb = db(account,password,database_name)
# print("_________________________________________________________________________")
# account = 54321
# password = "sdasfdasa"
# database_name = "db_1"
# mydb = db(account,password)
# account = 543898921
# password = "sdasfdssasa"
# database_name = "db_1"
# mydb = db(account,password,database_name)
# print("_________________________________________________________________________")
