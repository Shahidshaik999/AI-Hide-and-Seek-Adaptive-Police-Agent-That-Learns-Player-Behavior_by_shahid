"""
AI Agent Module
Controls police agent behavior and decision making
"""

import random
from typing import Tuple, List, Dict
from pattern_learning import PatternLearner
from pathfinding import AStarPathfinder


class PoliceAI:
    def __init__(self):
        self.pattern_learner = PatternLearner()
        self.pathfinder = AStarPathfinder(grid_size=10)
        self.round_number = 1
        self.catch_count = 0
        self.move_count = 0
        self.difficulty_level = 2  # Default: Direct chase (1=Random, 2=Chase, 3=Predictive, 4=Advanced)
        self.use_pathfinding = True  # Enable A* pathfinding by default
        
        # Interception tracking
        self.player_position_history = []  # Track last N positions
        self.player_velocity = (0, 0)  # Current velocity vector
        self.interception_mode = False  # Whether to use interception
        self.speed_multiplier = 1.0  # Police speed advantage
        
        # Proximity-based speed boost
        self.enable_speed_boost = True  # Enable proximity speed boost
        self.current_speed = 1  # Current movement speed (steps per update)
        
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return (dx**2 + dy**2)**0.5
    
    def calculate_manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def calculate_speed_boost(self, player_pos: Tuple[int, int], police_pos: Tuple[int, int]) -> int:
        """
        Calculate police speed based on proximity to player
        
        Distance Rules:
        - distance > 6: Normal speed (1 step per update)
        - distance 3-6: Fast speed (2 steps per update)
        - distance <= 3: CHASE MODE (3 steps per update)
        
        Returns:
            int: Number of steps police should move (1, 2, or 3)
        """
        if not self.enable_speed_boost:
            return 1
        
        # Calculate Euclidean distance
        distance = self.calculate_distance(player_pos, police_pos)
        
        # Apply proximity-based speed rules
        if distance <= 3:
            # CHASE MODE - Very close, maximum speed
            self.current_speed = 3
            return 3
        elif distance <= 6:
            # PURSUIT MODE - Getting close, increased speed
            self.current_speed = 2
            return 2
        else:
            # NORMAL MODE - Far away, normal speed
            self.current_speed = 1
            return 1
    
    def get_direction_to_target(self, current: Tuple[int, int], target: Tuple[int, int]) -> str:
        """Get the best direction to move towards target"""
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        
        # Prioritize the axis with larger distance
        if abs(dx) > abs(dy):
            return 'RIGHT' if dx > 0 else 'LEFT'
        elif abs(dy) > abs(dx):
            return 'DOWN' if dy > 0 else 'UP'
        else:
            # Equal distance, choose randomly
            if dx != 0:
                return 'RIGHT' if dx > 0 else 'LEFT'
            elif dy != 0:
                return 'DOWN' if dy > 0 else 'UP'
            else:
                return random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    
    def get_direction_with_pathfinding(
        self,
        current: Tuple[int, int],
        target: Tuple[int, int],
        obstacles: List[Tuple[int, int]] = None
    ) -> str:
        """
        Get the best direction using A* pathfinding
        Falls back to direct movement if pathfinding fails
        """
        if not self.use_pathfinding or not obstacles:
            return self.get_direction_to_target(current, target)
        
        # Try A* pathfinding
        next_move = self.pathfinder.get_next_move(current, target, obstacles)
        
        if next_move:
            return next_move
        else:
            # Fallback to direct movement if no path found
            return self.get_direction_to_target(current, target)
    
    def predict_player_position(
        self, 
        current_pos: Tuple[int, int], 
        recent_moves: List[str],
        steps_ahead: int = 2
    ) -> Tuple[int, int]:
        """
        Predict where player will be in N steps
        """
        predicted_pos = list(current_pos)
        
        for _ in range(steps_ahead):
            # Get move predictions
            move_probs = self.pattern_learner.predict_next_move(recent_moves)
            
            # Choose most likely move
            if move_probs:
                predicted_move = max(move_probs.items(), key=lambda x: x[1])[0]
                
                # Update predicted position
                if predicted_move == 'UP':
                    predicted_pos[1] -= 1
                elif predicted_move == 'DOWN':
                    predicted_pos[1] += 1
                elif predicted_move == 'LEFT':
                    predicted_pos[0] -= 1
                elif predicted_move == 'RIGHT':
                    predicted_pos[0] += 1
                
                # Add to recent moves for next prediction
                recent_moves = recent_moves[-2:] + [predicted_move]
        
        return tuple(predicted_pos)
    
    def update_player_position_history(self, position: Tuple[int, int]):
        """
        Track player position history for velocity calculation
        Keep last 5 positions
        """
        self.player_position_history.append(position)
        if len(self.player_position_history) > 5:
            self.player_position_history.pop(0)
        
        # Update velocity if we have enough history
        if len(self.player_position_history) >= 2:
            self.player_velocity = self.calculate_velocity()
    
    def calculate_velocity(self) -> Tuple[float, float]:
        """
        Calculate player's movement velocity (direction and speed)
        Returns: (vx, vy) velocity vector
        """
        if len(self.player_position_history) < 2:
            return (0, 0)
        
        # Calculate average velocity over recent positions
        total_vx = 0
        total_vy = 0
        count = 0
        
        for i in range(1, len(self.player_position_history)):
            prev_pos = self.player_position_history[i-1]
            curr_pos = self.player_position_history[i]
            
            vx = curr_pos[0] - prev_pos[0]
            vy = curr_pos[1] - prev_pos[1]
            
            total_vx += vx
            total_vy += vy
            count += 1
        
        if count > 0:
            avg_vx = total_vx / count
            avg_vy = total_vy / count
            return (avg_vx, avg_vy)
        
        return (0, 0)
    
    def predict_future_position_with_velocity(
        self,
        current_pos: Tuple[int, int],
        steps_ahead: int = 3,
        grid_size: int = 10
    ) -> Tuple[int, int]:
        """
        Predict future position based on current velocity
        More accurate than pattern-based prediction for consistent movement
        """
        vx, vy = self.player_velocity
        
        # Predict future position
        future_x = current_pos[0] + int(vx * steps_ahead)
        future_y = current_pos[1] + int(vy * steps_ahead)
        
        # Clamp to grid boundaries
        future_x = max(0, min(grid_size - 1, future_x))
        future_y = max(0, min(grid_size - 1, future_y))
        
        return (future_x, future_y)
    
    def calculate_interception_point(
        self,
        player_pos: Tuple[int, int],
        police_pos: Tuple[int, int],
        player_velocity: Tuple[float, float],
        grid_size: int = 10
    ) -> Tuple[int, int]:
        """
        Calculate optimal interception point
        Uses physics-based interception: where police and player paths will meet
        """
        vx, vy = player_velocity
        
        # If player is stationary, intercept at current position
        if abs(vx) < 0.1 and abs(vy) < 0.1:
            return player_pos
        
        # Calculate time to intercept
        # Assume police moves at same speed as player (or faster with multiplier)
        dx = player_pos[0] - police_pos[0]
        dy = player_pos[1] - police_pos[1]
        
        # Estimate interception time
        # This is a simplified interception calculation
        if abs(vx) > abs(vy):
            # Player moving more horizontally
            if vx != 0:
                time_to_intercept = abs(dx / vx)
            else:
                time_to_intercept = 3
        else:
            # Player moving more vertically
            if vy != 0:
                time_to_intercept = abs(dy / vy)
            else:
                time_to_intercept = 3
        
        # Limit interception time
        time_to_intercept = min(time_to_intercept, 5)
        
        # Calculate interception point
        intercept_x = player_pos[0] + int(vx * time_to_intercept)
        intercept_y = player_pos[1] + int(vy * time_to_intercept)
        
        # Clamp to grid
        intercept_x = max(0, min(grid_size - 1, intercept_x))
        intercept_y = max(0, min(grid_size - 1, intercept_y))
        
        return (intercept_x, intercept_y)
    
    def find_escape_route_block_position(
        self,
        player_pos: Tuple[int, int],
        player_velocity: Tuple[float, float],
        grid_size: int = 10
    ) -> Tuple[int, int]:
        """
        Find position to block player's most likely escape route
        Considers map boundaries and player direction
        """
        vx, vy = player_velocity
        
        # Determine player's general direction
        if abs(vx) > abs(vy):
            # Moving horizontally
            if vx > 0:
                # Moving right - block right side
                block_x = min(grid_size - 1, player_pos[0] + 3)
                block_y = player_pos[1]
            else:
                # Moving left - block left side
                block_x = max(0, player_pos[0] - 3)
                block_y = player_pos[1]
        else:
            # Moving vertically
            if vy > 0:
                # Moving down - block bottom
                block_x = player_pos[0]
                block_y = min(grid_size - 1, player_pos[1] + 3)
            else:
                # Moving up - block top
                block_x = player_pos[0]
                block_y = max(0, player_pos[1] - 3)
        
        return (block_x, block_y)
    
    def get_corner_trap_position(
        self,
        player_pos: Tuple[int, int],
        grid_size: int = 10
    ) -> Tuple[int, int]:
        """
        Identify which corner the player is heading towards
        Position police to trap player in corner
        """
        px, py = player_pos
        
        # Determine closest corner
        corners = [
            (0, 0),  # Top-left
            (grid_size - 1, 0),  # Top-right
            (0, grid_size - 1),  # Bottom-left
            (grid_size - 1, grid_size - 1)  # Bottom-right
        ]
        
        # Find closest corner
        closest_corner = min(corners, key=lambda c: self.calculate_distance(player_pos, c))
        
        # Position police between player and corner
        trap_x = (player_pos[0] + closest_corner[0]) // 2
        trap_y = (player_pos[1] + closest_corner[1]) // 2
        
        return (trap_x, trap_y)
    
    def get_blocking_position(
        self,
        player_pos: Tuple[int, int],
        police_pos: Tuple[int, int],
        recent_moves: List[str]
    ) -> Tuple[int, int]:
        """
        Calculate position to block player's likely escape route
        """
        # Predict where player is going
        predicted_pos = self.predict_player_position(player_pos, recent_moves, steps_ahead=3)
        
        # Find position between current player and predicted position
        block_x = (player_pos[0] + predicted_pos[0]) // 2
        block_y = (player_pos[1] + predicted_pos[1]) // 2
        
        return (block_x, block_y)
    
    def decide_move(
        self,
        player_pos: Tuple[int, int],
        police_pos: Tuple[int, int],
        recent_moves: List[str],
        obstacles: List[Tuple[int, int]] = None,
        difficulty: int = None
    ) -> Dict:
        """
        Main decision function with INTERCEPTION STRATEGIES and SPEED BOOST
        
        Difficulty Levels:
        1 - Random: Police moves randomly (easy)
        2 - Direct Chase: Police always moves toward player with A* (medium)
        3 - Velocity Interception: Uses velocity tracking and future prediction (hard)
        4 - Advanced Interception: Full interception with blocking and trapping (very hard)
        
        Returns: {
            'direction': str,
            'strategy': str,
            'confidence': float,
            'prediction': dict,
            'speed': int (1, 2, or 3 based on proximity),
            'distance': float
        }
        """
        self.move_count += 1
        obstacles = obstacles or []
        
        # Update player position history for velocity tracking
        self.update_player_position_history(player_pos)
        
        # Calculate proximity-based speed boost
        speed = self.calculate_speed_boost(player_pos, police_pos)
        distance = self.calculate_distance(player_pos, police_pos)
        
        # Use provided difficulty or fall back to instance difficulty
        if difficulty is not None:
            current_difficulty = difficulty
        else:
            current_difficulty = self.difficulty_level
        
        # LEVEL 1: Random Movement (Easy)
        if current_difficulty == 1:
            direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
            return {
                'direction': direction,
                'strategy': 'random',
                'confidence': 0.0,
                'prediction': None,
                'difficulty': 1,
                'speed': speed,
                'distance': distance
            }
        
        # LEVEL 2: Direct Chase with A* (Medium)
        elif current_difficulty == 2:
            direction = self.get_direction_with_pathfinding(police_pos, player_pos, obstacles)
            return {
                'direction': direction,
                'strategy': 'direct_chase_astar' if obstacles else 'direct_chase',
                'confidence': 0.5,
                'prediction': None,
                'difficulty': 2,
                'speed': speed,
                'distance': distance
            }
        
        # LEVEL 3: VELOCITY-BASED INTERCEPTION (Hard)
        elif current_difficulty == 3:
            # Calculate player velocity
            vx, vy = self.player_velocity
            velocity_magnitude = (vx**2 + vy**2)**0.5
            
            # If player is moving consistently, use velocity-based interception
            if velocity_magnitude > 0.3:
                # Predict future position based on velocity
                future_pos = self.predict_future_position_with_velocity(
                    player_pos,
                    steps_ahead=3
                )
                
                # Calculate interception point
                intercept_point = self.calculate_interception_point(
                    player_pos,
                    police_pos,
                    self.player_velocity
                )
                
                # Choose target: interception point if closer, otherwise future position
                dist_to_intercept = self.calculate_distance(police_pos, intercept_point)
                dist_to_future = self.calculate_distance(police_pos, future_pos)
                
                if dist_to_intercept < dist_to_future:
                    target = intercept_point
                    strategy = 'velocity_intercept'
                else:
                    target = future_pos
                    strategy = 'velocity_prediction'
                
                direction = self.get_direction_with_pathfinding(police_pos, target, obstacles)
                
                return {
                    'direction': direction,
                    'strategy': strategy + ('_astar' if obstacles else ''),
                    'confidence': min(velocity_magnitude, 1.0),
                    'prediction': {
                        'future_position': future_pos,
                        'interception_point': intercept_point,
                        'velocity': self.player_velocity,
                        'target_position': target
                    },
                    'difficulty': 3,
                    'speed': speed,
                    'distance': distance
                }
            else:
                # Player not moving consistently, fall back to pattern prediction
                confidence = self.pattern_learner.get_pattern_confidence()
                
                if confidence > 0.2 and len(recent_moves) >= 2:
                    predicted_pos = self.predict_player_position(
                        player_pos,
                        recent_moves,
                        steps_ahead=2
                    )
                    target = predicted_pos
                    strategy = 'pattern_prediction'
                else:
                    target = player_pos
                    strategy = 'adaptive_chase'
                
                direction = self.get_direction_with_pathfinding(police_pos, target, obstacles)
                
                return {
                    'direction': direction,
                    'strategy': strategy + ('_astar' if obstacles else ''),
                    'confidence': confidence,
                    'prediction': {
                        'predicted_position': target,
                        'target_position': target
                    },
                    'difficulty': 3,
                    'speed': speed,
                    'distance': distance
                }
        
        # LEVEL 4: ADVANCED INTERCEPTION (Very Hard)
        # Combines velocity tracking, pattern learning, blocking, and trapping
        else:
            vx, vy = self.player_velocity
            velocity_magnitude = (vx**2 + vy**2)**0.5
            pattern_confidence = self.pattern_learner.get_pattern_confidence()
            
            # Strategy selection based on game state
            current_distance = self.calculate_distance(police_pos, player_pos)
            
            # STRATEGY 1: Close range - Direct intercept
            if current_distance <= 3:
                if velocity_magnitude > 0.3:
                    # Use velocity-based interception
                    target = self.calculate_interception_point(
                        player_pos,
                        police_pos,
                        self.player_velocity
                    )
                    strategy = 'close_intercept'
                else:
                    # Direct chase
                    target = player_pos
                    strategy = 'close_chase'
            
            # STRATEGY 2: Medium range - Block escape routes
            elif current_distance <= 6:
                if velocity_magnitude > 0.3:
                    # Block the escape route
                    target = self.find_escape_route_block_position(
                        player_pos,
                        self.player_velocity
                    )
                    strategy = 'escape_blocking'
                elif pattern_confidence > 0.4 and len(recent_moves) >= 2:
                    # Use pattern-based blocking
                    target = self.get_blocking_position(player_pos, police_pos, recent_moves)
                    strategy = 'pattern_blocking'
                else:
                    # Predict future position
                    target = self.predict_future_position_with_velocity(
                        player_pos,
                        steps_ahead=3
                    )
                    strategy = 'future_intercept'
            
            # STRATEGY 3: Long range - Corner trapping
            else:
                # Check if player is near a corner
                corners = [(0, 0), (9, 0), (0, 9), (9, 9)]
                min_corner_dist = min(self.calculate_distance(player_pos, c) for c in corners)
                
                if min_corner_dist <= 3:
                    # Player near corner - trap them
                    target = self.get_corner_trap_position(player_pos)
                    strategy = 'corner_trap'
                elif velocity_magnitude > 0.3:
                    # Long-range interception
                    target = self.calculate_interception_point(
                        player_pos,
                        police_pos,
                        self.player_velocity,
                        grid_size=10
                    )
                    strategy = 'long_intercept'
                else:
                    # Predict with patterns
                    if pattern_confidence > 0.3 and len(recent_moves) >= 2:
                        target = self.predict_player_position(
                            player_pos,
                            recent_moves,
                            steps_ahead=4
                        )
                        strategy = 'long_prediction'
                    else:
                        target = player_pos
                        strategy = 'long_chase'
            
            # Get direction with pathfinding
            direction = self.get_direction_with_pathfinding(police_pos, target, obstacles)
            
            # Calculate combined confidence
            combined_confidence = (velocity_magnitude * 0.6 + pattern_confidence * 0.4)
            
            return {
                'direction': direction,
                'strategy': strategy + ('_astar' if obstacles else ''),
                'confidence': min(combined_confidence, 1.0),
                'prediction': {
                    'target_position': target,
                    'velocity': self.player_velocity,
                    'velocity_magnitude': velocity_magnitude,
                    'pattern_confidence': pattern_confidence,
                    'distance': current_distance
                },
                'difficulty': 4,
                'speed': speed,
                'distance': distance
            }
    
    def set_difficulty(self, level: int):
        """Set AI difficulty level (1-4)"""
        if 1 <= level <= 4:
            self.difficulty_level = level
        else:
            raise ValueError("Difficulty must be between 1 and 4")
    
    def set_pathfinding(self, enabled: bool):
        """Enable or disable A* pathfinding"""
        self.use_pathfinding = enabled
    
    def set_speed_boost(self, enabled: bool):
        """Enable or disable proximity-based speed boost"""
        self.enable_speed_boost = enabled
        if not enabled:
            self.current_speed = 1
    
    def get_path_to_target(
        self,
        police_pos: Tuple[int, int],
        target_pos: Tuple[int, int],
        obstacles: List[Tuple[int, int]] = None
    ) -> List[Tuple[int, int]]:
        """Get the full path from police to target using A*"""
        if not obstacles:
            return None
        return self.pathfinder.find_path(police_pos, target_pos, obstacles)
    
    def record_player_move(self, move: str, position: Tuple[int, int] = None):
        """Record a player move for learning"""
        self.pattern_learner.add_move(move, position)
    
    def record_catch(self):
        """Record that police caught the player"""
        self.catch_count += 1
    
    def set_round(self, round_num: int):
        """Update current round number"""
        self.round_number = round_num
    
    def get_statistics(self) -> Dict:
        """Get comprehensive AI statistics"""
        pattern_stats = self.pattern_learner.get_statistics()
        
        return {
            'round': self.round_number,
            'catches': self.catch_count,
            'total_moves': self.move_count,
            'catch_rate': round(self.catch_count / max(self.move_count, 1), 3),
            'learning_stats': pattern_stats
        }
    
    def reset_round(self):
        """Reset for new round (but keep learned patterns)"""
        self.move_count = 0
    
    def save_learning_data(self, filename: str = 'player_data.json'):
        """Save learned patterns to file"""
        self.pattern_learner.save_to_file(filename)
    
    def load_learning_data(self, filename: str = 'player_data.json'):
        """Load learned patterns from file"""
        self.pattern_learner.load_from_file(filename)
