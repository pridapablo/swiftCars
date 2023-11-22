from mesa import Agent, Model
from mesa.space import MultiGrid

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        self.elements.append((priority, item))
        self.elements.sort(reverse=True)  # Sort in place, highest priority first

    def get(self):
        return self.elements.pop()[1]
    
# A* search algorithm
def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(grid_matrix: MultiGrid, start, goal, is_path_clear):
    #typeof start and goal: tuple (x, y)
    #typeof grid_matrix: mesa model grid
    
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in get_neighbors(grid_matrix, current):
            if not is_path_clear(grid_matrix, current, next):
                continue
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()  # reverse the path to start -> goal
    return path

def get_neighbors(grid: MultiGrid, pos):
    x, y = pos
    neighbors = []

    # Assuming grid is a MultiGrid object
    current_cell_contents = grid.get_cell_list_contents([pos])

    # Check if current cell contains a road with a direction
    current_direction = None
    for obj in current_cell_contents:
        if isinstance(obj, Road):  # Replace 'Road' with your road class
            current_direction = obj.direction  # Assuming road objects have a 'direction' attribute

    if current_direction:
        # Get all neighbors (Moore neighborhood)
        all_neighbors = grid.get_neighborhood(pos, moore=True, include_center=False)

        # Filter based on the direction
        # Assuming directions are 'Left', 'Right', 'Up', 'Down'
        if current_direction == 'Left':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if nx < x]
        elif current_direction == 'Right':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if nx > x]
        elif current_direction == 'Up':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if ny > y]
        elif current_direction == 'Down':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if ny < y]
    else:
        # If the current cell does not contain a road, get all neighbors
        neighbors = grid.get_neighborhood(pos, moore=True, include_center=False)

    return neighbors

