#!/usr/bin/python
import pymzn
from flask import *
app = Flask(__name__)

@app.route('/')
def hello_world():
	model = pymzn.Model('test.mzn')
	return(str(pymzn.minizinc(model)))
#	return 'Hello, World!'