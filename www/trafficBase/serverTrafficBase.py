from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light, Obstacle, Road, Destination

# Model configuration
width = 0
height = 0
cityModel = None
currentStep = 0

app = Flask("Traffic")

@app.route('/init', methods=['POST']) #
def initModel():
    global width, height, cityModel, currentStep
    if request.method == 'POST':
        currentStep = 0

        cityModel = CityModel()
        return jsonify({"message":"Parameters recieved, model initiated."})
    else:
        return jsonify({
            "message": "Method not allowed."
        }), 405
    
    
@app.route('/getCars', methods=['GET']) # reads all (car) agents, and returns them to unity in json format
def getCars():
    global cityModel
    if not cityModel:
        return jsonify({
            "message": "Model not initialized."
        }), 500
    if request.method == 'GET':
        carPositions = [{"id": str(car.unique_id), "x": x, "y": 0, "z": z}
                for x in range(cityModel.grid.width)
                for z in range(cityModel.grid.height)
                for car in cityModel.grid.get_cell_list_contents((x, z))
                if isinstance(car, Car)]

        return jsonify({'positions':carPositions})

@app.route('/getObstacles', methods=['GET']) # there is no need to update obstacles, so this is a one-time call
def getObstacles():
    global cityModel
    if request.method == 'GET':
        obstaclePositions = [{"id": str(obstacle.unique_id), "x": x, "y": 0, "z": z}
                for x in range(cityModel.grid.width)
                for z in range(cityModel.grid.height)
                for obstacle in cityModel.grid.get_cell_list_contents((x, z))
                if isinstance(obstacle, Obstacle)]

        return jsonify({'positions':obstaclePositions})
   
@app.route('/getTrafficLights', methods=['GET']) # get the traffic lights and its state (red or green)
def getTrafficLights():
    global cityModel
    if request.method == 'GET':
        trafficLightPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} 
                                for a, (x, z) in cityModel.grid.coord_iter() 
                                if isinstance(a, Traffic_Light)]
        return jsonify({'positions':trafficLightPositions})
    
@app.route('/getRoads', methods=['GET'])
def getRoads():
    global cityModel
    if request.method == 'GET':
        roadPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Road)]
        return jsonify({'positions':roadPositions})
    
@app.route('/getDestinations', methods=['GET'])
def getDestinations():
    global cityModel
    if request.method == 'GET':
        destinationPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Destination)]
        return jsonify({'positions':destinationPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    # desde unity se va a mandar un get para que se actualice el modelo
    # una vez que se actualice, se regresa un mensaje de que se actualizó y el paso en el que va
    global currentStep, randomModel
    if request.method == 'GET':
        cityModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(
        host='localhost',
        port=8585,
        debug=True
    )
# 