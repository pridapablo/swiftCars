from mesa import Agent
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
        self.path = a_star_search(self.model.grid, start, end, is_path_clear)

        if len(self.path) == 0:
            print(f"Agent {self.unique_id} could not find a path to {end}")

        # Convert path to list of tuples and return it
        return self.path
    
    
    @staticmethod
    def get_direction(from_cell, to_cell):
        dx, dy = to_cell[0] - from_cell[0], to_cell[1] - from_cell[1]
        if abs(dx) > abs(dy):
            return "Horizontal" if dx > 0 else "Vertical"
        else:
            return "Vertical" if dy > 0 else "Horizontal"
        
    @staticmethod
    def validate_road_direction(current_road, next_road, current_pos, next_pos):
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

    
    def print_grid(multigrid):
            # Mapping of direction to arrow symbols
            direction_arrows = {
                "Left": "←",
                "Right": "→",
                "Up": "↑",
                "Down": "↓",
                "Vertical": "|",
                "Horizontal": "-"
            }

            for y in range(multigrid.height - 1, -1, -1):  # Start from the top row
                for x in range(multigrid.width):
                    next_cell_contents = multigrid.get_cell_list_contents([(x, y)])

                    # Check if the cell contains any Car agents
                    car_agents = [agent for agent in next_cell_contents if isinstance(agent, Car)]
                    if car_agents:
                        # If there's a car, represent it with '⊙'
                        print('⊙', end=' ')
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

    def move(self):
        # print(f"Agent @ {self.pos}: next cell: {self.path[0] if self.path else None} | path: {self.path}")
        if len(self.path) == 0:
            self.find_path()
            return
        
        current_cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        next_cell = self.path[0]
        next_cell_contents = self.model.grid.get_cell_list_contents([next_cell])

        # 1. Traffic lights
        traffic_light = next((obj for obj in next_cell_contents if isinstance(obj, Traffic_Light)), None)
        if traffic_light and not traffic_light.state:  # Assuming False means red
            print(f"Agent {self.unique_id} is waiting for the traffic light.")
            return

        # 2. Destination
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
                    self.find_path()
                    return

        # 3. Traffic
        if any(isinstance(obj, Car) for obj in next_cell_contents):
            # TODO: if the car in front does not move for x steps, change lane
            # TODO: Check if i've been waiting for x steps, if so, recalculate
            # path setting the following cells as obstacles
            return
        
        # 4. Road direction validation
        road = next((obj for obj in next_cell_contents if isinstance(obj, Road)), None) # this is an object

        if road:
            next_road = next((obj for obj in self.model.grid.get_cell_list_contents([next_cell]) if isinstance(obj, Road)), None)

            # Validate the direction of the road
            correct_direction = self.validate_road_direction(road, next_road, self.pos, next_cell)

            if not correct_direction:
                print(f"Path is invalid, forcing recalculation.")
                self.path = []
                self.find_path()
                return

        # All checks have passed, move to the next cell if exists
        if next_cell:
            self.model.grid.move_agent(self, next_cell)
            self.path.pop(0) # Remove the first element from the path since the agent has moved to that cell
        else:
            print(f"Recalculating path for agent {self.unique_id} no next cell found.")
            self.path = []
            self.find_path()
        

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # Agent design:
        # 3. Agents will always leave a gap of 1 cell between them and the next
        #    car (unless i'm super greedy)
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
        self.axis = "x" if state else "y"
        self.direction = False
        self.timeToChange = timeToChange

    def set_direction(self, same_cell_road, adjacent_roads):
        if same_cell_road and adjacent_roads:
            # Check if all adjacent roads have the same direction
            if all(road.direction == adjacent_roads[0].direction for road in adjacent_roads):
                self.direction = True
                same_cell_road.direction = adjacent_roads[0].direction
                print(f"Traffic Light @ {self.pos}: Direction set to {same_cell_road.direction} (based on adjacent roads)")
            else:
                # Handle the case where adjacent roads have different directions
                self.determine_direction_based_on_axis(same_cell_road)
        

    def determine_direction_based_on_axis(self, same_cell_road):
        # Print the initial axis and position

        # Use get_neighborhood to get the coordinates of the Von Neumann neighbors
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
                    self.direction = True
                    same_cell_road.direction = vertical_roads[0].direction
            else:
                # Filter roads with horizontal direction (Left or Right)
                horizontal_roads = [road for road in axis_roads if road.direction in ['Left', 'Right']]
                if horizontal_roads:
                    # Use the direction of the first horizontal road found
                    self.direction = True
                    same_cell_road.direction = horizontal_roads[0].direction

            print(f"Traffic Light @ {self.pos}: Direction set to {same_cell_road.direction} (based on axis)")
        else:
            print(f"Traffic Light @ {self.pos}: No axis roads found")

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
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
