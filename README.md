# Pygame Chess

A chess game built with Pygame, featuring:

- Local play: Player vs Player on the same machine.
- AI mode: Player vs Computer using the Stockfish engine.
- Online mode: simple peer‑to‑peer matchmaking via WebSockets.

The project is organized around a small state machine (`Home`, `Select AI color`, `Game`, `Waiting for opponent`), a reusable chess rules engine, and separate UI renderers for board, pieces, buttons, and modals.

---

## Features

- **Full chess rules**
  - Legal move generation, check, checkmate, stalemate.
  - Castling, en passant, pawn promotion.
  - Basic draw rules (fifty‑move, insufficient material, threefold repetition).

- **Game modes**
  - **Player vs Computer**  
    Uses the Stockfish engine for AI moves (configurable Elo).
  - **Player vs Player (local)**  
    Two players sharing the same screen and mouse.
  - **Play Online**  
    Simple matchmaking server: first player waits, second player connects and the game starts.
    - Random color assignment per game.
    - Moves and promotions are synchronized over WebSocket.

- **UI / UX**
  - Scaled board and sidebar based on your screen resolution.
  - Drag‑and‑drop piece movement.
  - Promotion modal to choose the new piece.
  - Game‑over overlay with winner information.
  - Sound effects for:
    - Entry into game
    - Move, capture, castling
    - Check and checkmate

---

## Requirements

- Python 3.11+ (recommended)
- **Optional but recommended**: `pipenv` for environment management
- **Required for AI mode**: Stockfish engine binary

All Python dependencies are declared in `Pipfile`.

---

## Installing dependencies

### Option 1: Using Pipenv (recommended)

From the project root:

```bash
pipenv install
```

To run commands inside the virtual environment:

```bash
pipenv shell
```

### Option 2: Using pip directly

If you prefer not to use Pipenv:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# (Linux/macOS would be: source .venv/bin/activate)

pip install -r requirements.txt
```

## Setting up Stockfish (Player vs AI mode)

To use the **Player vs Computer** mode, you need a Stockfish binary installed and referenced correctly:

1. **Download Stockfish**
   - Go to:  
     https://stockfishchess.org/
   - Download the engine appropriate for your OS (for example, the Windows binary).

2. **Place the binary in the project**
   - Extract the download and copy the Stockfish executable into:

     ```
     assets/engines/stockfish/
     ```

   - For example on Windows you might end up with:

     ```
     assets/engines/stockfish/stockfish-windows-x86-64.exe
     ```

3. **Configure the path in settings**
   - Open:  
     `src/utils/settings.py`

   - These constants control the engine path:

     ```python
     STOCKFISH_EXECUTOR = "stockfish-windows-x86-64.exe"
     STOCKFISH_PATH = ASSETS_PATH / "engines" / "stockfish" / STOCKFISH_EXECUTOR
     ```

   - If your executable has a different name or folder structure, adjust `STOCKFISH_EXECUTOR` (or `STOCKFISH_PATH`) accordingly so it points to the real binary.

4. **Run the game and choose “Player vs Computer”**
   - When the AI mode is selected, the game creates an `AiChessSession` which will call out to Stockfish through that configured path.

If the path is incorrect or the binary file is missing, the AI ​​mode will display an error when attempting to move.

---

## Running the game

### 1. Start the online server (for “Play Online”)

In one terminal, from the project root:

- With Pipenv:

  ```bash
  pipenv run server
  ```

- Without Pipenv (in your venv):

  ```bash
  uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
  ```

This starts a FastAPI WebSocket server on:

- `ws://localhost:8000/ws`

The client uses this URL via `URI_SERVER_ONLINE_GAME` in `src/utils/settings.py`.  
If you want to run the server elsewhere (different host/port), change that constant accordingly.

### 2. Start the Pygame client

In another terminal:

- With Pipenv:

  ```bash
  pipenv run start
  ```

- Without Pipenv:

  ```bash
  python -m src.main
  ```

This opens the main menu with:

- **Player vs Computer** – requires Stockfish properly configured.
- **Player vs Player** – local game on a single machine.
- **Play Online** – connects to the WebSocket server and waits for an opponent.
- **Exit** – closes the game.

---

## Online mode details

- Make sure the server (`src/server/main.py`) is running.
- On **Machine A**:
  - Start the client (`src/main.py`) and choose **Play Online**.
  - The game enters “Waiting for opponent…”.
- On **Machine B** (or another client instance):
  - Start the client and also choose **Play Online**.
  - The server pairs the two clients, assigns colors randomly, and sends a `match_found` message.
  - Each client then starts a `GameState` with an `OnlineChessSession`.

During online play:

- Each local move is applied via `GameLogic` and sent to the server.
- The server forwards the move to the opponent.
- Promotions are chosen only by the player who promotes; the result is synced to the opponent.
- If one player quits (Exit), the server notifies the opponent, and the client returns to the home screen.

---

## Project structure (high level)

- `src/main.py` – entry point for the Pygame client.
- `src/server/main.py` – FastAPI WebSocket matchmaking server.
- `src/core/`
  - `game.py` – main loop (`GameApp`), manages Pygame and state manager.
  - `chess_session.py` – abstract session and implementations:
    - `LocalChessSession`
    - `AiChessSession`
    - `OnlineChessSession`
- `src/states/` – application states:
  - `home_state.py` – main menu.
  - `select_color_vs_ai_state.py` – choose side vs AI and Elo.
  - `waiting_for_opponent_state.py` – online waiting room.
  - `game_state.py` – actual chess game UI/logic wiring.
- `src/chess/` – rules engine:
  - `game_logic.py`, `board.py`, and piece classes.
- `src/ui/` – renderers for board, pieces, buttons, modals, overlays.
- `assets/`
  - `images/pieces/` – piece sprites.
  - `sounds/` – sound effects.
  - `engines/stockfish/` – Stockfish engine binary (user-supplied).

---

## License

This project is for personal/educational use. Add your preferred license here if you plan to distribute it.
