/**
 * Main Phaser Game Scene
 * Handles game rendering, physics, and game loop
 */

import Phaser from 'phaser';
import { recordMove, getAIStrategy, updateGameState } from '../api';

export default class GameScene extends Phaser.Scene {
  constructor() {
    super({ key: 'GameScene' });
    
    // Game configuration
    this.GRID_SIZE = 10;
    this.CELL_SIZE = 50;
    this.MOVE_SPEED = 200;
    
    // Game state
    this.playerScore = 10;
    this.round = 1;
    this.gameOver = false;
    this.recentMoves = [];
    this.aiStrategy = null;
    this.difficulty = 2;  // Default: Direct Chase
    
    // Positions
    this.playerGridPos = { x: 1, y: 1 };
    this.policeGridPos = { x: 8, y: 8 };
    
    // Movement
    this.isMoving = false;
    this.lastMoveTime = 0;
    this.MOVE_COOLDOWN = 300;
    
    // Obstacles
    this.obstacles = [];
  }

  preload() {
    // Create simple colored rectangles for game entities
    this.createPlayerTexture();
    this.createPoliceTexture();
    this.createObstacleTexture();
    this.createGridTexture();
  }

  create() {
    // Create grid background
    this.createGrid();
    
    // Create obstacles
    this.createObstacles();
    
    // Create player
    this.player = this.add.sprite(
      this.gridToPixel(this.playerGridPos.x),
      this.gridToPixel(this.playerGridPos.y),
      'player'
    );
    
    // Create police
    this.police = this.add.sprite(
      this.gridToPixel(this.policeGridPos.x),
      this.gridToPixel(this.policeGridPos.y),
      'police'
    );
    
    // Setup keyboard input
    this.cursors = this.input.keyboard.createCursorKeys();
    
    // Setup AI update timer
    this.time.addEvent({
      delay: 500,
      callback: this.updateAI,
      callbackScope: this,
      loop: true
    });
    
    // Create UI text
    this.createUI();
    
    // Emit initial state
    this.emitGameState();
  }

  update(time) {
    if (this.gameOver || this.isMoving) return;
    
    // Handle player input
    if (time - this.lastMoveTime > this.MOVE_COOLDOWN) {
      let moved = false;
      let direction = null;
      
      if (this.cursors.up.isDown) {
        direction = 'UP';
        moved = this.movePlayer(0, -1);
      } else if (this.cursors.down.isDown) {
        direction = 'DOWN';
        moved = this.movePlayer(0, 1);
      } else if (this.cursors.left.isDown) {
        direction = 'LEFT';
        moved = this.movePlayer(-1, 0);
      } else if (this.cursors.right.isDown) {
        direction = 'RIGHT';
        moved = this.movePlayer(1, 0);
      }
      
      if (moved && direction) {
        this.lastMoveTime = time;
        this.recordPlayerMove(direction);
      }
    }
  }

  createPlayerTexture() {
    const graphics = this.add.graphics();
    graphics.fillStyle(0x4CAF50, 1);
    graphics.fillCircle(20, 20, 18);
    graphics.generateTexture('player', 40, 40);
    graphics.destroy();
  }

  createPoliceTexture() {
    const graphics = this.add.graphics();
    graphics.fillStyle(0xF44336, 1);
    graphics.fillCircle(20, 20, 18);
    graphics.generateTexture('police', 40, 40);
    graphics.destroy();
  }

  createObstacleTexture() {
    const graphics = this.add.graphics();
    graphics.fillStyle(0x424242, 1);
    graphics.fillRect(0, 0, 40, 40);
    graphics.generateTexture('obstacle', 40, 40);
    graphics.destroy();
  }

  createGridTexture() {
    const graphics = this.add.graphics();
    graphics.lineStyle(1, 0xcccccc, 1);
    
    for (let i = 0; i <= this.GRID_SIZE; i++) {
      graphics.moveTo(i * this.CELL_SIZE, 0);
      graphics.lineTo(i * this.CELL_SIZE, this.GRID_SIZE * this.CELL_SIZE);
      graphics.moveTo(0, i * this.CELL_SIZE);
      graphics.lineTo(this.GRID_SIZE * this.CELL_SIZE, i * this.CELL_SIZE);
    }
    
    graphics.strokePath();
  }

