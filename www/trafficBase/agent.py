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

            # Check if the move is diagonal
            dx = abs(next[0] - current[0])
            dy = abs(next[1] - current[1])
            if dx == 1 and dy == 1:
                new_cost += 1  # Add extra cost for diagonal move
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
        # Blinkers are off by default
        self.blinker_state = 'off'  # Initialize the blinker state
        self.blinkers = 'off'
        self.wait = False

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

            next_cell_contents = grid.get_cell_list_contents([next_pos])
            # Check if next cell is an obstacle (assuming obstacles are represented in a certain way)
            for obj in next_cell_contents:
                if isinstance(obj, Obstacle):
                    return False

            # Check for road directions
            current_road = next(filter(lambda obj: isinstance(obj, Road), grid.get_cell_list_contents([current_pos])), None)
            next_road = next(filter(lambda obj: isinstance(obj, Road), grid.get_cell_list_contents([next_pos])), None)
            if current_road:
                return self.validate_road_direction(current_road, next_road, current_pos, next_pos)

            # Path is clear if none of the above conditions are met
            return True
        
        # Find the path using A* algorithm
        self.path = a_star_search(matrix, start, end, is_path_clear)

        if len(self.path) == 0:
            print(f"Agent {self.unique_id} could not find a path to {end}")

        # Convert path to list of tuples and return it
        return self.path
    
    def is_turn_approaching(self):
        # Check the next few steps in the path for a turn
        look_ahead_distance = 3  # Number of steps to look ahead
        for i in range(1, min(look_ahead_distance, len(self.path))):
            current_direction = self.get_direction(self.pos, self.path[i - 1])
            next_direction = self.get_direction(self.path[i - 1], self.path[i])
            if current_direction != next_direction:
                return True
        return False
    
    @staticmethod
    def get_direction(from_cell, to_cell):
        dx, dy = to_cell[0] - from_cell[0], to_cell[1] - from_cell[1]
        if abs(dx) > abs(dy):
            return "Horizontal" if dx > 0 else "Vertical"
        else:
            return "Vertical" if dy > 0 else "Horizontal"
        
    @staticmethod
    def validate_road_direction(current_road, next_road, current_pos, next_pos):
        x, y = current_pos
        nx, ny = next_pos

        # Validate direction of the current road
        if current_road.direction == "Left" and nx >= x:
            return False
        if current_road.direction == "Right" and nx <= x:
            return False
        if current_road.direction == "Up" and ny <= y:
            return False
        if current_road.direction == "Down" and ny >= y:
            return False

        # Validate direction of the next road only if next_road is not None
        if next_road is not None:
            if next_road.direction == "Left" and nx >= x:
                return False
            if next_road.direction == "Right" and nx <= x:
                return False
            if next_road.direction == "Up" and ny <= y:
                return False
            if next_road.direction == "Down" and ny >= y:
                return False

        return True
    
    def move(self):
        if len(self.path) == 0:
            self.find_path()
            return
        
        next_cell = self.path.pop(0)
        cell_contents = self.model.grid.get_cell_list_contents([next_cell])

        # Check if the agent has arrived at the correct destination
        for obj in cell_contents:
            if isinstance(obj, Destination):
                if obj == self.destination:
                    print(f"Agent {self.unique_id} has arrived at its destination.")
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    return
                else:
                    print(f"Agent {self.unique_id} has arrived at a destination, but not its own.")
                    self.path = []
                    self.find_path()
                    return

        # Check for a red traffic light
        traffic_light = next((obj for obj in cell_contents if isinstance(obj, Traffic_Light)), None)
        if traffic_light and not traffic_light.state:  # Assuming False means red
            print(f"Agent {self.unique_id} is waiting for the traffic light.")
            return

        # Check for the presence of a road and validate its direction
        road = next((obj for obj in cell_contents if isinstance(obj, Road)), None)
        if road or isinstance(obj, Destination) or (traffic_light and traffic_light.state):  # Road, destination or green traffic light
            if road:
                next_road = next((obj for obj in self.model.grid.get_cell_list_contents([next_cell]) if isinstance(obj, Road)), None)
                # Validate the direction of the road
                correct_direction = self.validate_road_direction(road, next_road, self.pos, next_cell)
                if not correct_direction:
                    print(f"Agent {self.unique_id} is trying to move to {next_cell} but the road direction is {road.direction}")
                    self.path = []
                    self.find_path()
                    return

            # Check for car presence in the next cell
            if any(isinstance(obj, Car) for obj in cell_contents):
                print(f"Agent {self.unique_id} is waiting due to traffic ahead.")
                return

            # Handle upcoming turns
            if self.is_turn_approaching():
                self.model.grid.move_agent(self, next_cell)
                return

            # If all checks pass, move to the next cell
            self.model.grid.move_agent(self, next_cell)
        else:
            print(f"Agent {self.unique_id} cannot move to {next_cell} as it is not a valid cell for movement.")
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
        
        if self.wait:
            self.wait = False
            return  # Skip this step to yield

        # Set blinker state based on upcoming movement
        self.update_blinker_state()

        # Check and react to neighbors' blinker states
        self.react_to_neighbors_blinkers()

        self.move()
    
    def update_blinker_state(self):
        if self.is_turn_approaching():
            turn_direction = self.get_turn_direction()
            if self.blinker_state != turn_direction:
                print(f"Car {self.unique_id} turning on {turn_direction} blinker")  # Debug print
            self.blinker_state = turn_direction
        else:
            if self.blinker_state != 'off':
                print(f"Car {self.unique_id} turning off blinker")  # Debug print
            self.blinker_state = 'off'
    
    def get_turn_direction(self):
        # Ensure there are at least two steps ahead in the path to determine a turn
        if len(self.path) < 2:
            return 'off'

        # Current and next positions
        current_pos = self.path[0]
        next_pos = self.path[1]

        # Calculate direction vectors
        current_direction = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])

        # If there is a third position, use it to determine the turn direction
        if len(self.path) > 2:
            future_pos = self.path[2]
            next_direction = (future_pos[0] - next_pos[0], future_pos[1] - next_pos[1])

            # Compare current direction with next direction
            if current_direction[0] == next_direction[0] and current_direction[1] == next_direction[1]:
                return 'off'  # Going straight
            elif current_direction[0] == next_direction[1] and current_direction[1] == -next_direction[0]:
                return 'right'  # Right turn
            elif current_direction[0] == -next_direction[1] and current_direction[1] == next_direction[0]:
                return 'left'  # Left turn

        # If the path does not have a third position, it means we're not turning
        return 'off'
    
    def react_to_neighbors_blinkers(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            if isinstance(neighbor, Car) and neighbor.blinker_state in ['left', 'right']:
                # If the neighbor is signaling to turn, yield to allow them to pass
                self.yield_to_turning_car(neighbor)

    def yield_to_turning_car(self, turning_car):
        # Wait for one step
        self.wait = True

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
        self.axis = "x" if state else "y"
        self.direction = None
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if not self.direction:
            # Use adjacent cells to determine the direction of the traffic
            # light (filter out cells that don't contain a road)
            adjacent_roads = [obj for obj in self.model.grid.get_neighbors(self.pos, moore=False) if isinstance(obj, Road)]
            # Check if there are more than 2 roads adjacent to the traffic
            # light
            
            if all(road.direction == adjacent_roads[0].direction for road in adjacent_roads):
                self.direction = adjacent_roads[0].direction
            else:
                # Assume the direction of the road that has my axis using my
                # pos +/- 1 (e.g. if my axis is x, check the cell to my left
                # and right)
                if self.axis == "x":
                    # Check from the list of adjacent roads which one has the
                    # same x value as the traffic light
                    road = next((road for road in adjacent_roads if road.pos[0] == self.pos[0]), None)
                    if road:
                        self.direction = road.direction
                elif self.axis == "y":
                    # Check from the list of adjacent roads which one has the
                    # same y value as the traffic light
                    road = next((road for road in adjacent_roads if road.pos[1] == self.pos[1]), None)
                    if road:
                        self.direction = road.direction
                        
            
        # print(f"Traffic light is facing {self.direction}")
                    
        # Change the state of the traffic light
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
        for agent in cell:
            if isinstance(agent, Car) and agent.destination == self:
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
        # if len(cell) > 1:
        #     self.model.grid.remove_agent(cell[1])
        #     # remove the car from the schedule
        #     self.model.schedule.remove(cell[1])

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
