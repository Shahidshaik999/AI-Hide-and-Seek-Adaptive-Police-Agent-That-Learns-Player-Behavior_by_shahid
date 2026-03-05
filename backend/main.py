"""
FastAPI Backend for AI Hide and Seek Game
Provides endpoints for AI decision making and pattern learning
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import uvicorn

from ai_agent import PoliceAI

# Initialize FastAPI app
app = FastAPI(
    title="AI Hide and Seek API",
    description="Backend API for learning police agent",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agent
police_ai = PoliceAI()

# Request/Response Models
class MoveRecord(BaseModel):
    round: int
    move: str
    position: Optional[Tuple[int, int]] = None

class PredictRequest(BaseModel):
    history: List[str]

class AIStrategyRequest(BaseModel):
    player_pos: Tuple[int, int]
    police_pos: Tuple[int, int]
    recent_moves: List[str]
    round: int
    obstacles: Optional[List[Tuple[int, int]]] = None
    difficulty: Optional[int] = None  # 1=Random, 2=Chase, 3=Predictive, 4=Advanced

class GameStateUpdate(BaseModel):
    round: int
    player_score: int
    caught: bool

class DifficultyUpdate(BaseModel):
    difficulty: int  # 1=Random, 2=Chase, 3=Predictive, 4=Advanced


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Hide and Seek Backend",
        "version": "1.0.0"
    }

@app.post("/record_move")
async def record_move(move_data: MoveRecord):
    """
    Record a player move for learning
    
    Args:
        move_data: Contains round number, move direction, and optional position
    
    Returns:
        Confirmation and current learning statistics
    """
    try:
        police_ai.record_player_move(
            move=move_data.move,
            position=move_data.position
        )
        
        # Save learning data periodically
        if len(police_ai.pattern_learner.move_history) % 50 == 0:
            police_ai.save_learning_data()
        
        return {
            "status": "recorded",
            "total_moves_learned": len(police_ai.pattern_learner.move_history),
            "pattern_confidence": police_ai.pattern_learner.get_pattern_confidence()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_move")
async def predict_move(request: PredictRequest):
    """
    Predict player's next move based on history
    
    Args:
        request: Contains recent move history
    
    Returns:
        Probability distribution over possible next moves
    """
    try:
        predictions = police_ai.pattern_learner.predict_next_move(request.history)
        
        # Get the most likely move
        most_likely = max(predictions.items(), key=lambda x: x[1]) if predictions else ("UNKNOWN", 0)
        
        return {
            "predictions": predictions,
            "most_likely_move": most_likely[0],
            "confidence": most_likely[1],
            "pattern_strength": police_ai.pattern_learner.get_pattern_confidence()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai_strategy")
async def get_ai_strategy(request: AIStrategyRequest):
    """
    Get AI agent's next move decision
    
    Args:
        request: Contains player position, police position, recent moves, round, and difficulty
    
    Returns:
        AI decision including direction, strategy, and confidence
    """
    try:
        # Update round number
        police_ai.set_round(request.round)
        
        # Get AI decision with optional difficulty override
        decision = police_ai.decide_move(
            player_pos=request.player_pos,
            police_pos=request.police_pos,
            recent_moves=request.recent_moves,
            obstacles=request.obstacles,
            difficulty=request.difficulty
        )
        
        return decision
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/game_state")
async def update_game_state(state: GameStateUpdate):
    """
    Update game state (round changes, catches, etc.)
    
    Args:
        state: Current game state information
    
    Returns:
        Acknowledgment and updated statistics
    """
    try:
        police_ai.set_round(state.round)
        
        if state.caught:
            police_ai.record_catch()
        
        return {
            "status": "updated",
            "statistics": police_ai.get_statistics()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics():
    """
    Get comprehensive AI learning statistics
    
    Returns:
        Detailed statistics about AI performance and learned patterns
    """
    try:
        stats = police_ai.get_statistics()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patterns")
async def get_patterns():
    """
    Get detailed pattern analysis
    
    Returns:
        Common sequences, playstyle analysis, and pattern statistics
    """
    try:
        patterns = police_ai.pattern_learner.get_statistics()
        
        # Add transition probabilities for common moves
        transitions = {}
        for move1 in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            transitions[move1] = {}
            for move2 in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                prob = police_ai.pattern_learner.get_transition_probability(move1, move2)
                if prob > 0:
                    transitions[move1][move2] = round(prob, 3)
        
        return {
            **patterns,
            'transition_probabilities': transitions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_game():
    """
    Reset the game (keeps learned patterns)
    
    Returns:
        Confirmation message
    """
    try:
        police_ai.reset_round()
        police_ai.set_round(1)
        
        return {
            "status": "reset",
            "message": "Game reset, learned patterns retained"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset_learning")
async def reset_learning():
    """
    Reset all learned patterns (fresh start)
    
    Returns:
        Confirmation message
    """
    try:
        global police_ai
        police_ai = PoliceAI()
        
        return {
            "status": "reset",
            "message": "All learning data cleared"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set_difficulty")
async def set_difficulty(request: DifficultyUpdate):
    """
    Set AI difficulty level
    
    Args:
        request: Difficulty level (1-4)
    
    Returns:
        Confirmation message
    """
    try:
        police_ai.set_difficulty(request.difficulty)
        
        difficulty_names = {
            1: "Random (Easy)",
            2: "Direct Chase (Medium)",
            3: "Predictive (Hard)",
            4: "Advanced (Very Hard)"
        }
        
        return {
            "status": "updated",
            "difficulty": request.difficulty,
            "difficulty_name": difficulty_names.get(request.difficulty, "Unknown")
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/difficulty")
async def get_difficulty():
    """
    Get current AI difficulty level
    
    Returns:
        Current difficulty setting
    """
    try:
        difficulty_names = {
            1: "Random (Easy)",
            2: "Direct Chase (Medium)",
            3: "Predictive (Hard)",
            4: "Advanced (Very Hard)"
        }
        
        return {
            "difficulty": police_ai.difficulty_level,
            "difficulty_name": difficulty_names.get(police_ai.difficulty_level, "Unknown")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Load saved learning data on startup"""
    try:
        police_ai.load_learning_data()
        print("✓ Loaded previous learning data")
    except:
        print("✓ Starting with fresh learning data")

@app.on_event("shutdown")
async def shutdown_event():
    """Save learning data on shutdown"""
    try:
        police_ai.save_learning_data()
        print("✓ Saved learning data")
    except:
        print("✗ Could not save learning data")


if __name__ == "__main__":
    print("🚀 Starting AI Hide and Seek Backend...")
    print("📊 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
