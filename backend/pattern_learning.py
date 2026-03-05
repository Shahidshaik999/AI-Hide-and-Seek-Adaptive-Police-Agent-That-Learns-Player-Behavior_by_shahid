"""
Pattern Learning Module
Analyzes player movement patterns and calculates transition probabilities
"""

from collections import defaultdict, Counter
from typing import List, Dict, Tuple
import json


class PatternLearner:
    def __init__(self):
        # Store movement sequences
        self.move_history = []
        
        # Transition counts: {(prev_move, current_move): count}
        self.bigram_counts = defaultdict(int)
        
        # Trigram counts: {(move1, move2, move3): count}
        self.trigram_counts = defaultdict(int)
        
        # Single move frequencies
        self.unigram_counts = Counter()
        
        # Position-based patterns
        self.position_patterns = defaultdict(list)
    
    def add_move(self, move: str, position: Tuple[int, int] = None):
        """Add a new move to the learning system"""
        self.move_history.append(move)
        self.unigram_counts[move] += 1
        
        # Update bigrams
        if len(self.move_history) >= 2:
            prev_move = self.move_history[-2]
            self.bigram_counts[(prev_move, move)] += 1
        
        # Update trigrams
        if len(self.move_history) >= 3:
            move1 = self.move_history[-3]
            move2 = self.move_history[-2]
            self.trigram_counts[(move1, move2, move)] += 1
        
        # Store position patterns
        if position:
            self.position_patterns[position].append(move)
    
    def get_transition_probability(self, prev_move: str, next_move: str) -> float:
        """Calculate P(next_move | prev_move)"""
        # Count how many times prev_move occurred
        prev_count = sum(count for (p, _), count in self.bigram_counts.items() if p == prev_move)
        
        if prev_count == 0:
            return 0.0
        
        # Count how many times prev_move -> next_move occurred
        transition_count = self.bigram_counts.get((prev_move, next_move), 0)
        
        return transition_count / prev_count
    
    def predict_next_move(self, recent_moves: List[str]) -> Dict[str, float]:
        """
        Predict next move based on recent history
        Returns probability distribution over possible moves
        """
        predictions = defaultdict(float)
        possible_moves = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        
        # If we have no history, return uniform distribution
        if not recent_moves or not self.move_history:
            return {move: 0.25 for move in possible_moves}
        
        # Try trigram prediction first (most specific)
        if len(recent_moves) >= 2:
            move1, move2 = recent_moves[-2], recent_moves[-1]
            trigram_total = sum(
                count for (m1, m2, _), count in self.trigram_counts.items()
                if m1 == move1 and m2 == move2
            )
            
            if trigram_total > 0:
                for move in possible_moves:
                    count = self.trigram_counts.get((move1, move2, move), 0)
                    predictions[move] = count / trigram_total
                
                # If we have strong trigram predictions, use them
                if max(predictions.values()) > 0:
                    return dict(predictions)
        
        # Fall back to bigram prediction
        if len(recent_moves) >= 1:
            prev_move = recent_moves[-1]
            bigram_total = sum(
                count for (p, _), count in self.bigram_counts.items()
                if p == prev_move
            )
            
            if bigram_total > 0:
                for move in possible_moves:
                    count = self.bigram_counts.get((prev_move, move), 0)
                    predictions[move] = count / bigram_total
                
                if max(predictions.values()) > 0:
                    return dict(predictions)
        
        # Fall back to unigram (overall frequency)
        total = sum(self.unigram_counts.values())
        if total > 0:
            for move in possible_moves:
                predictions[move] = self.unigram_counts.get(move, 0) / total
            return dict(predictions)
        
        # Default: uniform distribution
        return {move: 0.25 for move in possible_moves}
    
    def get_most_common_sequences(self, n: int = 5) -> List[Tuple[Tuple[str, str], int]]:
        """Get the n most common bigram sequences"""
        # Sort bigrams by count and return top n
        sorted_bigrams = sorted(self.bigram_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_bigrams[:n]
    
    def get_pattern_confidence(self) -> float:
        """
        Calculate confidence in pattern predictions (0-1)
        Higher values mean more consistent patterns
        """
        if len(self.move_history) < 10:
            return 0.0
        
        # Calculate entropy of bigram distribution
        total_bigrams = sum(self.bigram_counts.values())
        if total_bigrams == 0:
            return 0.0
        
        # Find the most common pattern strength
        max_count = max(self.bigram_counts.values()) if self.bigram_counts else 0
        confidence = min(max_count / total_bigrams * 2, 1.0)
        
        return confidence
    
    def analyze_playstyle(self) -> str:
        """
        Classify player's playstyle based on movement patterns
        Returns: 'aggressive', 'stealth', 'defensive', or 'unpredictable'
        """
        if len(self.move_history) < 20:
            return 'learning'
        
        # Calculate movement diversity
        unique_bigrams = len(self.bigram_counts)
        total_moves = len(self.move_history)
        diversity = unique_bigrams / max(total_moves - 1, 1)
        
        # Calculate direction changes
        direction_changes = 0
        for i in range(1, len(self.move_history)):
            if self.move_history[i] != self.move_history[i-1]:
                direction_changes += 1
        
        change_rate = direction_changes / max(len(self.move_history) - 1, 1)
        
        # Classify based on patterns
        if change_rate > 0.7 and diversity > 0.5:
            return 'aggressive'  # Lots of direction changes, unpredictable
        elif change_rate < 0.3:
            return 'defensive'  # Stays in one direction, cautious
        elif diversity < 0.3:
            return 'predictable'  # Repeats same patterns
        else:
            return 'balanced'  # Mix of strategies
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about learned patterns"""
        return {
            'total_moves': len(self.move_history),
            'unique_bigrams': len(self.bigram_counts),
            'unique_trigrams': len(self.trigram_counts),
            'most_common_moves': dict(self.unigram_counts.most_common(4)),
            'most_common_sequences': [
                {'sequence': list(seq), 'count': count}
                for seq, count in self.get_most_common_sequences(5)
            ],
            'pattern_confidence': round(self.get_pattern_confidence(), 3),
            'playstyle': self.analyze_playstyle()
        }
    
    def save_to_file(self, filename: str):
        """Save learned patterns to file"""
        data = {
            'move_history': self.move_history,
            'bigram_counts': {str(k): v for k, v in self.bigram_counts.items()},
            'trigram_counts': {str(k): v for k, v in self.trigram_counts.items()},
            'unigram_counts': dict(self.unigram_counts)
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load learned patterns from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.move_history = data.get('move_history', [])
            self.unigram_counts = Counter(data.get('unigram_counts', {}))
            
            # Reconstruct bigrams
            self.bigram_counts = defaultdict(int)
            for k, v in data.get('bigram_counts', {}).items():
                key = eval(k)  # Convert string back to tuple
                self.bigram_counts[key] = v
            
            # Reconstruct trigrams
            self.trigram_counts = defaultdict(int)
            for k, v in data.get('trigram_counts', {}).items():
                key = eval(k)
                self.trigram_counts[key] = v
                
        except FileNotFoundError:
            pass  # Start fresh if file doesn't exist
