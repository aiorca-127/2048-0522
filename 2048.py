import streamlit as st
import streamlit.components.v1 as components

# Set up the Streamlit page
st.set_page_config(page_title="Streamlit 2048 Pro", layout="centered")
st.title("📱 Streamlit 2048: Pro Edition")
st.write("Play with **Arrow Keys** on desktop, or **Swipe** on your phone! Use your special abilities below.")

# The HTML, CSS, and JavaScript for the upgraded 2048 game
game_html = """
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <style>
    body {
      background-color: #0E1117;
      color: #FAFAFA;
      font-family: 'Clear Sans', 'Helvetica Neue', Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin: 0;
      padding: 10px;
      /* Prevent pull-to-refresh on mobile */
      overscroll-behavior-y: contain; 
    }
    
    .header {
      display: flex;
      justify-content: space-between;
      width: 100%;
      max-width: 400px;
      margin-bottom: 15px;
      align-items: center;
    }
    
    .score-container {
      background: #bbada0;
      padding: 5px 15px;
      border-radius: 6px;
      font-size: 16px;
      font-weight: bold;
      text-align: center;
      color: white;
    }
    #score { font-size: 24px; }
    
    .controls {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: center;
      width: 100%;
      max-width: 400px;
      margin-bottom: 15px;
    }
    
    button {
      padding: 10px 15px;
      font-size: 16px;
      font-weight: bold;
      background-color: #8f7a66;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      flex: 1;
      white-space: nowrap;
    }
    button:hover { background-color: #9f8b77; }
    button:disabled { background-color: #55483c; color: #888; cursor: not-allowed; }
    
    #magic-btn { background-color: #8b5a96; }
    #magic-btn:hover:not(:disabled) { background-color: #a06ab0; }
    
    .grid-container {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      background-color: #bbada0;
      padding: 10px;
      border-radius: 8px;
      position: relative;
      
      /* Essential for mobile swipe! Prevents the browser from scrolling */
      touch-action: none; 
      
      width: 90vw;
      max-width: 400px;
      height: 90vw;
      max-height: 400px;
      box-sizing: border-box;
    }
    
    .grid-cell {
      background-color: #cdc1b4;
      border-radius: 4px;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: clamp(24px, 6vw, 36px); /* Auto-scales font for mobile */
      font-weight: bold;
      color: #776e65;
      transition: all 0.1s ease-in-out;
    }
    
    /* Tile Colors */
    .val-0 { color: transparent; background-color: #cdc1b4; }
    .val-2 { background-color: #eee4da; }
    .val-4 { background-color: #ede0c8; }
    .val-8 { background-color: #f2b179; color: #f9f6f2; }
    .val-16 { background-color: #f59563; color: #f9f6f2; }
    .val-32 { background-color: #f67c5f; color: #f9f6f2; }
    .val-64 { background-color: #f65e3b; color: #f9f6f2; }
    .val-128 { background-color: #edcf72; color: #f9f6f2; font-size: clamp(20px, 5vw, 30px); }
    .val-256 { background-color: #edcc61; color: #f9f6f2; font-size: clamp(20px, 5vw, 30px); }
    .val-512 { background-color: #edc850; color: #f9f6f2; font-size: clamp(20px, 5vw, 30px); }
    .val-1024 { background-color: #edc53f; color: #f9f6f2; font-size: clamp(16px, 4vw, 24px); }
    .val-2048 { background-color: #edc22e; color: #f9f6f2; font-size: clamp(16px, 4vw, 24px); box-shadow: 0 0 30px 10px rgba(243, 215, 116, 0.55), inset 0 0 0 1px rgba(255, 255, 255, 0.33); }

    #game-over {
      display: none;
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(238, 228, 218, 0.85);
      border-radius: 8px;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #776e65;
      font-size: 36px;
      font-weight: bold;
      z-index: 10;
    }
  </style>
</head>
<body>

  <div class="header">
    <div class="score-container">SCORE<br><span id="score">0</span></div>
    <div class="score-container">BEST<br><span id="best-score">0</span></div>
  </div>

  <div class="controls">
    <button onclick="undoMove()" id="undo-btn">↩️ Undo</button>
    <button onclick="useMagic()" id="magic-btn">✨ Magic (1)</button>
    <button onclick="resetGame()">🔄 Restart</button>
  </div>

  <div class="grid-container" id="grid">
    <div id="game-over">
      Game Over!
      <button onclick="resetGame()" style="margin-top: 20px;">Try Again</button>
    </div>
  </div>

  <script>
    const gridElement = document.getElementById("grid");
    const scoreElement = document.getElementById("score");
    const bestScoreElement = document.getElementById("best-score");
    const gameOverScreen = document.getElementById("game-over");
    const magicBtn = document.getElementById("magic-btn");
    
    let board = [];
    let score = 0;
    let bestScore = localStorage.getItem("2048-best") || 0;
    
    // Feature: Undo Variables
    let historyBoard = null;
    let historyScore = 0;
    let magicUsed = false;
    
    // Initialize the UI
    function initUI() {
      document.querySelectorAll('.grid-cell').forEach(e => e.remove());
      bestScoreElement.innerHTML = bestScore;
      
      for (let i = 0; i < 16; i++) {
        let cell = document.createElement("div");
        cell.id = "cell-" + i;
        cell.className = "grid-cell val-0";
        gridElement.appendChild(cell);
      }
      gridElement.appendChild(gameOverScreen); 
    }

    function resetGame() {
      board = [
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0]
      ];
      score = 0;
      historyBoard = null;
      magicUsed = false;
      magicBtn.disabled = false;
      magicBtn.innerHTML = "✨ Magic (1)";
      gameOverScreen.style.display = "none";
      
      addRandomTile();
      addRandomTile();
      updateUI();
    }

    // --- NEW FEATURE: Undo Move ---
    function saveState() {
      historyBoard = board.map(row => [...row]);
      historyScore = score;
    }

    function undoMove() {
      if (historyBoard) {
        board = historyBoard.map(row => [...row]);
        score = historyScore;
        historyBoard = null; // Can only undo once per turn
        gameOverScreen.style.display = "none";
        updateUI();
      }
    }

    // --- NEW FEATURE: Magic Wand (Destroy lowest tile) ---
    function useMagic() {
      if (magicUsed) return;
      
      let minVal = Infinity;
      let targetR = -1; let targetC = -1;
      
      // Find the lowest non-zero tile
      for (let r=0; r<4; r++) {
         for (let c=0; c<4; c++) {
             if (board[r][c] > 0 && board[r][c] < minVal) {
                 minVal = board[r][c]; 
                 targetR = r; targetC = c;
             }
         }
      }
      
      // Destroy it!
      if (targetR !== -1) {
          saveState(); // You can undo magic!
          board[targetR][targetC] = 0;
          magicUsed = true;
          magicBtn.disabled = true;
          magicBtn.innerHTML = "✨ Used";
          updateUI();
      }
    }

    function addRandomTile() {
      let emptyCells = [];
      for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
          if (board[r][c] === 0) emptyCells.push({r, c});
        }
      }
      if (emptyCells.length > 0) {
        let randomCell = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        board[randomCell.r][randomCell.c] = Math.random() < 0.9 ? 2 : 4;
      }
    }

    function updateUI() {
      for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
          let cell = document.getElementById("cell-" + (r * 4 + c));
          let val = board[r][c];
          cell.className = "grid-cell val-" + (val > 2048 ? 2048 : val);
          cell.innerHTML = val === 0 ? "" : val;
        }
      }
      scoreElement.innerHTML = score;
      
      if (score > bestScore) {
        bestScore = score;
        bestScoreElement.innerHTML = bestScore;
        localStorage.setItem("2048-best", bestScore);
      }
    }

    // Core movement logic (with previous bug fix applied)
    function slideAndMerge(row) {
      let filtered = row.filter(val => val !== 0);
      for (let i = 0; i < filtered.length - 1; i++) {
        if (filtered[i] !== 0 && filtered[i] === filtered[i+1]) {
          filtered[i] *= 2;
          score += filtered[i];
          filtered[i+1] = 0;
        }
      }
      filtered = filtered.filter(val => val !== 0);
      while (filtered.length < 4) { filtered.push(0); }
      return filtered;
    }

    function moveLeft() {
      let moved = false;
      for (let r = 0; r < 4; r++) {
        let oldRow = [...board[r]];
        board[r] = slideAndMerge([...board[r]]);
        if (oldRow.join(',') !== board[r].join(',')) moved = true;
      }
      return moved;
    }

    function moveRight() {
      let moved = false;
      for (let r = 0; r < 4; r++) {
        let oldRow = [...board[r]];
        board[r] = slideAndMerge([...board[r]].reverse()).reverse();
        if (oldRow.join(',') !== board[r].join(',')) moved = true;
      }
      return moved;
    }

    function moveUp() {
      let moved = false;
      for (let c = 0; c < 4; c++) {
        let oldCol = [board[0][c], board[1][c], board[2][c], board[3][c]];
        let newCol = slideAndMerge([...oldCol]);
        if (oldCol.join(',') !== newCol.join(',')) moved = true;
        for (let r = 0; r < 4; r++) board[r][c] = newCol[r];
      }
      return moved;
    }

    function moveDown() {
      let moved = false;
      for (let c = 0; c < 4; c++) {
        let oldCol = [board[0][c], board[1][c], board[2][c], board[3][c]];
        let newCol = slideAndMerge([...oldCol].reverse()).reverse();
        if (oldCol.join(',') !== newCol.join(',')) moved = true;
        for (let r = 0; r < 4; r++) board[r][c] = newCol[r];
      }
      return moved;
    }

    function checkGameOver() {
      for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
          if (board[r][c] === 0) return false;
          if (r !== 3 && board[r][c] === board[r+1][c]) return false;
          if (c !== 3 && board[r][c] === board[r][c+1]) return false;
        }
      }
      return true;
    }

    function handleInput(direction) {
      saveState(); // Save state for Undo BEFORE moving
      
      let moved = false;
      if (direction === "Left") moved = moveLeft();
      else if (direction === "Right") moved = moveRight();
      else if (direction === "Up") moved = moveUp();
      else if (direction === "Down") moved = moveDown();

      if (moved) {
        addRandomTile();
        updateUI();
        if (checkGameOver()) {
          gameOverScreen.style.display = "flex";
        }
      } else {
        // If the move didn't do anything, revoke the save state so we don't waste the Undo
        historyBoard = null; 
      }
    }

    // --- KEYBOARD LISTENER ---
    document.addEventListener("keydown", (e) => {
      if(["ArrowLeft", "ArrowUp", "ArrowRight", "ArrowDown"].includes(e.key)) {
          e.preventDefault(); 
          handleInput(e.key.replace("Arrow", ""));
      }
    });

    // --- NEW FEATURE: MOBILE SWIPE LISTENER ---
    let touchStartX = 0;
    let touchStartY = 0;

    gridElement.addEventListener('touchstart', function(e) {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, false);

    gridElement.addEventListener('touchend', function(e) {
      let touchEndX = e.changedTouches[0].screenX;
      let touchEndY = e.changedTouches[0].screenY;
      
      let dx = touchEndX - touchStartX;
      let dy = touchEndY - touchStartY;
      
      // Require a minimum swipe distance to avoid accidental taps
      if (Math.abs(dx) > 30 || Math.abs(dy) > 30) {
        if (Math.abs(dx) > Math.abs(dy)) {
          // Horizontal swipe
          if (dx > 0) handleInput("Right");
          else handleInput("Left");
        } else {
          // Vertical swipe
          if (dy > 0) handleInput("Down");
          else handleInput("Up");
        }
      }
    }, false);

    // Boot up the game
    initUI();
    resetGame();
  </script>
</body>
</html>
"""

# We increased the height slightly to 750 to accommodate the new power-up buttons
components.html(game_html, height=750)
