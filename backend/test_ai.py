"""
Test suite for AI Agent and Pattern Learning
Run with: pytest test_ai.py
"""

import pytest
from ai_agent import PoliceAI
from pattern_learning import PatternLearner


class TestPatternLearner:
    """Test pattern learning functionality"""
    
    def test_initialization(self):
        """Test pattern learner initializes correctly"""
        learner = PatternLearner()
        assert len(learner.move_history) == 0
        assert len(learner.bigram_counts) == 0
        assert len(learner.trigram_counts) == 0
    
    def test_add_move(self):
        """Test adding moves to history"""
        learner = PatternLearner()
        learner.add_move('UP')
        learner.add_move('RIGHT')
        
        assert len(learner.move_history) == 2
        assert learner.move_history == ['UP', 'RIGHT']
    
    def test_bigram_counting(self):
        """Test bigram pattern detection"""
        learner = PatternLearner()
        learner.add_move('UP')
        learner.add_move('UP')
        learner.add_move('RIGHT')
        
        assert learner.bigram_counts[('UP', 'UP')] == 1
        assert learner.bigram_counts[('UP', 'RIGHT')] == 1
    
    def test_trigram_counting(self):
        """Test trigram pattern detection"""
        learner = PatternLearner()
        learner.add_move('UP')
        learner.add_move('UP')
        learner.add_move('RIGHT')
        
        assert learner.trigram_counts[('UP', 'UP', 'RIGHT')] == 1
    
    def test_transition_probability(self):
        """Test transition probability calculation"""
        learner = PatternLearner()
        
        # Add pattern: UP -> RIGHT (3 times), UP -> LEFT (1 time)
        for _ in range(3):
            learner.add_move('UP')
            learner.add_move('RIGHT')
        
        learner.add_move('UP')
        learner.add_move('LEFT')
        
        prob_right = learner.get_transition_probability('UP', 'RIGHT')
        prob_left = learner.get_transition_probability('UP', 'LEFT')
        
        assert prob_right == 0.75  # 3/4
        assert prob_left == 0.25   # 1/4
    
    def test_predict_next_move(self):
        """Test move prediction"""
        learner = PatternLearner()
        
        # Create strong pattern: UP -> RIGHT
        for _ in range(10):
            learner.add_move('UP')
            learner.add_move('RIGHT')
        
        predictions = learner.predict_next_move(['UP'])
        
        assert 'RIGHT' in predictions
        assert predictions['RIGHT'] > predictions.get('LEFT', 0)
    
    def test_pattern_confidence(self):
        """Test pattern confidence calculation"""
        learner = PatternLearner()
        
        # No data = no confidence
        assert learner.get_pattern_confidence() == 0.0
        
        # Add consistent pattern
        for _ in range(20):
            learner.add_move('UP')
            learner.add_move('RIGHT')
        
        confidence = learner.get_pattern_confidence()
        assert confidence > 0.0
    
    def test_playstyle_classification(self):
        """Test playstyle analysis"""
        learner = PatternLearner()
        
        # Not enough data
        assert learner.analyze_playstyle() == 'learning'
        
        # Add aggressive pattern (lots of changes)
        moves = ['UP', 'RIGHT', 'DOWN', 'LEFT', 'UP', 'RIGHT', 'DOWN', 'LEFT']
        for _ in range(3):
            for move in moves:
                learner.add_move(move)
        
        playstyle = learner.analyze_playstyle()
        assert playstyle in ['aggressive', 'balanced', 'defensive', 'predictable']
    
    def test_statistics(self):
        """Test statistics generation"""
        learner = PatternLearner()
        
        for _ in range(5):
            learner.add_move('UP')
            learner.add_move('RIGHT')
        
        stats = learner.get_statistics()
        
        assert 'total_moves' in stats
        assert 'unique_bigrams' in stats
        assert 'pattern_confidence' in stats
        assert 'playstyle' in stats
        assert stats['total_moves'] == 10


