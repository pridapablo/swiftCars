from flask import Flask, request, jsonify
from trafficBase.model import CityModel
from trafficBase.agent import Car, Traffic_Light, Obstacle, Road, Destination

# Model configuration
width = 0
height = 0
cityModel = None
currentStep = 0

app = Flask("Traffic")

@app.route('/init', methods=['POST'])
def initModel():
    global width, height, cityModel, currentStep
    if request.method == 'POST':
        currentStep = 0

        print(request.form)
        print(width, height)
        cityModel = CityModel()
        return jsonify({"message":"Parameters recieved, model initiated."})
    else:
        return jsonify({
            "message": "Parameters not received.",
            "data": request.form,
        }), 400  # Bad request
    
@app.route('/getCars', methods=['GET'])
def getAgents():
    global cityModel
    if request.method == 'GET':
        carPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Car)]
        return jsonify({'positions':carPositions})
   
@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global cityModel
    if request.method == 'GET':
        obstaclePositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Obstacle)]
        return jsonify({'positions':obstaclePositions})
   
@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global cityModel
    if request.method == 'GET':
        trafficLightPositions = [{"id": str(a.unique_id), "x": x, "y":1, "z":z} for a, (x, z) in cityModel.grid.coord_iter() if isinstance(a, Traffic_Light)]
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
    
if __name__=='__main__':
    app.run(
        host='localhost',
        port=8585,
        debug=True
    )