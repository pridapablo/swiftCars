from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light, Obstacle, Road, Destination
import argparse
import threading
from mesa.visualization import CanvasGrid, ModularServer

# Model configuration
width = 0
height = 0
cityModel = None
currentStep = 0
periodicity = None
endpoint = None

app = Flask("Traffic")

@app.route('/init', methods=['POST']) #
def initModel():
    global width, height, cityModel, currentStep
    if request.method == 'POST':
        currentStep = 0

        cityModel = CityModel(periodicity=periodicity, endpoint=endpoint)
        return jsonify({"message": "Parameters received, model initiated."})
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
        print(f"Step {currentStep}")
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


# 2D visualization
def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 1,
                 "h": 1
                 }

    if (isinstance(agent, Road)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 0
    
    if (isinstance(agent, Destination)):
        portrayal["Color"] = "lightgreen"
        portrayal["Layer"] = 0

    if (isinstance(agent, Traffic_Light)):
        portrayal["Color"] = "red" if not agent.state else "green"
        portrayal["Layer"] = 1
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Obstacle)):
        portrayal["Color"] = "cadetblue"
        portrayal["Layer"] = 0
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8

    if (isinstance(agent, Car)):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 2
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        

    return portrayal

# Global variables for model dimensions
width = 0
height = 0

# Read city file and determine dimensions
with open('city_files/2023_base.txt') as baseFile:
    lines = baseFile.readlines()
    width = len(lines[0]) - 1
    height = len(lines)

grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# Argument validation functions
def validate_port(port):
    """Validate the port number is within the acceptable range."""
    port = int(port)
    if port < 1024 or port > 65535:
        raise argparse.ArgumentTypeError("Port number should be between 1024 and 65535.")
    return port

def validate_post_periodicity(periodicity):
    """Validate the post periodicity is a positive integer."""
    periodicity = int(periodicity)
    if periodicity <= 0:
        raise argparse.ArgumentTypeError("Post periodicity should be a positive integer.")
    return periodicity

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Traffic model server configuration.')

    # Server configuration
    server_group = parser.add_argument_group('server configuration')
    server_group.add_argument('-p', '--port', type=int, default=8585,
                            help='Port number for the server to listen on. Default is 8585.')

    # Stats posting configuration
    post_group = parser.add_argument_group('stats posting configuration')
    post_group.add_argument('-e', '--endpoint', type=str, 
                            # default="http://52.1.3.19:8585/api/attempt",
                            help='Endpoint URL for posting data.')
    post_group.add_argument('-f', '--frequency', type=int, default=60,
                            help='Time interval (in seconds) between consecutive posts. Default is 60 seconds.')

    # Mode configuration
    mode_group = parser.add_argument_group('mode configuration')
    mode_group.add_argument('-m', '--mode', choices=['2d', '3d'], default='3d',
                            help='Visualization mode: 2d mesa portrayal or 3d (for use with Unity). Default is 3d. '
                                'Note: The server will not ping the post-endpoint in 2d mode.')

    # Parse the arguments
    args = parser.parse_args()

    # Launch the appropriate server based on the mode
    if args.mode == '2d':
        mesa_server = ModularServer(CityModel, [grid], "Traffic Base", {"endpoint": args.endpoint, "periodicity": args.frequency})
        mesa_server.port = args.port
        mesa_server.launch()
    else:
        # Validate the post periodicity
        periodicity = args.frequency
        endpoint = args.endpoint

        app.run(
            host='localhost',
            port=args.port,
            debug=True
        )