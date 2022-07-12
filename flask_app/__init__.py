from flask import Flask
app = Flask(__name__)
import os
from dotenv import load_dotenv
load_dotenv()


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
port = os.getenv("PORT")