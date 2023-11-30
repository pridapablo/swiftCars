from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import os
import json

def print_grid(multigrid: MultiGrid):
            # Mapping of direction to arrow symbols
            direction_arrows = {
                "Left": "←",
                "Right": "→",
                "Up": "↑",
                "Down": "↓",
                "Vertical": "|",
                "Horizontal": "-",
                "Any": "+"
            }

            for y in range(multigrid.height - 1, -1, -1):  # Start from the top row
                for x in range(multigrid.width):
                    next_cell_contents = multigrid.get_cell_list_contents([(x, y)])

                    # Check if the cell contains any Car agents
                    car_agents = [agent for agent in next_cell_contents if isinstance(agent, Car)]
                    destination_agents = [agent for agent in next_cell_contents if isinstance(agent, Destination)]
                    if car_agents:
                        # If there's a car, represent it with '⊙'
                        print('⊙', end=' ')
                    elif destination_agents:
                        # If there's a destination, represent it with 'D'
                        print('D', end=' ')
                    else:
                        # Check if the cell contains any Road agents
                        road_agents = [agent for agent in next_cell_contents if isinstance(agent, Road)]
                        if road_agents:
                            # Assuming one road per cell, modify if needed
                            road = road_agents[0]
                            print(direction_arrows.get(road.direction, '?'), end=' ')
                        else:
                            print('.', end=' ')  # '.' represents an empty cell
                print()  # Newline after each row
class CityModel(Model):
    """ 
        Creates a model based on a city map.
    """
    def __init__(self):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        path = os.path.abspath('./city_files/mapDictionary.json')
        dataDictionary = json.load(open(path))
        # Load the map file. The map file is a text file where each character
        # represents an agent.
        
        with open('./city_files/2023_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.cycle = 3 # Modulo of the step number to add a new car
            self.corners = [(0, 0), (self.width - 1, 0), (0, self.height - 1), (self.width - 1, self.height - 1)]

            self.complete_trips = 0
            self.traffic_lights = []
            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines): 
                for c, col in enumerate(row): 
                    if col in ["v", "^", ">", "<","."]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col]) # recibe un id, el modelo y la dirección de la calle
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                        # also place a road agent in the same position
                        agent = Road(f"r_{r*self.width+c}", self, direction="Vertical" if col == "S" else "Horizontal")
                        self.grid.place_agent(agent, (c, self.height - r - 1))  

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)

        self.num_agents = 0
        self.running = True

    def set_cycle(self, cycle):
        self.cycle = cycle

    def get_car_count(self):
        return len([agent for agent in self.schedule.agents if isinstance(agent, Car)])

    def add_complete_trip(self):
        self.complete_trips += 1

    def get_complete_trips(self):
        return self.complete_trips
    
    # Function to find a random destination for the cars
    def find_destination(self):
        # Create an empty list to store destination agents
        destinations = []

        # Iterate over all agents and add Destination agents to the list
        for agent in self.schedule.agents:
            if isinstance(agent, Destination):
                destinations.append(agent)

        # Choose a random destination from the list
        return self.random.choice(destinations) if destinations else None
    
    def step(self):
        '''Advance the model by one step.'''
        # Print the grid at step 2
        if self.schedule.steps == 2:
            print_grid(self.grid)

        # Check if it's time to add a new car
        if self.schedule.steps % self.cycle == 0:
            all_corners_filled = True  # Assume all corners are filled initially

            for corner in self.corners:
                destination = self.find_destination()
                if destination is None:
                    continue  # Skip if no destination found

                # Check if corner has a car
                if not any(isinstance(agent, Car) and agent.pos == corner for agent in self.schedule.agents):
                    all_corners_filled = False  # A corner is not filled

                    agent = Car(f"c_{self.num_agents}", self, destination)
                    self.grid.place_agent(agent, corner)
                    self.schedule.add(agent)
                    self.num_agents += 1
                else:
                    print(f"Corner {corner} is already filled")

            # Halt if all corners are filled
            # if all_corners_filled:
            #     print("All corners are filled. Halting the model.")
            #     self.running = False

        print(f"Total cars at destination: {self.get_complete_trips()}")
        # Proceed with the rest of the step
        self.schedule.step()