class TestPoliceAI:
    """Test AI agent functionality"""
    
    def test_initialization(self):
        """Test AI agent initializes correctly"""
        ai = PoliceAI()
        assert ai.round_number == 1
        assert ai.catch_count == 0
        assert ai.move_count == 0
    
    def test_distance_calculation(self):
        """Test Manhattan distance calculation"""
        ai = PoliceAI()
        
        distance = ai.calculate_distance((0, 0), (3, 4))
        assert distance == 7  # |3-0| + |4-0|
        
        distance = ai.calculate_distance((5, 5), (5, 5))
        assert distance == 0
    
    def test_direction_to_target(self):
        """Test direction calculation"""
        ai = PoliceAI()
        
        # Target is to the right
        direction = ai.get_direction_to_target((0, 0), (5, 0))
        assert direction == 'RIGHT'
        
        # Target is to the left
        direction = ai.get_direction_to_target((5, 0), (0, 0))
        assert direction == 'LEFT'
        
        # Target is above
        direction = ai.get_direction_to_target((0, 5), (0, 0))
        assert direction == 'UP'
        
        # Target is below
        direction = ai.get_direction_to_target((0, 0), (0, 5))
        assert direction == 'DOWN'
    
    def test_random_strategy(self):
        """Test random movement strategy (rounds 1-2)"""
        ai = PoliceAI()
        ai.set_round(1)
        
        decision = ai.decide_move(
            player_pos=(5, 5),
            police_pos=(3, 3),
            recent_moves=[]
        )
        
        assert decision['strategy'] == 'random'
        assert decision['direction'] in ['UP', 'DOWN', 'LEFT', 'RIGHT']
        assert decision['confidence'] == 0.0
    
    def test_direct_chase_strategy(self):
        """Test direct chase strategy (rounds 3-4)"""
        ai = PoliceAI()
        ai.set_round(3)
        
        decision = ai.decide_move(
            player_pos=(5, 5),
            police_pos=(3, 3),
            recent_moves=[]
        )
        
        assert decision['strategy'] == 'direct_chase'
        assert decision['direction'] in ['RIGHT', 'DOWN']  # Moving towards player
    
    def test_predictive_strategy(self):
        """Test predictive strategy (round 5+)"""
        ai = PoliceAI()
        ai.set_round(5)
        
        # Add some learning data
        for _ in range(20):
            ai.record_player_move('UP')
            ai.record_player_move('RIGHT')
        
        decision = ai.decide_move(
            player_pos=(5, 5),
            police_pos=(3, 3),
            recent_moves=['UP', 'RIGHT', 'UP']
        )
        
        assert decision['strategy'] in ['predictive_intercept', 'blocking', 'adaptive_chase']
        assert decision['confidence'] >= 0.0
    
    def test_position_prediction(self):
        """Test player position prediction"""
        ai = PoliceAI()
        
        # Add pattern: always move RIGHT
        for _ in range(10):
            ai.record_player_move('RIGHT')
        
        predicted_pos = ai.predict_player_position(
            current_pos=(5, 5),
            recent_moves=['RIGHT', 'RIGHT'],
            steps_ahead=2
        )
        
        # Should predict player moving right
        assert predicted_pos[0] > 5  # X coordinate increased
    
    def test_record_catch(self):
        """Test catch recording"""
        ai = PoliceAI()
        
        assert ai.catch_count == 0
        ai.record_catch()
        assert ai.catch_count == 1
    
    def test_statistics(self):
        """Test statistics generation"""
        ai = PoliceAI()
        ai.set_round(3)
        ai.record_catch()
        ai.record_player_move('UP')
        ai.record_player_move('RIGHT')
        
        stats = ai.get_statistics()
        
        assert 'round' in stats
        assert 'catches' in stats
        assert 'learning_stats' in stats
        assert stats['round'] == 3
        assert stats['catches'] == 1


class TestIntegration:
    """Integration tests for complete AI system"""
    
    def test_learning_improves_prediction(self):
        """Test that learning improves prediction accuracy"""
        ai = PoliceAI()
        
        # Create consistent pattern
        pattern = ['UP', 'UP', 'RIGHT', 'RIGHT', 'DOWN']
        
        # Train with pattern
        for _ in range(10):
            for move in pattern:
                ai.record_player_move(move)
        
        # Test prediction
        predictions = ai.pattern_learner.predict_next_move(['UP', 'UP'])
        
        # Should predict RIGHT with high probability
        assert predictions['RIGHT'] > 0.5
    
    def test_ai_adapts_to_round(self):
        """Test that AI strategy changes with rounds"""
        ai = PoliceAI()
        
        # Round 1: Random
        ai.set_round(1)
        decision1 = ai.decide_move((5, 5), (3, 3), [])
        assert decision1['strategy'] == 'random'
        
        # Round 3: Direct chase
        ai.set_round(3)
        decision2 = ai.decide_move((5, 5), (3, 3), [])
        assert decision2['strategy'] == 'direct_chase'
        
        # Round 5+: Adaptive (with learning data)
        ai.set_round(5)
        for _ in range(20):
            ai.record_player_move('UP')
        decision3 = ai.decide_move((5, 5), (3, 3), ['UP', 'UP'])
        assert decision3['strategy'] in ['predictive_intercept', 'blocking', 'adaptive_chase']
    
    def test_full_game_simulation(self):
        """Simulate a full game"""
        ai = PoliceAI()
        player_pos = [5, 5]
        police_pos = [0, 0]
        
        for round_num in range(1, 6):
            ai.set_round(round_num)
            
            # Simulate 10 moves per round
            for _ in range(10):
                # Player makes a move
                move = 'RIGHT'  # Simple pattern
                ai.record_player_move(move)
                player_pos[0] += 1
                
                # AI decides move
                decision = ai.decide_move(
                    tuple(player_pos),
                    tuple(police_pos),
                    ['RIGHT']
                )
                
                assert decision['direction'] in ['UP', 'DOWN', 'LEFT', 'RIGHT']
        
        # Check that AI learned something
        stats = ai.get_statistics()
        assert stats['learning_stats']['total_moves'] == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
