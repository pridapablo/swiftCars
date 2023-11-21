from mesa import Agent
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.heuristic import manhattan
import random

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
        # Create a grid with the city streets (non-road cells are considered
        # obstacles)
        grid_matrix = []
        grid_height = self.model.height
        grid_width = self.model.width

        for y in range(grid_height):
            row = []
            for x in range(grid_width):
                cell = self.model.grid.get_cell_list_contents([(x, y)])
                if cell[0].__class__.__name__ == "Obstacle":
                    row.append(0) # 0 - obstacle
                else:
                    row.append(1) # 1 - walkable
            grid_matrix.append(row)

        grid = Grid(matrix=grid_matrix)
        print("Grid Matrix:")
        for row in reversed(grid_matrix):
            print(' '.join(str(cell) for cell in row))

        # Create a start and end node
        start = grid.node(*self.pos)
        end = grid.node(*self.destination.get_position())

        # Create the finder
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, _ = finder.find_path(start, end, grid)

        if len(path) == 0:
            print(f"Agent {self.unique_id} could not find a path to {self.destination.get_position()}")

        self.path = [(x, y) for x, y in path][1:]

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
            print(f"Agent {self.unique_id} is moving to {self.path[0]}")
            next_cell = self.path.pop(0)
            self.model.grid.move_agent(self, next_cell)

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
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
        pass

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
