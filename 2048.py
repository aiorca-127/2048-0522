import streamlit as st
import streamlit.components.v1 as components

# Set up the Streamlit page
st.set_page_config(page_title="Streamlit 2048", layout="centered")
st.title("🧩 Streamlit 2048")
st.write("Use your **Arrow Keys** to slide the tiles. Merge matching numbers to reach **2048**!")

# The HTML, CSS, and JavaScript for the 2048 game
game_html = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      background-color: #0E1117;
      color: #FAFAFA;
      font-family: 'Clear Sans', 'Helvetica Neue', Arial, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      margin: 0;
      padding: 20px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      width: 400px;
      margin-bottom: 20px;
      align-items: center;
    }
    .score-container {
      background: #bbada0;
      padding: 10px 25px;
      border-radius: 6px;
      font-size: 20px;
      font-weight: bold;
      text-align: center;
      color: white;
    }
    #score { font-size: 28px; }
    
    .grid-container {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      background-color: #bbada0;
      padding: 12px;
      border-radius: 8px;
      position: relative;
    }
    .grid-cell {
      width: 80px;
      height: 80px;
      background-color: #cdc1b4;
      border-radius: 4px;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 36px;
      font-weight: bold;
      color: #776e65;
      transition: all 0.15s ease-in-out;
    }
    
    /* Tile Colors */
    .val-0 { color: transparent; background-color: #cdc1b4; }
    .val-2 { background-color: #eee4da; }
    .val-4 { background-color: #ede0c8; }
    .val-8 { background-color: #f2b179; color: #f9f6f2; }
    .val-16 { background-color: #f59563; color: #f9f6f2; }
    .val-32 { background-color: #f67c5f; color: #f9f6f2; }
    .val-64 { background-color: #f65e3b; color: #f9f6f2; }
    .val-128 { background-color: #edcf72; color: #f9f6f2; font-size: 30px; }
    .val-256 { background-color: #edcc61; color: #f9f6f2; font-size: 30px; }
    .val-512 { background-color: #edc850; color: #f9f6f2; font-size: 30px; }
    .val-1024 { background-color: #edc53f; color: #f9f6f2; font-size: 24px; }
    .val-2048 { background-color: #edc22e; color: #f9f6f2; font-size: 24px; box-shadow: 0 0 30px 10px rgba(243, 215, 116, 0.55), inset 0 0 0 1px rgba(255, 255, 255, 0.33); }

    #game-over {
      display: none;
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(238, 228, 218, 0.73);
      border-radius: 8px;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #776e65;
      font-size: 40px;
      font-weight: bold;
    }
    button {
      margin-top: 20px;
      padding: 10px 20px;
      font-size: 18px;
      font-weight: bold;
      background-color: #8f7a66;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover { background-color: #9f8b77; }
  </style>
</head>
<body>

  <div class="header">
    <div class="score-container">SCORE<br><span id="score">0</span></div>
    <button onclick="resetGame()">Restart</button>
  </div>

  <div class="grid-container" id="grid">
    <div id="game-over">
      Game Over!
      <button onclick="resetGame()">Try Again</button>
    </div>
  </div>

  <script>
    const gridElement = document.getElementById("grid");
    const scoreElement = document.getElementById("score");
    const gameOverScreen = document.getElementById("game-over");
    
    let board = [];
    let score = 0;
    
    // Initialize the grid UI
    function initUI() {
      // Clear existing cells
      document.querySelectorAll('.grid-cell').forEach(e => e.remove());
      
      for (let i = 0; i < 16; i++) {
        let cell = document.createElement("div");
        cell.id = "cell-" + i;
        cell.className = "grid-cell val-0";
        gridElement.appendChild(cell);
      }
      gridElement.appendChild(gameOverScreen); 
    }

    // Start a new game
    function resetGame() {
      board = [
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0],
        [0,0,0,0]
      ];
      score = 0;
      gameOverScreen.style.display = "none";
      addRandomTile();
      addRandomTile();
      updateUI();
    }

    // Add a 2 or 4 to a random empty spot
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

    // Update the HTML to match the board array
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
    }

    // Core logic for sliding an array and merging duplicates
    function slideAndMerge(row) {
      // 1. Remove zeros
      let filtered = row.filter(val => val !== 0);
      
      // 2. Merge adjacent equals
      for (let i = 0; i < filtered.length - 1; i++) {
        if (filtered[i] !== 0 && filtered[i] === filtered[i+1]) {
          filtered[i] *= 2;
          score += filtered[i];
          filtered[i+1] = 0;
        }
      }
      
      // 3. Remove zeros again (BUG FIXED HERE: It now filters the merged array!)
      filtered = filtered.filter(val => val !== 0);
      
      // 4. Pad with zeros to keep length 4
      while (filtered.length < 4) {
        filtered.push(0);
      }
      return filtered;
    }

    // Handle board rotations
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

    // Check if any moves are possible
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

    // Keyboard listener
    document.addEventListener("keydown", (e) => {
      if([37, 38, 39, 40].indexOf(e.keyCode) > -1) {
          e.preventDefault(); // Prevent page scrolling
      }
      
      let moved = false;
      if (e.key === "ArrowLeft") moved = moveLeft();
      else if (e.key === "ArrowRight") moved = moveRight();
      else if (e.key === "ArrowUp") moved = moveUp();
      else if (e.key === "ArrowDown") moved = moveDown();

      if (moved) {
        addRandomTile();
        updateUI();
        if (checkGameOver()) {
          gameOverScreen.style.display = "flex";
        }
      }
    });

    // Boot up the game
    initUI();
    resetGame();
  </script>
</body>
</html>
"""

# Render the game. Height 650 is perfect for the board + score header
components.html(game_html, height=650)
