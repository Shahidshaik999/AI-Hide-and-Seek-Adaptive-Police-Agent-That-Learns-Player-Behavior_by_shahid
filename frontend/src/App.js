import React, { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import './App.css';
import GameScene from './components/GameScene';
import { getStatistics, getPatterns, resetGame, resetLearning, setDifficulty, getDifficulty } from './api';

function App() {
  const gameRef = useRef(null);
  const phaserGameRef = useRef(null);
  
  const [gameState, setGameState] = useState({
    playerScore: 10,
    round: 1,
    gameOver: false,
    aiStrategy: null,
    recentMoves: []
  });
  
  const [statistics, setStatistics] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [currentDifficulty, setCurrentDifficulty] = useState(2);

  useEffect(() => {
    // Initialize Phaser game
    const config = {
      type: Phaser.AUTO,
      width: 500,
      height: 500,
      parent: gameRef.current,
      backgroundColor: '#f5f5f5',
      scene: GameScene,
      physics: {
        default: 'arcade',
        arcade: {
          debug: false
        }
      }
    };

    phaserGameRef.current = new Phaser.Game(config);

    // Listen for game state updates
    phaserGameRef.current.events.on('gameStateUpdate', (state) => {
      setGameState(state);
    });

    // Check backend connection
    checkBackendConnection();

    // Fetch statistics periodically
    const statsInterval = setInterval(() => {
      fetchStatistics();
      fetchPatterns();
    }, 3000);

    return () => {
      clearInterval(statsInterval);
      if (phaserGameRef.current) {
        phaserGameRef.current.destroy(true);
      }
    };
  }, []);

  const checkBackendConnection = async () => {
    try {
      await getStatistics();
      setBackendConnected(true);
      
      // Get current difficulty
      const diffData = await getDifficulty();
      setCurrentDifficulty(diffData.difficulty);
    } catch (error) {
      setBackendConnected(false);
      console.error('Backend not connected:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const stats = await getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const fetchPatterns = async () => {
    try {
      const patternsData = await getPatterns();
      setPatterns(patternsData);
    } catch (error) {
      console.error('Failed to fetch patterns:', error);
    }
  };

  const handleResetGame = async () => {
    try {
      await resetGame();
      const scene = phaserGameRef.current.scene.getScene('GameScene');
      if (scene) {
        scene.resetGame();
      }
      fetchStatistics();
    } catch (error) {
      console.error('Failed to reset game:', error);
    }
  };

  const handleResetLearning = async () => {
    if (window.confirm('This will erase all learned patterns. Are you sure?')) {
      try {
        await resetLearning();
        setStatistics(null);
        setPatterns(null);
        handleResetGame();
      } catch (error) {
        console.error('Failed to reset learning:', error);
      }
    }
  };

  const handleDifficultyChange = async (level) => {
    try {
      await setDifficulty(level);
      setCurrentDifficulty(level);
      
      // Update game scene difficulty
      const scene = phaserGameRef.current.scene.getScene('GameScene');
      if (scene) {
        scene.setDifficulty(level);
      }
    } catch (error) {
      console.error('Failed to set difficulty:', error);
    }
  };

  return (
    <div className="App">
      <div className="game-container">
        <div className="game-header">
          <h1>🎮 AI Hide and Seek</h1>
          <p>Escape from the learning police agent!</p>
          {!backendConnected && (
            <div className="error">
              ⚠️ Backend not connected. Make sure the API is running on http://localhost:8000
            </div>
          )}
        </div>

        <div className="difficulty-selector">
          <h3>🎯 AI Difficulty</h3>
          <div className="difficulty-buttons">
            <button 
              className={currentDifficulty === 1 ? 'active' : ''}
              onClick={() => handleDifficultyChange(1)}
            >
              Easy (Random)
            </button>
            <button 
              className={currentDifficulty === 2 ? 'active' : ''}
              onClick={() => handleDifficultyChange(2)}
            >
              Medium (Chase)
            </button>
            <button 
              className={currentDifficulty === 3 ? 'active' : ''}
              onClick={() => handleDifficultyChange(3)}
            >
              Hard (Predictive)
            </button>
            <button 
              className={currentDifficulty === 4 ? 'active' : ''}
              onClick={() => handleDifficultyChange(4)}
            >
              Very Hard (Advanced)
            </button>
          </div>
        </div>

        <div className="game-stats">
          <div className="stat-card">
            <h3>Lives</h3>
            <p>{gameState.playerScore}</p>
          </div>
          <div className="stat-card">
            <h3>Round</h3>
            <p>{gameState.round}</p>
          </div>
          {statistics && (
            <>
              <div className="stat-card">
                <h3>AI Catches</h3>
                <p>{statistics.catches}</p>
              </div>
              <div className="stat-card">
                <h3>Pattern Confidence</h3>
                <p>{Math.round((statistics.learning_stats?.pattern_confidence || 0) * 100)}%</p>
              </div>
            </>
          )}
        </div>

        {gameState.gameOver && (
          <div className="game-over">
            <h2>Game Over!</h2>
            <p>The AI caught you {statistics?.catches || 0} times</p>
            <p>You survived {gameState.round} rounds</p>
            <button onClick={handleResetGame}>Play Again</button>
          </div>
        )}

        <div className="game-canvas-wrapper">
          <div ref={gameRef}></div>
        </div>

        <div className="controls">
          <h3>Controls</h3>
          <p>⬆️ ⬇️ ⬅️ ➡️ Arrow Keys - Move your character (Green)</p>
          <p>🎯 Objective: Avoid the red police agent</p>
          <p>⚠️ Gray blocks are obstacles</p>
        </div>

        {gameState.aiStrategy && (
          <div className="ai-info">
            <h3>🤖 AI Intelligence</h3>
            <div className="ai-strategy">
              <div className="strategy-item">
                <strong>Strategy</strong>
                {gameState.aiStrategy.strategy.replace(/_/g, ' ').toUpperCase()}
              </div>
              <div className="strategy-item">
                <strong>Confidence</strong>
                {Math.round(gameState.aiStrategy.confidence * 100)}%
              </div>
              {gameState.aiStrategy.prediction && (
                <div className="strategy-item">
                  <strong>Predicted Move</strong>
                  {gameState.aiStrategy.prediction.move_probabilities && 
                    Object.entries(gameState.aiStrategy.prediction.move_probabilities)
                      .sort((a, b) => b[1] - a[1])[0][0]
                  }
                </div>
              )}
            </div>
          </div>
        )}

        {patterns && patterns.total_moves > 10 && (
          <div className="pattern-analysis">
            <h4>📊 Pattern Analysis</h4>
            <p><strong>Playstyle:</strong> {patterns.playstyle?.toUpperCase()}</p>
            <p><strong>Total Moves Learned:</strong> {patterns.total_moves}</p>
            {patterns.most_common_moves && (
              <div>
                <p><strong>Most Common Moves:</strong></p>
                <div className="pattern-list">
                  {Object.entries(patterns.most_common_moves).map(([move, count]) => (
                    <span key={move} className="pattern-badge">
                      {move}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {patterns.most_common_sequences && patterns.most_common_sequences.length > 0 && (
              <div>
                <p><strong>Common Sequences:</strong></p>
                <div className="pattern-list">
                  {patterns.most_common_sequences.slice(0, 3).map((seq, idx) => (
                    <span key={idx} className="pattern-badge">
                      {seq.sequence.join(' → ')} ({seq.count}x)
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="button-group">
          <button onClick={handleResetGame}>
            🔄 New Game
          </button>
          <button onClick={handleResetLearning}>
            🧹 Reset AI Learning
          </button>
          <button onClick={fetchStatistics}>
            📊 Refresh Stats
          </button>
        </div>

        {statistics && (
          <div className="ai-info">
            <h3>📈 AI Learning Progress</h3>
            <div className="ai-strategy">
              <div className="strategy-item">
                <strong>Total Moves Analyzed</strong>
                {statistics.learning_stats?.total_moves || 0}
              </div>
              <div className="strategy-item">
                <strong>Unique Patterns</strong>
                {statistics.learning_stats?.unique_bigrams || 0}
              </div>
              <div className="strategy-item">
                <strong>Catch Rate</strong>
                {Math.round((statistics.catch_rate || 0) * 100)}%
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="game-container" style={{ marginTop: '20px', padding: '20px' }}>
        <h3>🎯 How It Works</h3>
        <p style={{ textAlign: 'left', color: '#666', lineHeight: '1.6' }}>
          This game demonstrates machine learning in action. The police AI starts with simple random movement,
          but as you play, it learns your movement patterns. It analyzes sequences like "UP → UP → RIGHT"
          and calculates probabilities for your next move. By round 5+, the AI uses predictive algorithms
          to intercept you before you even get there. The more you play, the smarter it becomes!
        </p>
      </div>
    </div>
  );
}

export default App;
