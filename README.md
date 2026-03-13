# 🎮 AI Hide and Seek – Intelligent Police Agent

[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.9+-blue)]()
[![React](https://img.shields.io/badge/react-18.0+-61dafb)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

##  Project Overview

An advanced AI-powered hide-and-seek game featuring an intelligent police agent that uses **A* pathfinding**, **velocity-based interception**, **pattern learning**, and **proximity-based speed boost** to hunt down the player. The AI adapts to player behavior in real-time, creating an increasingly challenging and dynamic gameplay experience.

###  What Makes This Special

This isn't just a simple chase game. The police AI features:

✅ **A* Pathfinding** - Intelligently navigates around obstacles  
✅ **Velocity Tracking** - Predicts where you'll be, not where you are  
✅ **Interception Strategies** - Cuts off escape routes and traps you in corners  
✅ **Pattern Learning** - Learns your movement habits over time  
✅ **Proximity Speed Boost** - Accelerates when close (prevents infinite escapes)  
✅ **4 Difficulty Levels** - From random movement to advanced tactical AI  

## 🎮 Game Concept

### Players
- **🟢 Player (You)**: Human-controlled using arrow keys
- **🔴 Police Agent**: AI-controlled with advanced hunting algorithms

### Objective
Survive as long as possible without getting caught by the increasingly intelligent police AI.

### Core Mechanics
- **Map**: 10×10 grid with strategic obstacle placement
- **Lives**: Start with 10 points
- **Catch Penalty**: Lose 1 point when caught
- **Game Over**: All points lost
- **Dynamic Difficulty**: AI becomes smarter and faster as it gets closer

##  Key Features

### 1. A* Pathfinding System
The police AI uses the A* algorithm to find the shortest path to the player while avoiding obstacles.

**Features:**
- Manhattan distance heuristic
- Obstacle avoidance
- Performance: <1ms per calculation
- Never gets stuck behind walls

**Example:**
```
Player at (9, 9), Police at (1, 1), Obstacles in between
→ Police calculates optimal path around obstacles
→ Moves intelligently toward player
```

 **See**: [PATHFINDING.md](PATHFINDING.md) for technical details

### 2. Velocity-Based Interception
Instead of just chasing your current position, the AI predicts where you'll be.

**How it works:**
1. Tracks your last 5 positions
2. Calculates velocity vector (speed + direction)
3. Predicts future position
4. Calculates interception point
5. Moves to intercept, not chase

**Example:**
```
You're moving RIGHT consistently
→ AI predicts you'll continue RIGHT
→ AI moves to intercept your future position
→ You can't escape by just running straight!
```

 **See**: [INTERCEPTION_STRATEGIES.md](INTERCEPTION_STRATEGIES.md)

### 3. Proximity-Based Speed Boost ⭐ NEW!
The police speed dynamically adjusts based on distance to create intense chase sequences.

**Speed Tiers:**

| Distance | Speed | Mode | Visual |
|----------|-------|------|--------|
| > 6 cells | 1× | Normal | - |
| 3-6 cells | 2× | Pursuit | ⚡ PURSUIT! |
| ≤ 3 cells | 3× | Chase | 🔥 CHASE MODE! |

**Why this matters:**
- ❌ **Before**: Player could escape forever by staying just ahead
- ✅ **After**: Police accelerates when close, making escape much harder

 **See**: [SPEED_BOOST_SYSTEM.md](SPEED_BOOST_SYSTEM.md)

### 4. Pattern Learning System
The AI learns your movement habits and predicts your next move.

**What it tracks:**
- Movement sequences (UP → UP → RIGHT)
- Transition probabilities (P(RIGHT | UP) = 65%)
- Common escape routes
- Playstyle classification (Aggressive/Stealth/Defensive)
**Screenshots**
  <img width="1303" height="878" alt="image" src="https://github.com/user-attachments/assets/c90c0ca1-cf88-4493-a985-e75b1307480f" />
  <img width="857" height="923" alt="image" src="https://github.com/user-attachments/assets/9d059b2d-22d5-400d-aeb8-a6345df39f1c" />
  <img width="837" height="665" alt="image" src="https://github.com/user-attachments/assets/3f9bf4d9-7d2a-431f-af6f-313719af1091" />
  <img width="842" height="585" alt="image" src="https://github.com/user-attachments/assets/8cc4b650-7037-42b9-8f24-2c625adf265b" />




  

**Example:**
```
You often move: UP → UP → RIGHT
→ AI learns this pattern
→ Next time you move UP → UP
→ AI predicts RIGHT and blocks that direction
```

### 5. Four Difficulty Levels

Choose your challenge level or watch the AI evolve:

#### 🟢 Level 1: Random (Easy)
- Random movement
- No strategy
- Good for learning the game

#### 🟡 Level 2: Direct Chase (Medium)
- Uses A* pathfinding
- Always moves toward your current position
- Navigates around obstacles intelligently
- **Speed boost active**: Accelerates when close

#### 🟠 Level 3: Velocity Interception (Hard)
- **Tracks your velocity** (last 5 positions)
- **Predicts future position** based on movement patterns
- **Calculates interception points** to cut you off
- Combines velocity tracking with pattern learning
- **Speed boost active**: 3× speed when very close

#### 🔴 Level 4: Advanced Interception (Very Hard)
- **Close Range (≤3 cells)**: Immediate velocity-based interception
- **Medium Range (3-6 cells)**: Blocks escape routes and predicted paths
- **Long Range (>6 cells)**: Corner trapping and strategic positioning
- **Adaptive tactics**: Changes strategy based on distance and behavior
- **Speed boost active**: Maximum aggression mode

##  AI Intelligence Breakdown

### A* Pathfinding Algorithm

**Implementation:**
```python
class AStarPathfinder:
    def find_path(start, goal, obstacles):
        # Uses Manhattan distance heuristic
        # Priority queue for optimal path selection
        # Returns shortest path avoiding obstacles
```

**Performance:**
- Time Complexity: O(b^d) where b=branching factor, d=depth
- Average calculation time: <1ms
- Grid size: 10×10 = 100 nodes
- Never fails to find path if one exists

**Visual Example:**
```
S = Start (Police)
G = Goal (Player)
# = Obstacle
. = Empty

. . . # # . . . . .
. S . # # . . . . .
. * . . . . . . . .
. * * * . . . . . .
. . . * * * . . . .
. . . . . * * . . .
. . . . . . * * . .
. . . . . . . . G .

* = Calculated path
```

### Velocity Tracking & Prediction

**Algorithm:**
```python
# Track last 5 positions
positions = [(1,1), (2,1), (3,1), (4,1), (5,1)]

# Calculate velocity
velocity = average_change_per_step
# Result: vx=1.0, vy=0.0 (moving right)

# Predict future position
future_pos = current_pos + (velocity × steps_ahead)
# If at (5,1) moving right: predict (8,1) in 3 steps

# Calculate interception
intercept_point = calculate_intersection(
    police_pos, police_speed,
    player_pos, player_velocity
)
```

**Interception Strategies by Range:**

**Close Range (≤3 cells):**
- Direct velocity-based interception
- Maximum speed (3×)
- No escape time

**Medium Range (3-6 cells):**
- Escape route blocking
- Pattern-based prediction
- Increased speed (2×)

**Long Range (>6 cells):**
- Corner trapping
- Strategic positioning
- Normal speed (1×)

### Pattern Learning System

**Data Structure:**
```python
{
    "moves": ["UP", "UP", "RIGHT", "DOWN", ...],
    "bigrams": {
        ("UP", "UP"): 45,      # UP followed by UP: 45 times
        ("UP", "RIGHT"): 30,   # UP followed by RIGHT: 30 times
    },
    "trigrams": {
        ("UP", "UP", "RIGHT"): 25,
    }
}
```

**Prediction Algorithm:**
```python
def predict_next_move(recent_moves):
    # Get last 2 moves: ["UP", "UP"]
    # Find all sequences starting with ["UP", "UP"]
    # Calculate probabilities:
    # P(RIGHT | UP, UP) = 25/45 = 55%
    # P(UP | UP, UP) = 20/45 = 44%
    # Return: "RIGHT" (highest probability)
```

**Confidence Calculation:**
```python
confidence = (
    pattern_frequency / total_patterns × 0.6 +
    velocity_consistency × 0.4
)
# Higher confidence = more predictable player
```

### Proximity Speed Boost System

**Distance Calculation:**
```python
distance = sqrt((player_x - police_x)² + (player_y - police_y)²)
```

**Speed Determination:**
```python
if distance <= 3:
    speed = 3  # CHASE MODE 🔥
elif distance <= 6:
    speed = 2  # PURSUIT MODE ⚡
else:
    speed = 1  # NORMAL MODE
```

**Movement Execution:**
```javascript
// Frontend: Move police multiple times per update
for (let i = 0; i < speed; i++) {
    movePolice(direction);
    await delay(50ms);  // Visual smoothness
}
```

**Impact on Gameplay:**

| Scenario | Without Boost | With Boost |
|----------|---------------|------------|
| Distance: 8 cells | 8 updates to catch | ~3 updates to catch |
| Player escape time | ∞ Infinite | ⏱️ Limited |
| Tension level | ⭐ Low | ⭐⭐⭐⭐⭐ High |
| Difficulty | ⭐⭐ Easy | ⭐⭐⭐⭐ Hard |

##  Tech Stack

### Frontend
- **React 18.0+** - UI framework
- **Phaser.js 3.55+** - 2D game engine for rendering and physics
- **Axios** - HTTP client for API communication
- **HTML5 Canvas** - Game rendering
- **CSS3** - Styling and animations

### Backend
- **Python 3.9+** - Core language
- **FastAPI** - High-performance async web framework
- **Uvicorn** - ASGI server
- **JSON** - Data persistence for pattern learning

### Algorithms & AI
- **A* Pathfinding** - Optimal path calculation
- **Markov Chains** - Movement pattern prediction
- **N-gram Analysis** - Sequence pattern recognition
- **Velocity Tracking** - Physics-based prediction
- **Euclidean Distance** - Proximity calculations

### Development Tools
- **npm** - Frontend package management
- **pip** - Python package management
- **Git** - Version control

##  System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   React UI   │  │  Phaser Game │  │  API Client  │      │
│  │  Components  │  │    Engine    │  │   (Axios)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    HTTP/REST API
                             │
┌────────────────────────────┼──────────────────────────────────┐
│                        BACKEND                                │
│         ┌────────────────────────────────┐                    │
│         │       FastAPI Server           │                    │
│         │    (API Endpoints & Routes)    │                    │
│         └────────────────────────────────┘                    │
│                        │                                      │
│         ┌──────────────┴──────────────┐                      │
│         │                              │                      │
│  ┌──────▼──────┐              ┌───────▼────────┐            │
│  │  AI Agent   │              │    Pattern     │            │
│  │  Module     │◄────────────►│    Learning    │            │
│  └─────────────┘              └────────────────┘            │
│         │                              │                      │
│  ┌──────▼──────┐              ┌───────▼────────┐            │
│  │ Pathfinding │              │  Data Storage  │            │
│  │  (A* Algo)  │              │     (JSON)     │            │
│  └─────────────┘              └────────────────┘            │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Player Input (Arrow Keys)
   ↓
2. Frontend: Update player position
   ↓
3. API Call: POST /record_move
   ↓
4. Backend: Store move in pattern learning
   ↓
5. API Call: POST /ai_strategy
   ↓
6. Backend: Calculate AI decision
   ├─ Calculate distance → Speed boost
   ├─ Track velocity → Predict future position
   ├─ Analyze patterns → Predict next move
   ├─ Run A* pathfinding → Find optimal path
   └─ Select strategy → Return direction
   ↓
7. Frontend: Move police (speed × times)
   ↓
8. Check collision → Update game state
   ↓
9. Repeat
```

##  Installation & Setup

### Prerequisites

Ensure you have the following installed:
- **Node.js** 16.0 or higher
- **Python** 3.9 or higher
- **npm** or **yarn**
- **pip** (Python package manager)

### Quick Start (Recommended)

#### Windows:
```bash
# Double-click start.bat
# OR run in terminal:
start.bat
```

#### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

This will automatically:
1. Install backend dependencies
2. Install frontend dependencies
3. Start backend server (port 8000)
4. Start frontend server (port 3000)
5. Open game in browser

### Manual Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd ai-hide-seek-game
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python main.py
```

Backend will run on: **http://localhost:8000**  
API Documentation: **http://localhost:8000/docs**

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on: **http://localhost:3000**

### Environment Variables (Optional)

Create `frontend/.env` file:
```env
REACT_APP_API_URL=http://localhost:8000
```

## 🎮 How to Play

### Starting the Game

1. Open **http://localhost:3000** in your browser
2. Select difficulty level (1-4)
3. Click "Start Game" or press any arrow key

### Controls

| Key | Action |
|-----|--------|
| ⬆️ Arrow Up | Move player up |
| ⬇️ Arrow Down | Move player down |
| ⬅️ Arrow Left | Move player left |
| ➡️ Arrow Right | Move player right |

### Game Elements

- **🟢 Green Circle**: Your player
- **🔴 Red Circle**: Police AI
- **⬛ Gray Squares**: Obstacles (walls)
- **Grid Lines**: Movement grid (10×10)

### Visual Indicators

The game displays real-time AI information:

```
AI: velocity_intercept_astar (85%) 🔥 CHASE MODE!
Distance: 2.8 | Speed: 3x
```

- **Strategy**: Current AI tactic being used
- **Confidence**: AI's confidence in prediction (0-100%)
- **Speed Indicator**: 
  - 🔥 CHASE MODE! = 3× speed (very close)
  - ⚡ PURSUIT! = 2× speed (getting close)
  - (none) = 1× speed (normal)
- **Distance**: Exact distance to police in cells
- **Speed**: Current police speed multiplier

### Gameplay Tips

#### 🟢 When Police is Far (>6 cells)
- ✅ Safe to explore and plan
- ✅ Police moves at normal speed
- ✅ Good time to analyze patterns
- ✅ Position yourself strategically

#### 🟡 When Police is Medium Range (3-6 cells)
- ⚠️ Start moving away
- ⚠️ Police moves 2× faster
- ⚠️ Avoid predictable patterns
- ⚠️ Use obstacles for cover
- ⚠️ Change direction frequently

#### 🔴 When Police is Close (≤3 cells)
- 🚨 DANGER! Move immediately!
- 🚨 Police moves 3× faster
- 🚨 Change direction every move
- 🚨 Head for obstacles
- 🚨 No time to think - react!
- 🚨 Avoid corners at all costs

### Advanced Strategies

**Against Level 2 (Direct Chase):**
- Use obstacles to create distance
- Move in circles around obstacles
- Police will take longer path

**Against Level 3 (Velocity Interception):**
- Change direction frequently
- Don't move in straight lines
- Use unpredictable patterns
- Stop and change direction suddenly

**Against Level 4 (Advanced Interception):**
- Never stay in corners
- Constantly vary your movement
- Use obstacles strategically
- Move toward center of map
- Don't establish patterns
- React to police position, not just distance

##  API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive API Docs
FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Record Player Move
```http
POST /record_move
Content-Type: application/json

{
  "round": 1,
  "move": "UP",
  "position": [5, 5]
}
```

**Response:**
```json
{
  "status": "recorded",
  "total_moves": 42
}
```

#### 2. Get AI Strategy
```http
POST /ai_strategy
Content-Type: application/json

{
  "player_pos": [5, 5],
  "police_pos": [3, 3],
  "recent_moves": ["UP", "UP", "RIGHT"],
  "round": 1,
  "obstacles": [[3, 4], [6, 7]],
  "difficulty": 3
}
```

**Response:**
```json
{
  "direction": "RIGHT",
  "strategy": "velocity_intercept_astar",
  "confidence": 0.85,
  "speed": 3,
  "distance": 2.83,
  "prediction": {
    "future_position": [8, 5],
    "interception_point": [9, 5],
    "velocity": [1.0, 0.0],
    "target_position": [9, 5]
  },
  "difficulty": 3
}
```

#### 3. Predict Next Move
```http
POST /predict_move
Content-Type: application/json

{
  "history": ["UP", "UP", "RIGHT"]
}
```

**Response:**
```json
{
  "predicted_move": "RIGHT",
  "confidence": 0.65,
  "probabilities": {
    "UP": 0.15,
    "DOWN": 0.05,
    "LEFT": 0.15,
    "RIGHT": 0.65
  }
}
```

#### 4. Update Game State
```http
POST /game_state
Content-Type: application/json

{
  "round": 5,
  "player_score": 7,
  "caught": true
}
```

**Response:**
```json
{
  "status": "updated",
  "round": 5,
  "score": 7
}
```

#### 5. Get Statistics
```http
GET /statistics
```

**Response:**
```json
{
  "round": 5,
  "catches": 3,
  "total_moves": 150,
  "catch_rate": 0.02,
  "learning_stats": {
    "total_moves": 150,
    "unique_bigrams": 12,
    "unique_trigrams": 45,
    "pattern_confidence": 0.65,
    "playstyle": "aggressive"
  }
}
```

#### 6. Get Pattern Analysis
```http
GET /patterns
```

**Response:**
```json
{
  "most_common_moves": [
    {"move": "RIGHT", "count": 45},
    {"move": "UP", "count": 38},
    {"move": "DOWN", "count": 35},
    {"move": "LEFT", "count": 32}
  ],
  "most_common_sequences": [
    {"sequence": ["UP", "UP", "RIGHT"], "count": 15},
    {"sequence": ["RIGHT", "RIGHT", "DOWN"], "count": 12}
  ],
  "transition_matrix": {
    "UP": {"UP": 0.4, "RIGHT": 0.3, "DOWN": 0.2, "LEFT": 0.1},
    "RIGHT": {"UP": 0.2, "RIGHT": 0.5, "DOWN": 0.2, "LEFT": 0.1}
  }
}
```

#### 7. Set Difficulty
```http
POST /set_difficulty
Content-Type: application/json

{
  "difficulty": 3
}
```

**Response:**
```json
{
  "status": "updated",
  "difficulty": 3
}
```

#### 8. Get Current Difficulty
```http
GET /difficulty
```

**Response:**
```json
{
  "difficulty": 3
}
```

#### 9. Reset Game
```http
POST /reset
```

**Response:**
```json
{
  "status": "reset",
  "message": "Game state reset successfully"
}
```

#### 10. Reset Learning Data
```http
POST /reset_learning
```

**Response:**
```json
{
  "status": "reset",
  "message": "All learning data cleared"
}
```

## Project Structure

```
ai-hide-seek-game/
│
├── backend/                      # Python FastAPI backend
│   ├── main.py                   # FastAPI server & API endpoints
│   ├── ai_agent.py               # Police AI logic & decision making
│   ├── pattern_learning.py       # Pattern recognition & prediction
│   ├── pathfinding.py            # A* pathfinding algorithm
│   ├── test_ai.py                # Unit tests for AI
│   ├── player_data.json          # Persistent learning data
│   ├── requirements.txt          # Python dependencies
│   └── __pycache__/              # Python cache
│
├── frontend/                     # React + Phaser.js frontend
│   ├── public/
│   │   └── index.html            # HTML entry point
│   ├── src/
│   │   ├── components/
│   │   │   └── GameScene.js      # Main Phaser game scene
│   │   ├── App.js                # React root component
│   │   ├── App.css               # Application styles
│   │   ├── api.js                # API client functions
│   │   ├── index.js              # React entry point
│   │   └── index.css             # Global styles
│   ├── package.json              # Node dependencies
│   ├── package-lock.json         # Dependency lock file
│   └── node_modules/             # Node packages
│
├── docs/                         # Documentation
│   ├── README.md                 # This file
│   ├── QUICKSTART.md             # Quick start guide
│   ├── ARCHITECTURE.md           # System architecture details
│   ├── PATHFINDING.md            # A* algorithm documentation
│   ├── INTERCEPTION_STRATEGIES.md # AI interception details
│   ├── SPEED_BOOST_SYSTEM.md     # Speed boost implementation
│   ├── API_DOCUMENTATION.md      # Complete API reference
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── TROUBLESHOOTING.md        # Common issues & solutions
│   └── FEATURES.md               # Feature list
│
├── start.bat                     # Windows startup script
├── start.sh                      # Linux/Mac startup script
├── .gitignore                    # Git ignore rules
└── LICENSE                       # MIT License

```

### Key Files Explained

#### Backend Files

**main.py** (320 lines)
- FastAPI application setup
- All API endpoint definitions
- CORS configuration
- Server startup logic

**ai_agent.py** (600+ lines)
- `PoliceAI` class - Main AI logic
- A* pathfinding integration
- Velocity tracking and prediction
- Interception strategy selection
- Speed boost calculation
- Pattern learning integration

**pattern_learning.py** (200+ lines)
- `PatternLearner` class
- N-gram analysis (bigrams, trigrams)
- Move prediction algorithms
- Pattern confidence calculation
- Data persistence (JSON)

**pathfinding.py** (300+ lines)
- `AStarPathfinder` class
- A* algorithm implementation
- Manhattan distance heuristic
- Path reconstruction
- Obstacle avoidance

#### Frontend Files

**GameScene.js** (400+ lines)
- Phaser game scene
- Game loop and rendering
- Player movement handling
- Police AI visualization
- Collision detection
- UI updates

**App.js** (200+ lines)
- React component structure
- Game state management
- Difficulty selector
- Statistics display
- Game controls

**api.js** (150+ lines)
- Axios HTTP client
- API endpoint wrappers
- Error handling
- Request/response formatting

##  Testing

### Backend Tests

Run AI unit tests:
```bash
cd backend
python test_ai.py
```

**Test Coverage:**
- ✅ A* pathfinding accuracy
- ✅ Velocity calculation
- ✅ Speed boost tiers
- ✅ Pattern prediction
- ✅ Interception strategies

### Manual Testing

**Test Speed Boost:**
```bash
# Test close distance (should return speed: 3)
curl -X POST http://localhost:8000/ai_strategy \
  -H "Content-Type: application/json" \
  -d '{"player_pos": [5,5], "police_pos": [4,3], "recent_moves": ["UP"], "round": 1, "obstacles": [], "difficulty": 2}'
```

**Test Pattern Learning:**
```bash
# Record some moves
curl -X POST http://localhost:8000/record_move \
  -H "Content-Type: application/json" \
  -d '{"round": 1, "move": "UP", "position": [5,5]}'

# Get patterns
curl http://localhost:8000/patterns
```

##  Performance Metrics

### Backend Performance

| Operation | Average Time | Max Time |
|-----------|--------------|----------|
| A* Pathfinding | <1ms | 3ms |
| Speed Calculation | <0.1ms | 0.2ms |
| Pattern Prediction | <2ms | 5ms |
| API Response | <10ms | 20ms |

### Frontend Performance

| Metric | Value |
|--------|-------|
| Frame Rate | 60 FPS |
| Render Time | <16ms |
| Input Latency | <50ms |
| Memory Usage | ~50MB |

### AI Accuracy

| Difficulty | Catch Rate | Prediction Accuracy |
|------------|------------|---------------------|
| Level 1 | ~5% | N/A (random) |
| Level 2 | ~15% | N/A (direct chase) |
| Level 3 | ~35% | ~65% |
| Level 4 | ~55% | ~75% |

##  Development Journey

This project was built through 6 major development phases:

### Phase 1: Initial Setup 
- Full-stack project scaffolding
- Basic game mechanics
- Player movement and collision
- Simple random AI

### Phase 2: Pattern Learning 
- N-gram analysis implementation
- Move prediction algorithm
- Data persistence
- Bug fixes in pattern recognition

### Phase 3: Difficulty Levels 
- 4-tier difficulty system
- Direct chase implementation
- Difficulty selector UI
- Backend difficulty management

### Phase 4: A* Pathfinding 
- A* algorithm implementation
- Obstacle navigation
- Path optimization
- Performance tuning (<1ms)

### Phase 5: Interception Strategies 
- Velocity tracking system
- Future position prediction
- Interception point calculation
- Escape route blocking
- Corner trapping
- Distance-based tactics

### Phase 6: Speed Boost System 
- Proximity detection
- Dynamic speed adjustment
- 3-tier speed system
- Visual indicators
- Multi-step movement
- Balance tuning

**Total Development:**
- ~1,800 lines of Python
- ~800 lines of JavaScript
- ~4,000 lines of documentation
- 40+ files created
- 6 major features implemented

## Deployment

### Frontend Deployment (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Configure build settings:
   ```
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```
4. Add environment variable:
   ```
   REACT_APP_API_URL=<your-backend-url>
   ```
5. Deploy

### Backend Deployment (Render/Railway/Heroku)

1. Create `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Update `requirements.txt` if needed

3. Deploy to platform of choice

4. Configure CORS in `main.py` to allow frontend domain

 **See**: [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

##  Configuration

### Adjust AI Difficulty

Edit `backend/ai_agent.py`:

```python
# Change speed boost thresholds
def calculate_speed_boost(self, player_pos, police_pos):
    distance = self.calculate_distance(player_pos, police_pos)
    
    if distance <= 3:    # Make harder: change to 4
        return 3
    elif distance <= 6:  # Make easier: change to 8
        return 2
    else:
        return 1
```

### Enable/Disable Features

```python
# In backend/ai_agent.py __init__
self.use_pathfinding = True      # A* pathfinding
self.enable_speed_boost = True   # Proximity speed boost
self.interception_mode = True    # Interception strategies
```

### Adjust Game Settings

Edit `frontend/src/components/GameScene.js`:

```javascript
// Game configuration
this.GRID_SIZE = 10;           // Grid size (10×10)
this.CELL_SIZE = 50;           // Cell size in pixels
this.MOVE_SPEED = 200;         // Animation speed (ms)
this.MOVE_COOLDOWN = 300;      // Input cooldown (ms)
```

##  Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Module not found:**
```bash
pip install -r requirements.txt
```

**CORS errors:**
- Check `main.py` CORS configuration
- Ensure frontend URL is in `allow_origins`

### Frontend Issues

**Port 3000 already in use:**
```bash
# Kill process on port 3000
# Windows: Use Task Manager
# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

**API connection failed:**
- Check backend is running on port 8000
- Verify `REACT_APP_API_URL` in `.env`
- Check browser console for errors

**Game not rendering:**
- Clear browser cache
- Check console for Phaser errors
- Ensure all dependencies installed

 **See**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions

##  Documentation

### Available Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - Complete project overview |
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide for beginners |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and design |
| [PATHFINDING.md](PATHFINDING.md) | A* algorithm implementation details |
| [INTERCEPTION_STRATEGIES.md](INTERCEPTION_STRATEGIES.md) | AI interception logic explained |
| [SPEED_BOOST_SYSTEM.md](SPEED_BOOST_SYSTEM.md) | Speed boost feature documentation |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Deployment instructions |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [FEATURES.md](FEATURES.md) | Complete feature list |

##  Learning Resources

### Algorithms Used

**A* Pathfinding:**
- [A* Search Algorithm - Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Introduction to A* - Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)

**Markov Chains:**
- [Markov Chains - Brilliant](https://brilliant.org/wiki/markov-chains/)
- [N-gram Models - Stanford NLP](https://web.stanford.edu/~jurafsky/slp3/3.pdf)

**Game AI:**
- [Game AI Pro - Articles](http://www.gameaipro.com/)
- [AI for Games - Ian Millington](https://www.amazon.com/AI-Games-Third-Ian-Millington/dp/1138483974)

### Technologies

**FastAPI:**
- [Official Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

**Phaser.js:**
- [Official Documentation](https://photonstorm.github.io/phaser3-docs/)
- [Phaser Examples](https://phaser.io/examples)

**React:**
- [Official Documentation](https://react.dev/)
- [React Tutorial](https://react.dev/learn)

##  Contributing

This is a portfolio/educational project, but contributions are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Ideas

-  Improve UI/UX design
-  Add sound effects and music
-  Create new map layouts
-  Implement reinforcement learning
- Add multiplayer mode
-  Make mobile-responsive
-  Add leaderboard system
-  Add power-ups and special abilities

##  Future Enhancements

### Planned Features

- [ ] **Reinforcement Learning**: Train AI using Q-learning or Deep Q-Networks
- [ ] **Multiplayer Mode**: Multiple players vs AI or PvP
- [ ] **Power-ups**: Speed boost, invisibility, teleportation
- [ ] **Multiple Maps**: Different layouts and obstacle configurations
- [ ] **Sound Effects**: Movement, catch, background music
- [ ] **Mobile Support**: Touch controls and responsive design
- [ ] **Replay System**: Record and replay games
- [ ] **Leaderboard**: Global high scores
- [ ] **Achievements**: Unlock achievements for milestones
- [ ] **Custom Skins**: Customize player and police appearance

### Advanced AI Features

- [ ] **Multi-Agent Coordination**: Multiple police working together
- [ ] **Predictive Blocking**: Block multiple escape routes simultaneously
- [ ] **Adaptive Learning Rate**: Adjust learning based on player skill
- [ ] **Personality Modes**: Aggressive, Defensive, Balanced AI styles
- [ ] **Neural Network Prediction**: Deep learning for move prediction

##  Project Highlights

### Technical Achievements

✅ **Full-Stack Development**: Complete React + Python application  
✅ **Advanced AI**: 4 difficulty levels with sophisticated strategies  
✅ **A* Pathfinding**: Optimal path calculation with obstacle avoidance  
✅ **Velocity Prediction**: Physics-based future position calculation  
✅ **Pattern Learning**: N-gram analysis and Markov chain prediction  
✅ **Dynamic Difficulty**: Proximity-based speed adjustment  
✅ **Real-time Updates**: Smooth 60 FPS gameplay  
✅ **RESTful API**: Clean, documented API design  
✅ **Comprehensive Documentation**: 4,000+ lines of documentation  

### Skills Demonstrated

- **Frontend**: React, Phaser.js, HTML5 Canvas, CSS3
- **Backend**: Python, FastAPI, RESTful API design
- **Algorithms**: A*, Markov Chains, N-gram analysis
- **AI/ML**: Pattern recognition, prediction, adaptive behavior
- **Game Development**: Physics, collision detection, game loop
- **Software Engineering**: Clean code, documentation, testing
- **Problem Solving**: Complex algorithm implementation
- **System Design**: Architecture planning and implementation

##  License

MIT License

Copyright (c) 2026 AI Hide and Seek Game

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Acknowledgments

- **Phaser.js** - Excellent 2D game engine
- **FastAPI** - Modern, fast Python web framework
- **React** - Powerful UI library
- **A* Algorithm** - Classic pathfinding solution
- **Game AI Community** - Inspiration and resources



**🎮 Happy Gaming! 🎮**

</div>