  createGrid() {
    const graphics = this.add.graphics();
    graphics.fillStyle(0xf5f5f5, 1);
    graphics.fillRect(0, 0, this.GRID_SIZE * this.CELL_SIZE, this.GRID_SIZE * this.CELL_SIZE);
    
    graphics.lineStyle(2, 0xdddddd, 1);
    for (let i = 0; i <= this.GRID_SIZE; i++) {
      graphics.moveTo(i * this.CELL_SIZE, 0);
      graphics.lineTo(i * this.CELL_SIZE, this.GRID_SIZE * this.CELL_SIZE);
      graphics.moveTo(0, i * this.CELL_SIZE);
      graphics.lineTo(this.GRID_SIZE * this.CELL_SIZE, i * this.CELL_SIZE);
    }
    graphics.strokePath();
  }

  createObstacles() {
    // Create some obstacles on the map
    const obstaclePositions = [
      { x: 3, y: 3 }, { x: 3, y: 4 }, { x: 3, y: 5 },
      { x: 6, y: 2 }, { x: 6, y: 3 },
      { x: 5, y: 7 }, { x: 6, y: 7 }, { x: 7, y: 7 },
      { x: 2, y: 8 }, { x: 8, y: 2 }
    ];
    
    obstaclePositions.forEach(pos => {
      const obstacle = this.add.sprite(
        this.gridToPixel(pos.x),
        this.gridToPixel(pos.y),
        'obstacle'
      );
      this.obstacles.push({ sprite: obstacle, pos });
    });
  }

  createUI() {
    // UI is handled by React, but we can add in-game indicators
    this.strategyText = this.add.text(10, 10, '', {
      fontSize: '14px',
      fill: '#333',
      backgroundColor: '#fff',
      padding: { x: 10, y: 5 }
    });
  }

  gridToPixel(gridCoord) {
    return gridCoord * this.CELL_SIZE + this.CELL_SIZE / 2;
  }

  pixelToGrid(pixelCoord) {
    return Math.floor(pixelCoord / this.CELL_SIZE);
  }

  isValidPosition(x, y) {
    // Check bounds
    if (x < 0 || x >= this.GRID_SIZE || y < 0 || y >= this.GRID_SIZE) {
      return false;
    }
    
    // Check obstacles
    return !this.obstacles.some(obs => obs.pos.x === x && obs.pos.y === y);
  }

  movePlayer(dx, dy) {
    const newX = this.playerGridPos.x + dx;
    const newY = this.playerGridPos.y + dy;
    
    if (!this.isValidPosition(newX, newY)) {
      return false;
    }
    
    this.playerGridPos.x = newX;
    this.playerGridPos.y = newY;
    
    this.isMoving = true;
    
    this.tweens.add({
      targets: this.player,
      x: this.gridToPixel(newX),
      y: this.gridToPixel(newY),
      duration: this.MOVE_SPEED,
      onComplete: () => {
        this.isMoving = false;
        this.checkCollision();
      }
    });
    
    return true;
  }

  movePolice(direction) {
    let dx = 0, dy = 0;
    
    switch (direction) {
      case 'UP': dy = -1; break;
      case 'DOWN': dy = 1; break;
      case 'LEFT': dx = -1; break;
      case 'RIGHT': dx = 1; break;
      default: return;
    }
    
    const newX = this.policeGridPos.x + dx;
    const newY = this.policeGridPos.y + dy;
    
    if (!this.isValidPosition(newX, newY)) {
      return;
    }
    
    this.policeGridPos.x = newX;
    this.policeGridPos.y = newY;
    
    this.tweens.add({
      targets: this.police,
      x: this.gridToPixel(newX),
      y: this.gridToPixel(newY),
      duration: this.MOVE_SPEED,
      onComplete: () => {
        this.checkCollision();
      }
    });
  }

  checkCollision() {
    if (this.playerGridPos.x === this.policeGridPos.x &&
        this.playerGridPos.y === this.policeGridPos.y) {
      this.handleCatch();
    }
  }

