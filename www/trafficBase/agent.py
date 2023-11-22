from mesa import Agent

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

def a_star_search(grid_matrix, start, goal, is_path_clear):
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

def get_neighbors(grid, pos):
    x, y = pos
    neighbors = []
    directions = {'Left': (-1, 0), 'Right': (1, 0), 'Up': (0, -1), 'Down': (0, 1)}

    # Get current cell and its direction if it's a road
    current_cell = grid[y][x]
    if isinstance(current_cell, tuple) and current_cell[0] == 1:
        current_direction = current_cell[1]

        # Add only the neighbor in the direction of the road
        dx, dy = directions[current_direction]
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
            neighbor_cell = grid[ny][nx]
            if neighbor_cell != 0:  # Check if the neighbor cell is not an obstacle
                neighbors.append((nx, ny))

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

        def print_grid_matrix(grid_matrix):
            # Symbols for each type of cell
            symbols = {
                0: "O",  # Obstacle
                1: ".",  # Walkable (no specific direction)
                (1, "Left"): "←",
                (1, "Right"): "→",
                (1, "Up"): "↑",
                (1, "Down"): "↓"
            }

            # reverse the grid matrix to print it correctly
            grid_matrix.reverse()
            
            for row in grid_matrix:
                for cell in row:
                    # Print the symbol for the cell, end='' keeps it on the same line
                    print(symbols.get(cell, "?"), end=' ')
                print()  # Newline after each row


        grid_matrix = []
        grid_height = self.model.height
        grid_width = self.model.width

       # Example modification for the grid matrix construction
        for y in range(grid_height):
            row = []
            for x in range(grid_width):
                cell = self.model.grid.get_cell_list_contents([(x, y)])
                cell_type = cell[0].__class__.__name__
                if cell_type == "Obstacle":
                    row.append(0)
                elif cell_type == "Road":
                    row.append((1, cell[0].direction))  # Assuming Road objects have a 'direction' attribute
                else:
                    row.append(1)
            grid_matrix.append(row)

        # Print the grid matrix
        print_grid_matrix(grid_matrix)

        start = self.pos
        end = self.destination.get_position()

        # Check if the path is clear
        def is_path_clear(grid, current_pos, next_pos):
            x, y = current_pos
            nx, ny = next_pos
            current_cell = grid[y][x]
            next_cell = grid[ny][nx]

            # If moving into an obstacle, return False
            if isinstance(next_cell, int) and next_cell == 0:
                return False

            # If both current and next cells are roads, check if the direction aligns
            if isinstance(current_cell, tuple) and current_cell[0] == 1 and \
            isinstance(next_cell, tuple) and next_cell[0] == 1:
                current_direction = current_cell[1]
                if current_direction == "Left" and nx >= x:
                    return False
                if current_direction == "Right" and nx <= x:
                    return False
                if current_direction == "Up" and ny >= y:
                    return False
                if current_direction == "Down" and ny <= y:
                    return False

            # If current or next cell is not a road, movement is allowed
            return True

        # Find the path using A* algorithm
        self.path = a_star_search(grid_matrix, start, end, is_path_clear)

        if len(self.path) == 0:
            print(f"Agent {self.unique_id} could not find a path to {end}")

        # Convert path to list of tuples and return it
        return self.path

    def move(self):
        """ 
        Determines if the agent can move to the next cell in the path, and then
        moves
        
        """        
        if len(self.path) == 0:
            # If the path is empty, find a new path
            print(f"Agent {self.unique_id} is looking for a path to {self.destination.get_position()}")
            self.find_path()
        else:
            # If the path is not empty, move to the next cell
            print(f"Agent {self.pos} is moving with path {self.path}")
            # Get the next cell in the path
            next_cell = self.path.pop(0)
            # Get contents of the next cell
            cell = self.model.grid.get_cell_list_contents([next_cell])
            # If the cell is road, move to it
            
            if cell[0].__class__.__name__ == "Road":
                # Check if the road direction is correct
                correct_direction = True
                # if cell[0].direction == "Left":
                #     correct_direction = True if next_cell[0] < self.pos[0] else False
                # elif cell[0].direction == "Right":
                #     correct_direction = True if next_cell[0] > self.pos[0] else False
                # elif cell[0].direction == "Up":
                #     correct_direction = True if next_cell[1] > self.pos[1] else False
                # elif cell[0].direction == "Down":
                #     correct_direction = True if next_cell[1] < self.pos[1] else False
                # If the road direction is correct, move to it
                if correct_direction:
                    self.model.grid.move_agent(self, next_cell)
                else:
                    print(f"Agent {self.unique_id} is trying to move to {next_cell} but the road direction is {cell[0].direction}")
                    # Delete the path and find a new one
                    self.path = []
                    self.find_path()
            # If the cell is not road, find a new path
            elif cell[0].__class__.__name__ == "Destination":
                print(f"Agent {self.unique_id} has reached its destination")
                self.model.grid.move_agent(self, next_cell)
                self.path = []
            elif cell[0].__class__.__name__ == "Traffic_Light":
                # Check if the traffic light is green
                if cell[0].state:
                    self.model.grid.move_agent(self, next_cell)
                else:
                    print(f"Agent {self.unique_id} is trying to move to {next_cell} but the traffic light is red")
                    # Delete the path and find a new one
                    self.path = []
                    self.find_path()
            else:
                print(f"Agent {self.unique_id} is trying to move to {next_cell} but the cell is not road")


    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # Agent design:
        # 1. If semaphores are green, move
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
