import pymzn
import os
from subprocess import Popen, PIPE
from flask import Flask, json, Response
app = Flask(__name__)

models = []
for file in os.listdir('.'):
	if file.endswith('.mzn'):
		models.append(file)

@app.route('/')
def AllSolvers():
	return json.jsonify(result=models)

@app.route('/solve/<string:solver>')
def Solve(solver):
	if (solver+".mzn" in models):
		def output_line():
			output = []
			with Popen(["MiniZinc", solver+".mzn", "-a"], stdout=PIPE, bufsize=1, universal_newlines=True) as p:
				for line in p.stdout:
					if line.rstrip() != '----------':
						yield json.dumps(line.rstrip())
					#print(line, end='')
		#output = pymzn.minizinc("" + solver + ".mzn")#, data={'n':4})
		#return json.jsonify(output)
		return Response(output_line(),  mimetype='text/json')
	else:
		return json.jsonify(solver="no solver found")