  async handleCatch() {
    this.playerScore--;
    
    // Flash effect
    this.cameras.main.flash(200, 255, 0, 0);
    
    // Update backend
    try {
      await updateGameState(this.round, this.playerScore, true);
    } catch (error) {
      console.error('Failed to update game state:', error);
    }
    
    if (this.playerScore <= 0) {
      this.endGame();
    } else {
      this.nextRound();
    }
    
    this.emitGameState();
  }

  nextRound() {
    this.round++;
    
    // Reset positions
    this.playerGridPos = { x: 1, y: 1 };
    this.policeGridPos = { x: 8, y: 8 };
    
    this.player.setPosition(
      this.gridToPixel(this.playerGridPos.x),
      this.gridToPixel(this.playerGridPos.y)
    );
    
    this.police.setPosition(
      this.gridToPixel(this.policeGridPos.x),
      this.gridToPixel(this.policeGridPos.y)
    );
    
    this.emitGameState();
  }

  endGame() {
    this.gameOver = true;
    this.emitGameState();
  }

  async recordPlayerMove(direction) {
    this.recentMoves.push(direction);
    if (this.recentMoves.length > 10) {
      this.recentMoves.shift();
    }
    
    try {
      await recordMove(
        this.round,
        direction,
        [this.playerGridPos.x, this.playerGridPos.y]
      );
    } catch (error) {
      console.error('Failed to record move:', error);
    }
  }

  async updateAI() {
    if (this.gameOver || this.isMoving) return;
    
    try {
      const obstaclePositions = this.obstacles.map(obs => [obs.pos.x, obs.pos.y]);
      
      const strategy = await getAIStrategy(
        [this.playerGridPos.x, this.playerGridPos.y],
        [this.policeGridPos.x, this.policeGridPos.y],
        this.recentMoves,
        this.round,
        obstaclePositions,
        this.difficulty  // Pass difficulty level
      );
      
      this.aiStrategy = strategy;
      
      // Get speed from strategy (1, 2, or 3 steps)
      const speed = strategy.speed || 1;
      const distance = strategy.distance || 10;
      
      // Move police multiple times based on speed
      for (let i = 0; i < speed; i++) {
        // Recalculate direction for each step if needed
        if (i > 0) {
          // For subsequent moves, recalculate strategy
          const newStrategy = await getAIStrategy(
            [this.playerGridPos.x, this.playerGridPos.y],
            [this.policeGridPos.x, this.policeGridPos.y],
            this.recentMoves,
            this.round,
            obstaclePositions,
            this.difficulty
          );
          this.movePolice(newStrategy.direction);
        } else {
          this.movePolice(strategy.direction);
        }
        
        // Small delay between moves for visual effect
        if (i < speed - 1) {
          await new Promise(resolve => setTimeout(resolve, 50));
        }
      }
      
      // Update strategy display with speed indicator
      let speedText = '';
      if (speed === 3) {
        speedText = ' 🔥 CHASE MODE!';
      } else if (speed === 2) {
        speedText = ' ⚡ PURSUIT!';
      }
      
      this.strategyText.setText(
        `AI: ${strategy.strategy} (${Math.round(strategy.confidence * 100)}%)${speedText}\n` +
        `Distance: ${distance.toFixed(1)} | Speed: ${speed}x`
      );
      
      this.emitGameState();
    } catch (error) {
      console.error('Failed to get AI strategy:', error);
    }
  }
  
  setDifficulty(level) {
    this.difficulty = level;
  }

  emitGameState() {
    // Emit game state to React component
    if (this.game.events) {
      this.game.events.emit('gameStateUpdate', {
        playerScore: this.playerScore,
        round: this.round,
        gameOver: this.gameOver,
        aiStrategy: this.aiStrategy,
        recentMoves: this.recentMoves
      });
    }
  }

  resetGame() {
    this.playerScore = 10;
    this.round = 1;
    this.gameOver = false;
    this.recentMoves = [];
    this.aiStrategy = null;
    
    this.playerGridPos = { x: 1, y: 1 };
    this.policeGridPos = { x: 8, y: 8 };
    
    this.player.setPosition(
      this.gridToPixel(this.playerGridPos.x),
      this.gridToPixel(this.playerGridPos.y)
    );
    
    this.police.setPosition(
      this.gridToPixel(this.policeGridPos.x),
      this.gridToPixel(this.policeGridPos.y)
    );
    
    this.emitGameState();
  }
}
