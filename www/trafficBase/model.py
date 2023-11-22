from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json

class CityModel(Model):
    """ 
        Creates a model based on a city map.

        Args:
            N: Number of agents in the simulation
    """
    def __init__(self, N):

        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []

        # Load the map file. The map file is a text file where each character represents an agent.
        with open('city_files/2022_base.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines): 
                for c, col in enumerate(row): 
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col]) # recibe un id, el modelo y la dirección de la calle
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{r*self.width+c}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)


        self.num_agents = N
        self.running = True

    # Function to find a random destination for the cars
    def find_destination(self):
        # Create an empty list to store destination agents
        destinations = []

        # Iterate over all agents and add Destination agents to the list
        for agent in self.schedule.agents:
            if isinstance(agent, Destination):
                destinations.append(agent)

        # Choose a random destination from the list
        print(destinations)
        # return self.random.choice(destinations) if destinations else None
        return destinations[0] if destinations else None

    def step(self):
        '''Advance the model by one step.'''
     # If the step is a multiple of 10, then add 4 cars to the simulation
    # One in each corner
        # if self.schedule.steps % 10 == 0:
        if self.schedule.steps == 1:
            # Define corner positions
            # corners = [(0, 0), (self.width - 1, 0), (0, self.height - 1),
            # (self.width - 1, self.height - 1)]
            corners = [(0, 0)]

            for corner in corners:
                destination = self.find_destination()
                if destination is None: return # If there are no destinations, then return
                agent = Car(f"c_{self.num_agents}", self, destination)
                self.grid.place_agent(agent, corner)
                self.schedule.add(agent)
                self.num_agents += 1
                print(f"Added car {self.num_agents}")

        self.schedule.step()