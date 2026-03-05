/**
 * API Service for communicating with backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Record a player move
 */
export const recordMove = async (round, move, position) => {
  try {
    const response = await api.post('/record_move', {
      round,
      move,
      position,
    });
    return response.data;
  } catch (error) {
    console.error('Error recording move:', error);
    throw error;
  }
};

/**
 * Get AI strategy decision
 */
export const getAIStrategy = async (playerPos, policePos, recentMoves, round, obstacles = [], difficulty = null) => {
  try {
    const response = await api.post('/ai_strategy', {
      player_pos: playerPos,
      police_pos: policePos,
      recent_moves: recentMoves,
      round,
      obstacles,
      difficulty,
    });
    return response.data;
  } catch (error) {
    console.error('Error getting AI strategy:', error);
    throw error;
  }
};

/**
 * Predict next player move
 */
export const predictMove = async (history) => {
  try {
    const response = await api.post('/predict_move', {
      history,
    });
    return response.data;
  } catch (error) {
    console.error('Error predicting move:', error);
    throw error;
  }
};

/**
 * Update game state
 */
export const updateGameState = async (round, playerScore, caught) => {
  try {
    const response = await api.post('/game_state', {
      round,
      player_score: playerScore,
      caught,
    });
    return response.data;
  } catch (error) {
    console.error('Error updating game state:', error);
    throw error;
  }
};

/**
 * Get AI statistics
 */
export const getStatistics = async () => {
  try {
    const response = await api.get('/statistics');
    return response.data;
  } catch (error) {
    console.error('Error getting statistics:', error);
    throw error;
  }
};

/**
 * Get pattern analysis
 */
export const getPatterns = async () => {
  try {
    const response = await api.get('/patterns');
    return response.data;
  } catch (error) {
    console.error('Error getting patterns:', error);
    throw error;
  }
};

/**
 * Reset game
 */
export const resetGame = async () => {
  try {
    const response = await api.post('/reset');
    return response.data;
  } catch (error) {
    console.error('Error resetting game:', error);
    throw error;
  }
};

/**
 * Reset all learning data
 */
export const resetLearning = async () => {
  try {
    const response = await api.post('/reset_learning');
    return response.data;
  } catch (error) {
    console.error('Error resetting learning:', error);
    throw error;
  }
};

/**
 * Set AI difficulty level
 */
export const setDifficulty = async (difficulty) => {
  try {
    const response = await api.post('/set_difficulty', {
      difficulty,
    });
    return response.data;
  } catch (error) {
    console.error('Error setting difficulty:', error);
    throw error;
  }
};

/**
 * Get current AI difficulty
 */
export const getDifficulty = async () => {
  try {
    const response = await api.get('/difficulty');
    return response.data;
  } catch (error) {
    console.error('Error getting difficulty:', error);
    throw error;
  }
};

export default api;
