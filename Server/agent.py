from mesa import Agent
from mesa.space import MultiGrid
import math

class PriorityQueue:
    """
        Simple priority queue implementation.
    """
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        self.elements.append((priority, item))
        self.elements.sort()  # Sort in ascending order

    def get(self):
        return self.elements.pop(0)[1]  # Pop the element with the lowest priority

def heuristic(a, b):
    """
        Calculates the Euclidean distance between two points on a grid.
    """
    (x1, y1) = a
    (x2, y2) = b
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def a_star_search(grid_matrix: MultiGrid, start, goal, is_path_clear, block_cells=None):
    """
        Modified A* search algorithm that finds the shortest path between two points on
        a grid. It takes into account the direction of the road when calculating
        the path and any blocking cells that should be avoided.
    """
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
            dx = abs(next[0] - current[0])
            dy = abs(next[1] - current[1])
            if dx == 1 and dy == 1:
                new_cost += math.sqrt(2) - 1

            if block_cells and next in block_cells:
                new_cost += 1000

            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current)
    path.reverse()

    if not path:
        print("No path found!")
    elif path[-1] != goal:
        print(f"!!!!!!! Path does not reach the goal: {path[-1]} != {goal}")
    
    return path

def get_neighbors(grid: MultiGrid, pos):
    """
        Returns the neighbors of a cell based on the direction of the road.
    """
    x, y = pos
    neighbors = []

    # Agent knows all road directions, so we can get them from the grid
    current_next_cell_contents = grid.get_cell_list_contents([pos])

    # Check if current cell contains a road with a direction
    current_direction = None
    for obj in current_next_cell_contents:
        if isinstance(obj, Road):  # Replace 'Road' with your road class
            current_direction = obj.direction  # Assuming road objects have a 'direction' attribute

    if current_direction:
        # Get all neighbors (Moore neighborhood)
        all_neighbors = grid.get_neighborhood(pos, moore=True, include_center=False)

        # Filter based on the direction
        # Directions: Left, Right, Up, Down, Vertical, Horizontal
        if current_direction == 'Left':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if nx < x]
        elif current_direction == 'Right':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if nx > x]
        elif current_direction == 'Up':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if ny > y]
        elif current_direction == 'Down':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if ny < y]
        elif current_direction == 'Vertical':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if nx == x]
        elif current_direction == 'Horizontal':
            neighbors = [(nx, ny) for nx, ny in all_neighbors if ny == y]
        elif current_direction == 'Any':
            neighbors = all_neighbors
    else:
        # If the current cell does not contain a road, get all neighbors
        neighbors = grid.get_neighborhood(pos, moore=True, include_center=False)

    return neighbors

