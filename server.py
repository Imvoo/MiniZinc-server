import pymzn
import os
from flask import Flask, json
app = Flask(__name__)

solvers = []
for file in os.listdir('.'):
    if file.endswith('.mzn'):
        solvers.append(file)

@app.route('/')
def AllSolvers():
    return json.jsonify(result=solvers)

@app.route('/solve/<string:solver>')
def Solve(solver):
    if (solver+".mzn" in solvers):
        output = pymzn.minizinc("" + solver + ".mzn")#, data={'n':4})
        return json.jsonify(output)
    else:
        return json.jsonify(solver="no solver found")
