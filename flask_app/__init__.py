from flask import Flask
app = Flask(__name__)
import os
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
import os
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
port = os.getenv('PORT')