class Car(Agent):
    """
    A car agent in the traffic simulation that aims to reach a randomly assigned destination 
    while avoiding traffic congestion. It moves on a predefined grid, reacting to traffic lights 
    and other cars, and recalculates its path using A* algorithm when necessary.

    Attributes:
        unique_id: A unique identifier for the agent.
        model: The model instance of the simulation the agent is part of.
        destination: The destination the agent is trying to reach.
        path: A list of tuples representing the path to the destination.
        greediness: A measure of how proactive the agent is in route recalculations (0-1).
    """
    def __init__(self, unique_id, model, destination):
        super().__init__(unique_id, model)
        self.destination = destination
        self.path = []
        self.greediness = self.random.random() # value between 0 and 1
        self.position_history = [] # Determines if the agent is stuck
        self.is_stuck = False

    def find_path(self, block_cells=None):
        """ 
        Finds the path to the destination using A* checking road directions.
        """
        start = self.pos # Current position
        end = self.destination.get_position()

        # Check if the path is clear
        def is_path_clear(grid: MultiGrid, current_pos, next_pos):

            next_cell_contents = grid.get_cell_list_contents([next_pos])
            # Check if next cell is an obstacle (assuming obstacles are represented in a certain way)
            for obj in next_cell_contents:
                if isinstance(obj, Obstacle):
                    return False
                
            # Cells that are not my destination are also obstacles (or buildings, etc.)
            for obj in next_cell_contents:
                if isinstance(obj, Destination) and obj != self.destination:
                    return False

            # Check for road directions
            current_road = next(filter(lambda obj: isinstance(obj, Road), grid.get_cell_list_contents([current_pos])), None)
            next_road = next(filter(lambda obj: isinstance(obj, Road), grid.get_cell_list_contents([next_pos])), None)

            if current_road:
                return self.validate_road_direction(current_road, next_road, current_pos, next_pos)

            # Path is clear if none of the above conditions are met
            return True
        
        # Find the path using A* algorithm (block_cell is an optional parameter
        # and will be passed as none if not provided)
        self.path = a_star_search(self.model.grid, start, end, is_path_clear, block_cells)

        if len(self.path) == 0:
            print(f"Agent {self.unique_id} could not find a path to {end}, keeping current path.")
            return # Don't update the path if no path was found

        # Convert path to list of tuples and return it
        return self.path
    
    def update_position_history(self):
        """
            Updates the position history of the agent and checks if it is stuck
            based on the greediness of the agent.
        """
        # Add the current position to the history
        self.position_history.append(self.pos)

        # At minimum greediness (close to 0), the history length will be approximately 7. ​​
        # At maximum greediness (close to 1), the history length will be 4.
        max_history_length = round(7 - 4 * self.greediness)

        # Keep only the last x positions
        if len(self.position_history) > max_history_length:
            self.position_history.pop(0)

        # Check if the agent is stuck
        if len(self.position_history) == max_history_length and len(set(self.position_history)) == 1:
            self.is_stuck = True
        else:
            self.is_stuck = False
    
    @staticmethod
    def validate_road_direction(current_road, next_road, current_pos, next_pos):
        """
            Validates the direction of the road based on the current and next positions.
        """
        # Check if there is no movement
        if current_pos == next_pos:
            print(f"No movement from {current_pos} to {next_pos}, forcing path recalculation.")
            return False # No movement

        def is_valid_direction(road, x, y, nx, ny):
            directions = {
                "Left": nx < x,
                "Right": nx > x,
                "Up": ny > y,
                "Down": ny < y,
                "Vertical": nx == x,
                "Horizontal": ny == y
            }
            return directions.get(road.direction, True)

        x, y = current_pos
        nx, ny = next_pos

        # Validate direction of the current road
        if not is_valid_direction(current_road, x, y, nx, ny):
            return False

        # Validate direction of the next road only if next_road is not None
        if next_road is not None and not is_valid_direction(next_road, x, y, nx, ny):
            return False

        return True


    def step(self):
        """ 
            Triggered at each step of the simulation. Moves the agent to the
            next cell in the path and follows the subsumption architecture.

            Subsumption architecture:
            1. Destination
            2. Traffic lights
            3. Stuck: recalculate path before moving
            4. Traffic
            5. Road direction validation since the agent is moving
        """
        self.update_position_history()
        # 1. Destination
        current_cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in current_cell_contents:
            if isinstance(obj, Destination):
                if obj == self.destination:
                    print(f"Agent {self.unique_id} has arrived at its destination.")
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    return
                else:
                    print(f"Agent {self.unique_id} has arrived at a destination, but not its own.")
                    self.path = []
                    self.find_path(block_cells=[self.pos]) # Exclude the destination from the path
                    return
                
        # If the path is empty, find a new path since no destination was found
        if len(self.path) == 0:
            self.find_path()
            return
        
        next_cell = self.path[0]
        next_cell_contents = self.model.grid.get_cell_list_contents([next_cell])

        if next_cell:
            # 2. Traffic lights
            traffic_light = next((obj for obj in next_cell_contents if isinstance(obj, Traffic_Light)), None)
            if traffic_light and not traffic_light.state:  # False = Red
                return
        
            # 3. Stuck: recalculate path before moving
            if self.is_stuck:
                self.path = []
                # coordinates of the blocking neighbor is next_cell
                self.find_path(block_cells = [next_cell])
                if len(self.path) == 0:
                    print(f"Agent {self.unique_id} could not find a path to {self.destination.get_position()}, keeping current path.")
                    return
                next_cell = self.path[0]
                road = next((obj for obj in next_cell_contents if isinstance(obj, Road)), None) # this is an object

                if road:
                    next_road = next((obj for obj in self.model.grid.get_cell_list_contents([next_cell]) if isinstance(obj, Road)), None)

                    # Validate the direction of the road
                    correct_direction = self.validate_road_direction(road, next_road, self.pos, next_cell)

                    if not correct_direction:
                        self.path = []
                        self.find_path(block_cells=[next_cell]) # Exclude the invalid cell from the path
                        return

                # All checks have passed, move to the next cell if exists
                self.model.grid.move_agent(self, next_cell)
                self.path.pop(0) # Remove the first element from the path since the agent has moved to that cell
                return

            # 4. Traffic
            if any(isinstance(obj, Car) for obj in next_cell_contents):
                return # Won't move if there is a car in the next cell
            
            # 5. Road direction validation since the agent is moving
            road = next((obj for obj in next_cell_contents if isinstance(obj, Road)), None) # this is an object

            if road:
                next_road = next((obj for obj in self.model.grid.get_cell_list_contents([next_cell]) if isinstance(obj, Road)), None)

                # Validate the direction of the road
                correct_direction = self.validate_road_direction(road, next_road, self.pos, next_cell)

                if not correct_direction:
                    self.path = []
                    self.find_path(block_cells=[next_cell]) # Exclude the invalid cell from the path
                    return

            # All checks have passed, move to the next cell if exists
            self.model.grid.move_agent(self, next_cell)
            self.path.pop(0) # Remove the first element from the path since the agent has moved to that cell
        else:
            self.path = []
            self.find_path()