class Car(Agent):
    """
    Agent that moves towards its destination using A*.
    """
    def __init__(self, unique_id, model, destination):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            destination: Where the agent should go (destination agent)
            path: The path the agent will follow to get to the destination
            (could be empty)
            greedyness: How greedy the agent is (how proactive it is when
            interacting with other agents) (0-1)
        """
        super().__init__(unique_id, model)
        self.destination = destination
        self.path = []
        # Randomly choose a greedyness value between 0 and 1
        self.greedyness = self.random.random()

    def find_path(self):
        """ 
        Finds the path to the destination using A*
        """

        matrix = self.model.grid
        def print_grid(multigrid):
            # Mapping of direction to arrow symbols
            direction_arrows = {
                "Left": "←",
                "Right": "→",
                "Up": "↑",
                "Down": "↓"
            }

            for y in range(multigrid.height - 1, -1, -1):  # Start from the top row
                for x in range(multigrid.width):
                    cell_contents = multigrid.get_cell_list_contents([(x, y)])

                    # Check if the cell contains any Car agents
                    car_agents = [agent for agent in cell_contents if isinstance(agent, Car)]
                    if car_agents:
                        # If there's a car, represent it with '⊙'
                        print('⊙', end=' ')
                    else:
                        # Check if the cell contains any Road agents
                        road_agents = [agent for agent in cell_contents if isinstance(agent, Road)]
                        if road_agents:
                            # Assuming one road per cell, modify if needed
                            road = road_agents[0]
                            print(direction_arrows.get(road.direction, '?'), end=' ')
                        else:
                            print('.', end=' ')  # '.' represents an empty cell
                print()  # Newline after each row



        print_grid(matrix)

        start = self.pos # Current position
        end = self.destination.get_position()

        # Check if the path is clear
        def is_path_clear(grid: MultiGrid, current_pos, next_pos):
            # Get the contents of the current and next cell
            current_cell_contents = grid.get_cell_list_contents([current_pos])
            next_cell_contents = grid.get_cell_list_contents([next_pos])

            # Check if next cell is an obstacle (assuming obstacles are represented in a certain way)
            for obj in next_cell_contents:
                if isinstance(obj, Obstacle):  # Replace 'Obstacle' with your obstacle class
                    return False

            # Check for road directions
            current_road = next(filter(lambda obj: isinstance(obj, Road), current_cell_contents), None)
            next_road = next(filter(lambda obj: isinstance(obj, Road), next_cell_contents), None)

            if current_road and next_road:
                # Directions comparison
                current_direction = current_road.direction
                x, y = current_pos
                nx, ny = next_pos

                if current_direction == "Left" and nx >= x:
                    return False
                if current_direction == "Right" and nx <= x:
                    return False
                if current_direction == "Up" and ny <= y:
                    return False
                if current_direction == "Down" and ny >= y:
                    return False

            # Path is clear if none of the above conditions are met
            return True

        # Find the path using A* algorithm
        self.path = a_star_search(matrix, start, end, is_path_clear)

        if len(self.path) == 0:
            print(f"Agent {self.unique_id} could not find a path to {end}")

        # Convert path to list of tuples and return it
        return self.path

    def move(self):
        """ 
        Determines if the agent can move to the next cell in the path, and then moves.
        """        
        if len(self.path) == 0:
            # If the path is empty, find a new path
            print(f"Agent {self.unique_id} is looking for a path to {self.destination.get_position()}")
            self.find_path()
        else:
            # If the path is not empty, move to the next cell
            print(f"Agent {self.pos} is moving to {self.path[0]}")
            next_cell = self.path.pop(0)
            cell_contents = self.model.grid.get_cell_list_contents([next_cell])

            # Check if any car is present in the next cell
            if any(isinstance(obj, Car) for obj in cell_contents):
                print(f"Agent {self.unique_id} cannot move to {next_cell} as it's occupied by another car.")
                self.path = []
                self.find_path()
                return

            # Check if the cell contains a road and move accordingly
            road = next((obj for obj in cell_contents if isinstance(obj, Road)), None)
            if road:
                # Check the direction of the road
                correct_direction = True  # Default to True
                # if road.direction == "Left":
                #     correct_direction = next_cell[0] < self.pos[0]
                # elif road.direction == "Right":
                #     correct_direction = next_cell[0] > self.pos[0]
                # elif road.direction == "Up":
                #     correct_direction = next_cell[1] > self.pos[1]
                # elif road.direction == "Down":
                #     correct_direction = next_cell[1] < self.pos[1]

                if correct_direction:
                    self.model.grid.move_agent(self, next_cell)
                else:
                    print(f"Agent {self.unique_id} is trying to move to {next_cell} but the road direction is {road.direction}")
                    self.path = []
                    self.find_path()
            elif any(isinstance(obj, Destination) for obj in cell_contents):
                print(f"Agent {self.unique_id} has reached its destination")
                self.model.grid.move_agent(self, next_cell)
                self.path = []
            elif any(isinstance(obj, Traffic_Light) and obj.state for obj in cell_contents):
                traffic_light = next((obj for obj in cell_contents if isinstance(obj, Traffic_Light)), None)
                if traffic_light and traffic_light.state:
                    self.model.grid.move_agent(self, next_cell)
                else:
                    print(f"Agent {self.unique_id} is trying to move to {next_cell} but the traffic light is red")
                    self.path = []
                    self.find_path()
            else:
                print(f"Agent {self.unique_id} is trying to move to {next_cell} but the cell is not road or traffic light is red")
                self.path = []
                self.find_path()



    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # Agent design:
        # 2. If semaphores are red, wait (unless i'm super greedy and i see no cars)
        # 3. Agents will always leave a gap of 1 cell between them and the next
        #    car (unless i'm super greedy)
        # 4. What happens with road direction when calculating the path?
        # 5. Even if the path says to go to a cell, move needs to check if the
        #    direction is correct and if the cell is empty (neighbor cars)
        # 6. Communication between agents? Turn signals?
        # 7. Deal with congested roads (agent has own memory of the last x
        #    steps)
        # 9. Agents only change lanes if they will turn in the next
        #    intersection
        # Ya son proactivos
        
        # Falta paciencia (reactividad) 

        self.move()

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def get_position(self):
        return self.pos

    def step(self):
        # If there is a car in the destination, remove it
        cell = self.model.grid.get_cell_list_contents([self.pos])
        if len(cell) > 1:
            self.model.grid.remove_agent(cell[1])
            # remove the car from the schedule
            self.model.schedule.remove(cell[1])

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
