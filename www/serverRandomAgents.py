# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git 

from flask import Flask, request, jsonify
from randomAgents.model import RandomModel # toma random agents como una librería
from randomAgents.agent import RandomAgent, ObstacleAgent

#configuración del modelo, van a ser datos que se van a recibir de unity
# son variables globales
# Size of the board:
number_agents = 10
width = 28
height = 28
randomModel = None
currentStep = 0

app = Flask("Traffic example")

@app.route('/init', methods=['POST']) # @ -> decorador, a partir de la aplicación de flask 
# le voy a ir indicando los endpoint que van a aplicarse con esta función
def initModel():
    global currentStep, randomModel, number_agents, width, height

    # recibir los parámetros del modelo
    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents')) # lo más simple que puede mandar unity es un form
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        randomModel = RandomModel(number_agents, width, height)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        # gets the positions of the agents and returns them to unity in json format
        # positions are sent as a list of dictionaries, where each dictionary has the id and position of an agent
        agentPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in randomModel.grid.coord_iter() if isinstance(a, RandomAgent)]
        # coord_iter() -> iterador que recorre el grid y regresa la posición de cada agente
        # isinstance() -> regresa true si el agente es de la clase RandomAgen, regresa la posición
        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel
    # pasa lo mismo que arriba pero para los obstáculos, este no se actualiza. solo pasa una vez
    if request.method == 'GET':
        carPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in randomModel.grid.coord_iter() if isinstance(a, ObstacleAgent)]

        return jsonify({'positions':carPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    # desde unity se va a mandar un get para que se actualice el modelo
    # una vez que se actualice, se regresa un mensaje de que se actualizó y el paso en el que va
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

# se corre el servidor
if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)