class Traffic_Light(Agent):
    """
    A traffic light agent that alternates between green and red states, influencing the traffic flow.
    It is smart enough to turn green when a certain number of cars are waiting and can orient 
    itself and the road beneath it based on the direction of the adjacent roads.

    Attributes:
        unique_id: A unique identifier for the agent.
        model: The model instance of the simulation the agent is part of.
        state: A boolean indicating the state of the traffic light, where True is green and False is red.
        axis: The axis along which the traffic light operates, determined by its initial state ('x' or 'y').
        direction: The direction the traffic light faces based on the adjacent roads.
        green_duration: The number of steps the traffic light remains green.
    """
    def __init__(self, unique_id, model, state = False):
        super().__init__(unique_id, model)
        self.state = state
        self.axis = "x" if state else "y"
        self.direction = None 
        self.green_duration = 4 if state else 0

    def set_direction(self, same_cell_road, adjacent_roads):
        """
            Sets the direction of the road and light based on the adjacent roads.
        """
        if same_cell_road and adjacent_roads:
            # Check if all adjacent roads have the same direction
            if all(road.direction == adjacent_roads[0].direction for road in adjacent_roads):
                self.direction = adjacent_roads[0].direction
                same_cell_road.direction = adjacent_roads[0].direction
            else:
                # Handle the case where adjacent roads have different directions
                self.determine_direction_based_on_axis(same_cell_road)
        

    def determine_direction_based_on_axis(self, same_cell_road):
        """
            Helper function to determine the direction of the traffic light
            based on the axis.
        """
        # get_neighborhood to get the coordinates of the Von Neumann neighbors
        neighboring_positions = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)

        axis_roads = []
        for pos in neighboring_positions:
            cell_contents = self.model.grid.get_cell_list_contents(pos)

            has_traffic_light = any(isinstance(obj, Traffic_Light) for obj in cell_contents)
            if has_traffic_light:
                continue

            for obj in cell_contents:
                if isinstance(obj, Road):
                    axis_roads.append(obj)

        # If there are roads in the axis direction, set the direction of the traffic light
        if axis_roads:
            # Set the direction based on the axis
            if self.axis == 'y':
                # Filter roads with vertical direction (Up or Down)
                vertical_roads = [road for road in axis_roads if road.direction in ['Up', 'Down']]
                if vertical_roads:
                    # Use the direction of the first vertical road found
                    self.direction = vertical_roads[0].direction
                    same_cell_road.direction = vertical_roads[0].direction
            else:
                # Filter roads with horizontal direction (Left or Right)
                horizontal_roads = [road for road in axis_roads if road.direction in ['Left', 'Right']]
                if horizontal_roads:
                    # Use the direction of the first horizontal road found
                    self.direction = horizontal_roads[0].direction
                    same_cell_road.direction = horizontal_roads[0].direction
        else:
            print(f"Traffic Light @ {self.pos}: No axis roads found")

    def is_direction_compatible(self, road_direction):
        """
            Checks if the direction of the road is compatible with the
            direction of the traffic light (defines its perception).
        """
        # Check if road direction is compatible with traffic light direction
        if self.direction in ['Left', 'Right']:
            return road_direction in ['Left', 'Right', 'Horizontal']
        elif self.direction in ['Up', 'Down']:
            return road_direction in ['Up', 'Down', 'Vertical']
        elif self.direction == 'Horizontal':
            return road_direction in ['Left', 'Right']
        elif self.direction == 'Vertical':
            return road_direction in ['Up', 'Down']
        return True  # 'Any' direction
    def step(self):
        """ 
            Changes the state of the traffic light based on the number of cars
            waiting and follows the subsumption architecture.
        """
        if not self.direction:
            # Getting adjacent roads but excluding the road on the same cell as the traffic light
            adjacent_cells_contents = [self.model.grid.get_cell_list_contents([pos]) 
                                       for pos in self.model.grid.get_neighborhood(self.pos, moore=False)]

            # Flatten the list of lists and then filter for Road objects excluding the current cell
            adjacent_roads = [obj for sublist in adjacent_cells_contents for obj in sublist 
                              if isinstance(obj, Road) and obj.pos != self.pos]

            # Get contents of the same cell
            same_cell_contents = self.model.grid.get_cell_list_contents([self.pos])

            # Filter for Road objects in the same cell
            this_cell_road = next((obj for obj in same_cell_contents if isinstance(obj, Road)), None) # this is an object

            # Check and update direction if all adjacent roads have the same direction
            # and there is a road on the same cell
            self.set_direction(this_cell_road, adjacent_roads)  
        
        ## Smart traffic light
        car_count = 0
        # Get the neighboring positions with a radius of 5
        for pos in self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False, radius=4):
            cell_contents = self.model.grid.get_cell_list_contents(pos)

            # Check for roads and their directions
            for obj in cell_contents:
                if isinstance(obj, Road) and self.is_direction_compatible(obj.direction):
                    # Count cars on this road
                    car_count += sum(isinstance(item, Car) for item in cell_contents)

        # Check for 2+ cars and change the light to green
        if car_count >= 2:
            self.state = True
            self.green_duration = 4  # Set the green light duration

        # Decrement green light duration and change back to red if duration is over
        if self.state and self.green_duration > 0:
            self.green_duration -= 1
            if self.green_duration == 0:
                self.state = False
class Destination(Agent):
    """
    A destination agent representing the target location for car agents. When a car agent reaches its 
    destination, it is removed from the simulation, and the trip is recorded as complete.

    Attributes:
        unique_id: A unique identifier for the agent.
        model: The model instance of the simulation the agent is part of.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def get_position(self):
        return self.pos

    def step(self):
        """
            Triggered at each step of the simulation. Checks if there is a car in
            the destination. If so, removes the car from the simulation and records.
        """
        # If there is a car in the destination, remove it
        cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cell:
            if isinstance(agent, Car) and agent.destination == self:
                self.model.add_complete_trip()
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
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
    Road agent. Determines which direction the cars can move in.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
