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
    
    
@app.route('/getAgents', methods=['GET'])
def getAgents():
    global cityModel
    if not cityModel:
        return jsonify({
            "message": "Model not initialized."
        }), 500

    # Retrieve the 'static' parameter from the URL, default to False if not provided
    # static = request.args.get('static', 'false').lower() == 'true'

    if request.method == 'GET':
        obstaclePositions = [{"id": str(obstacle.unique_id), "x": x, "y": 0, "z": z}
                    for x in range(cityModel.grid.width)
                    for z in range(cityModel.grid.height)
                    for obstacle in cityModel.grid.get_cell_list_contents((x, z))
                    if isinstance(obstacle, Obstacle)]
        trafficLightPositions = [{"id": str(a.unique_id), "x": x, "y":0, "z":z, "state": a.state}
                            for x in range(cityModel.grid.width)
                            for z in range(cityModel.grid.height)
                            for a in cityModel.grid.get_cell_list_contents((x, z))
                            if isinstance(a, Traffic_Light)]
        roadPositions = [{"id": str(road.unique_id), "x": x, "y": 0, "z": z}
                    for x in range(cityModel.grid.width)
                    for z in range(cityModel.grid.height)
                    for road in cityModel.grid.get_cell_list_contents((x, z))
                    if isinstance(road, Road)]
        destinationPositions = [{"id": str(destination.unique_id), "x": x, "y": 0, "z": z}
                    for x in range(cityModel.grid.width)
                    for z in range(cityModel.grid.height)
                    for destination in cityModel.grid.get_cell_list_contents((x, z))
                    if isinstance(destination, Destination)]
        carPositions = [{"id": str(car.unique_id), "x": x, "y": 0, "z": z}
                        for x in range(cityModel.grid.width)
                        for z in range(cityModel.grid.height)
                        for car in cityModel.grid.get_cell_list_contents((x, z))
                        if isinstance(car, Car)]
        
        return jsonify(
            {'carPos':carPositions,
                'obstaclePos':obstaclePositions, 
                'trafficLightPos':trafficLightPositions, 
                'roadPos':roadPositions, 
                'destinationPos':destinationPositions
                })

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