from app import Create_app
from flask import request, make_response, redirect, render_template,session,url_for,flash
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Create_app()
app.secret_key = 'your secret key'
