"""
Advanced Tic‑Tac‑Toe with Minimax AI and alpha‑beta pruning
===================================================

Features
--------
* **Play modes**
  1. Human vs AI (play as **X**)  
  2. Human vs AI (play as **O**)  
  3. **AI vs AI** – completely hands‑off; watch two AIs battle it out.
* **AI difficulty**: easy (random), medium (depth‑2 search), hard (perfect play).
* **Scoreboard** for the human player (suppressed in AI‑vs‑AI mode).
* **Fixed‑width board printer** – columns never drift, even with colour codes.
* Optional **colour output** via `colorama`.
"""

from __future__ import annotations
import random, sys
from typing import List, Optional, Tuple, Dict

# ---------------------------------------------------------------------------
# Optional colour support
# ---------------------------------------------------------------------------
try:
    from colorama import Fore, Style, init as colorama_init  # type: ignore
    colorama_init()
    USE_COLOR = True
except ImportError:  # run fine without colourama
    USE_COLOR = False

# ---------------------------------------------------------------------------
# Board helpers
# ---------------------------------------------------------------------------
Board = List[str]  # flat list of nine "X", "O", or " "
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
]

def make_empty_board() -> Board:
    return [" "] * 9

def winner(b: Board) -> Optional[str]:
    for i, j, k in WIN_LINES:
        if b[i] == b[j] == b[k] != " ":
            return b[i]
    return None

def is_full(b: Board) -> bool:
    return " " not in b

# ---------------------------------------------------------------------------
# Pretty printer with rock‑solid alignment
# ---------------------------------------------------------------------------

def _style_sq(sq: str) -> str:
    """Return a *two‑character‑wide* cell string, colourised if available."""
    if sq == " ":
        return "--"
    cell = sq
    if USE_COLOR:
        cell = f"{Fore.RED if sq == 'X' else Fore.BLUE}{sq}{Style.RESET_ALL}"
    return cell + " "  # pad to width 2

def draw_board(b: Board) -> str:
    cells = [_style_sq(s) for s in b]
    rows = [" {0}| {1}| {2} ".format(*cells[r:r + 3]) for r in range(0, 9, 3)]
    return "\n---+---+---\n".join(rows)

# ---------------------------------------------------------------------------
# Static evaluator + Minimax with α‑β pruning
# ---------------------------------------------------------------------------

def evaluate(b: Board) -> int:
    w = winner(b)
    return 1 if w == "X" else -1 if w == "O" else 0

def minimax(b: Board, player: str, alpha: int = -2, beta: int = 2,
            depth_limit: Optional[int] = None) -> Tuple[int, int]:
    """Return (best_score, nodes_examined) from position *b* with side *player*."""
    nodes = 1
    term = evaluate(b)
    if term or is_full(b) or depth_limit == 0:
        return term, nodes

    best = -2 if player == "X" else 2
    for i in range(9):
        if b[i] == " ":
            b[i] = player
            score, sub = minimax(b, "O" if player == "X" else "X",
                                   alpha, beta,
                                   None if depth_limit is None else depth_limit - 1)
            b[i] = " "
            nodes += sub

            if player == "X":
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if beta <= alpha:
                break  # prune
    return best, nodes


def choose_move(b: Board, player: str, level: str) -> Tuple[int, int]:
    """Return (square_index, nodes_examined) for *player* using given difficulty."""
    empties = [i for i, s in enumerate(b) if s == " "]
    if level == "easy":
        return random.choice(empties), 1
    depth_limit = 2 if level == "medium" else None

    best_idx, best_nodes = -1, 0
    best_score = -2 if player == "X" else 2
    for i in empties:
        b[i] = player
        score, nodes = minimax(b, "O" if player == "X" else "X", depth_limit=depth_limit)
        b[i] = " "
        if (player == "X" and score > best_score) or (player == "O" and score < best_score):
            best_score, best_idx, best_nodes = score, i, nodes
    return best_idx, best_nodes or 1

# ---------------------------------------------------------------------------
# Console I/O utilities
# ---------------------------------------------------------------------------

def ask_int(prompt: str, valid: range) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit() and int(s) in valid:
            return int(s)
        print(f"Invalid choice – enter {valid.start}-{valid.stop - 1}.")


def human_turn(b: Board, mark: str) -> None:
    while True:
        idx = ask_int(f"Your move ({mark}) 1‑9: ", range(1, 10)) - 1
        if b[idx] == " ":
            b[idx] = mark
            return
        print("That square is occupied.")


def ai_turn(b: Board, mark: str, level: str) -> None:
    idx, nodes = choose_move(b, mark, level)
    b[idx] = mark
    r, c = divmod(idx, 3)
    print(f"AI ({level}) plays ({r + 1},{c + 1}) – searched {nodes:,} nodes.")

# ---------------------------------------------------------------------------
# Game orchestration – supports Human vs AI *and* AI vs AI
# ---------------------------------------------------------------------------

def play(cfg: Dict[str, str], score: Dict[str, int]) -> None:
    board = make_empty_board()
    human_mark = cfg["human"]  # "X", "O", or "-" (no human)
    level = cfg["level"]

    # Mapping from mark → player‑type
    player_type = {"X": ("human" if human_mark == "X" else "ai"),
                   "O": ("human" if human_mark == "O" else "ai")}

    current_mark = "X"  # X always starts

    while True:
        print("\n" + draw_board(board) + "\n")

        if player_type[current_mark] == "human":
            human_turn(board, current_mark)
        else:
            ai_turn(board, current_mark, level)

        # Check for end of game
        w = winner(board)
        if w or is_full(board):
            print("\n" + draw_board(board))
            if human_mark != "-":  # update scoreboard only in human games
                if w == human_mark:
                    print("🎉 You win!")
                    score["wins"] += 1
                elif w is None:
                    print("It's a draw.")
                    score["draws"] += 1
                else:
                    print("🤖 AI wins.")
                    score["losses"] += 1
            else:  # AI vs AI summary
                if w:
                    print(f"🧠 AI playing '{w}' wins.")
                else:
                    print("It's a draw (AI vs AI).")
            break

        # Switch sides
        current_mark = "O" if current_mark == "X" else "X"

# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

def main_menu() -> Dict[str, str]:
    print("=== Advanced Tic‑Tac‑Toe ===")
    print("1. Play as X")
    print("2. Play as O")
    print("3. Watch AI vs AI")
    choice = ask_int("Select: ", range(1, 4))

    cfg: Dict[str, str] = {"level": "hard"}
    if choice == 3:
        cfg.update(human="-")
    elif choice == 1:
        cfg.update(human="X")
    else:
        cfg.update(human="O")

    print("\nAI difficulty:")
    print("1. Easy   (random)")
    print("2. Medium (depth‑2)")
    print("3. Hard   (perfect)")
    lvl = ask_int("Select: ", range(1, 4))
    cfg["level"] = {1: "easy", 2: "medium", 3: "hard"}[lvl]

    return cfg

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    scoreboard = {"wins": 0, "losses": 0, "draws": 0}
    print("Welcome – press Ctrl+C to quit at any time.")

    while True:
        cfg = main_menu()
        play(cfg, scoreboard)

        if cfg["human"] != "-":
            print(f"\nScore  W:{scoreboard['wins']} L:{scoreboard['losses']} D:{scoreboard['draws']}")
        if input("Play again? (y/n): ").strip().lower() != "y":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
