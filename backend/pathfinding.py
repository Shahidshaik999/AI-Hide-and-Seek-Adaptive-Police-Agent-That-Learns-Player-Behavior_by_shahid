"""
A* Pathfinding Algorithm
Allows police AI to navigate around obstacles intelligently
"""

import heapq
from typing import Tuple, List, Optional, Set


class Node:
    """Node class for A* pathfinding"""
    
    def __init__(self, position: Tuple[int, int], parent: Optional['Node'] = None):
        self.position = position
        self.parent = parent
        self.g = 0  # Distance from start node
        self.h = 0  # Heuristic distance to goal
        self.f = 0  # Total cost (g + h)
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __lt__(self, other):
        return self.f < other.f
    
    def __hash__(self):
        return hash(self.position)


class AStarPathfinder:
    """A* pathfinding implementation for grid-based navigation"""
    
    def __init__(self, grid_size: int = 10):
        self.grid_size = grid_size
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate Manhattan distance heuristic
        Manhattan distance is optimal for grid-based movement (4 directions)
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(
        self, 
        position: Tuple[int, int], 
        obstacles: Set[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions (up, down, left, right)
        """
        x, y = position
        neighbors = []
        
        # Four directions: up, down, left, right
        directions = [
            (x, y - 1),  # UP
            (x, y + 1),  # DOWN
            (x - 1, y),  # LEFT
            (x + 1, y),  # RIGHT
        ]
        
        for nx, ny in directions:
            # Check if within grid bounds
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                # Check if not an obstacle
                if (nx, ny) not in obstacles:
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        obstacles: List[Tuple[int, int]] = None
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find shortest path from start to goal using A* algorithm
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            obstacles: List of obstacle positions
        
        Returns:
            List of positions representing the path, or None if no path exists
        """
        if obstacles is None:
            obstacles = []
        
        # Convert obstacles to set for O(1) lookup
        obstacle_set = set(obstacles)
        
        # Check if start or goal is an obstacle
        if start in obstacle_set or goal in obstacle_set:
            return None
        
        # Check if start equals goal
        if start == goal:
            return [start]
        
        # Initialize open and closed lists
        open_list = []
        closed_set = set()
        
        # Create start node
        start_node = Node(start)
        start_node.g = 0
        start_node.h = self.heuristic(start, goal)
        start_node.f = start_node.g + start_node.h
        
        heapq.heappush(open_list, start_node)
        
        # Keep track of nodes in open list for faster lookup
        open_dict = {start: start_node}
        
        # A* main loop
        while open_list:
            # Get node with lowest f score
            current_node = heapq.heappop(open_list)
            del open_dict[current_node.position]
            
            # Add to closed set
            closed_set.add(current_node.position)
            
            # Check if we reached the goal
            if current_node.position == goal:
                # Reconstruct path
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Reverse to get start -> goal
            
            # Generate neighbors
            neighbors = self.get_neighbors(current_node.position, obstacle_set)
            
            for neighbor_pos in neighbors:
                # Skip if already evaluated
                if neighbor_pos in closed_set:
                    continue
                
                # Create neighbor node
                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = current_node.g + 1  # Cost is 1 per step
                neighbor_node.h = self.heuristic(neighbor_pos, goal)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                
                # Check if neighbor is in open list with higher g score
                if neighbor_pos in open_dict:
                    existing_node = open_dict[neighbor_pos]
                    if neighbor_node.g < existing_node.g:
                        # Update existing node
                        existing_node.g = neighbor_node.g
                        existing_node.f = neighbor_node.f
                        existing_node.parent = current_node
                        # Re-heapify
                        heapq.heapify(open_list)
                else:
                    # Add to open list
                    heapq.heappush(open_list, neighbor_node)
                    open_dict[neighbor_pos] = neighbor_node
        
        # No path found
        return None
    
    def get_next_move(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        obstacles: List[Tuple[int, int]] = None
    ) -> Optional[str]:
        """
        Get the next move direction to reach goal from start
        
        Args:
            start: Current position
            goal: Target position
            obstacles: List of obstacle positions
        
        Returns:
            Direction string ('UP', 'DOWN', 'LEFT', 'RIGHT') or None
        """
        path = self.find_path(start, goal, obstacles)
        
        if not path or len(path) < 2:
            return None
        
        # Get next position in path
        next_pos = path[1]
        
        # Calculate direction
        dx = next_pos[0] - start[0]
        dy = next_pos[1] - start[1]
        
        if dx > 0:
            return 'RIGHT'
        elif dx < 0:
            return 'LEFT'
        elif dy > 0:
            return 'DOWN'
        elif dy < 0:
            return 'UP'
        
        return None
    
    def get_path_length(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        obstacles: List[Tuple[int, int]] = None
    ) -> int:
        """
        Get the length of the shortest path
        
        Returns:
            Path length, or -1 if no path exists
        """
        path = self.find_path(start, goal, obstacles)
        return len(path) - 1 if path else -1


def visualize_path(
    grid_size: int,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    obstacles: List[Tuple[int, int]],
    path: List[Tuple[int, int]] = None
) -> str:
    """
    Visualize the grid, obstacles, and path (for debugging)
    
    Returns:
        String representation of the grid
    """
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Mark obstacles
    for ox, oy in obstacles:
        if 0 <= ox < grid_size and 0 <= oy < grid_size:
            grid[oy][ox] = '#'
    
    # Mark path
    if path:
        for px, py in path:
            if (px, py) != start and (px, py) != goal:
                grid[py][px] = '*'
    
    # Mark start and goal
    sx, sy = start
    gx, gy = goal
    grid[sy][sx] = 'S'
    grid[gy][gx] = 'G'
    
    # Convert to string
    result = []
    for row in grid:
        result.append(' '.join(row))
    
    return '\n'.join(result)


# Example usage and testing
if __name__ == '__main__':
    # Create pathfinder
    pathfinder = AStarPathfinder(grid_size=10)
    
    # Define test scenario
    start = (1, 1)
    goal = (8, 8)
    obstacles = [
        (3, 3), (3, 4), (3, 5),
        (6, 2), (6, 3),
        (5, 7), (6, 7), (7, 7),
        (2, 8), (8, 2)
    ]
    
    # Find path
    path = pathfinder.find_path(start, goal, obstacles)
    
    if path:
        print("Path found!")
        print(f"Path length: {len(path) - 1} steps")
        print(f"Path: {path}")
        print("\nVisualization:")
        print(visualize_path(10, start, goal, obstacles, path))
        
        # Get next move
        next_move = pathfinder.get_next_move(start, goal, obstacles)
        print(f"\nNext move from start: {next_move}")
    else:
        print("No path found!")
