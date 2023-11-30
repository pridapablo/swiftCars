from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light, Obstacle, Road, Destination
import argparse
import threading
import time
import requests

# Model configuration
width = 0
height = 0
cityModel = None
currentStep = 0

app = Flask("Traffic")

def background_task(post_endpoint, periodicity):
    print(f"Starting background task to post to {post_endpoint} every {periodicity} seconds.")
    global cityModel
    while True:
        try:
            if cityModel:
                car_count = cityModel.get_car_count()
                total_trips = cityModel.get_complete_trips()
                payload = {
                    "year": 2023,
                    "classroom": 301,
                    "name": "Equipo 2: Swifties",
                    "num_cars": car_count,
                    "num_trips": total_trips,
                }
                print(f"Payload: {payload}")
                response = requests.post(post_endpoint, json=payload)
                print(f"Posted to {post_endpoint}: {response.status_code} {response.reason}")
        except Exception as e:
            print(f"Error during POST: {e}")
        time.sleep(periodicity)

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
        trafficLightPositions = [{"id": str(a.unique_id), "x": x, "y": 0, "z": z, "state": "red" if not a.state else "green", "axis": a.axis, "direction": a.direction}
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
        
        print(f"Red traffic lights: {len([tl for tl in cityModel.traffic_lights if tl.state == False])}")
        
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
    # una vez que se actualice, se regresa un mensaje de que se actualizó y el
    # paso en el que va
    global currentStep, cityModel
    if not cityModel:
        return jsonify({
            "message": "Model not initialized."
        }), 500
    if request.method == 'GET':
        cityModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

@app.route('/setCycle', methods=['POST'])
def updateCycle():
    global cityModel
    if not cityModel:
        return jsonify({
            "message": "Model not initialized."
        }), 500
    if request.method == 'POST':
        cityModel.set_cycle(request.json['cycle'])
        return jsonify({'message':f'Cycle updated to {cityModel.cycle}.'})


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Run the model server.')
    parser.add_argument(
        '--port', 
        dest='port', 
        type=int, 
        default=8585,
        help='The port to run the server on.'
    )
    parser.add_argument(
        '--postEP',
        dest='postEP',
        type=str,
        default="http://52.1.3.19:8585/api/validate_attempt",
        help='The endpoint to post to.'
    )
    parser.add_argument(
        '--postPeriodicity',
        dest='postPeriodicity',
        type=int,
        default=60,
        help='The number of seconds between posts.'
    )

    args = parser.parse_args()

    if args.postEP:
        # Start the background task
        thread = threading.Thread(
            target=background_task, 
            args=(args.postEP, args.postPeriodicity), 
            daemon=True
        )
        thread.start()

    app.run(
        host='localhost',
        port=args.port,
        debug=True
    )