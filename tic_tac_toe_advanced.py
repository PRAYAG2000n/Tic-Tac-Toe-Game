from __future__ import annotations
import random
import sys
from typing import List, Optional, Tuple, Dict

# ----------------------------- optional colours -----------------------------
try:
    from colorama import Fore, Style, init as _cinit  # type: ignore
    _cinit()
    _USE_COLOUR = True
except Exception:
    _USE_COLOUR = False

# ------------------------------- basic helpers ------------------------------
Board = List[str]  # 9 cells, each "X", "O", or " "
_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6),             # diags
]

def new_board() -> Board:
    return [" "] * 9

def won(b: Board) -> Optional[str]:
    for a, c, d in _LINES:
        if b[a] == b[c] == b[d] != " ":
            return b[a]
    return None

def full(b: Board) -> bool:
    return " " not in b

# ------------------------------ board printing ------------------------------
def _paint(mark: str) -> str:
    """Two-char cell string. ANSI colour if available, but width stays steady."""
    if mark == " ":
        return "--"
    if not _USE_COLOUR:
        return mark + " "
    col = Fore.RED if mark == "X" else Fore.BLUE
    return f"{col}{mark}{Style.RESET_ALL} "

def board_text(b: Board) -> str:
    cells = [_paint(x) for x in b]
    rows = [f" {cells[i]}| {cells[i+1]}| {cells[i+2]} " for i in (0, 3, 6)]
    return "\n---+----+----\n".join(rows)

# ---------------------------- evaluation / search ---------------------------
def score(b: Board) -> int:
    w = won(b)
    if w == "X":
        return 1
    if w == "O":
        return -1
    return 0

def minimax(b: Board,
            to_move: str,
            alpha: int = -2,
            beta: int = 2,
            depth: Optional[int] = None) -> Tuple[int, int]:
    """Return (best_score, nodes_visited) for the side 'to_move'."""
    nodes = 1
    terminal = score(b)
    if terminal or full(b) or depth == 0:
        return terminal, nodes

    best = -2 if to_move == "X" else 2
    nxt = "O" if to_move == "X" else "X"

    for i in range(9):
        if b[i] != " ":
            continue
        b[i] = to_move
        child, sub = minimax(b, nxt, alpha, beta, None if depth is None else depth - 1)
        b[i] = " "
        nodes += sub

        if to_move == "X":
            if child > best:
                best = child
            if best > alpha:
                alpha = best
        else:
            if child < best:
                best = child
            if best < beta:
                beta = best

        if beta <= alpha:  # prune
            break

    return best, nodes

def pick_move(b: Board, side: str, level: str) -> Tuple[int, int]:
    """Choose a move for 'side'. Returns (index, nodes_visited)."""
    empties = [i for i, v in enumerate(b) if v == " "]
    if not empties:
        return -1, 1

    if level == "easy":
        return random.choice(empties), 1

    depth = 2 if level == "medium" else None  # 'hard' uses full search
    best_i = -1
    best_nodes = 0
    best_val = -2 if side == "X" else 2
    other = "O" if side == "X" else "X"

    for i in empties:
        b[i] = side
        val, nodes = minimax(b, other, depth=depth)
        b[i] = " "
        if (side == "X" and val > best_val) or (side == "O" and val < best_val):
            best_val, best_i, best_nodes = val, i, nodes

    return best_i, (best_nodes or 1)

# ------------------------------- user I/O bits ------------------------------
def ask_int(msg: str, ok: range) -> int:
    while True:
        s = input(msg).strip()
        if s.isdigit() and int(s) in ok:
            return int(s)
        print(f"Enter a number in [{ok.start}-{ok.stop - 1}]")

def human_move(b: Board, side: str) -> None:
    while True:
        pos = ask_int(f"Your move ({side}) [1-9]: ", range(1, 10)) - 1
        if b[pos] == " ":
            b[pos] = side
            return
        print("That spot is taken. Try again.")

def ai_move(b: Board, side: str, level: str) -> None:
    idx, nodes = pick_move(b, side, level)
    b[idx] = side
    r, c = divmod(idx, 3)
    print(f"AI ({level}) played ({r+1},{c+1}) — searched {nodes:,} nodes.")

# -------------------------------- game driver -------------------------------
def run_game(cfg: Dict[str, str], tally: Dict[str, int]) -> None:
    board = new_board()
    who_is_human = cfg["human"]     # "X", "O", or "-" for AI vs AI
    level = cfg["level"]            # "easy" | "medium" | "hard"

    player_kind = {"X": ("human" if who_is_human == "X" else "ai"),
                   "O": ("human" if who_is_human == "O" else "ai")}
    turn = "X"  # X starts

    while True:
        print("\n" + board_text(board) + "\n")

        if player_kind[turn] == "human":
            human_move(board, turn)
        else:
            ai_move(board, turn, level)

        w = won(board)
        if w or full(board):
            print("\n" + board_text(board))
            if who_is_human == "-":
                # pure AI match
                print(f"\nResult: {'draw' if w is None else w + ' wins'} (AI vs AI)")
            else:
                if w is None:
                    print("\nIt's a draw.")
                    tally["draws"] += 1
                elif w == who_is_human:
                    print("\nYou win!")
                    tally["wins"] += 1
                else:
                    print("\nAI wins.")
                    tally["losses"] += 1
            break

        turn = "O" if turn == "X" else "X"

# ---------------------------------- menus -----------------------------------
def choose_setup() -> Dict[str, str]:
    print("=== Tic-Tac-Toe ===")
    print("1) Play as X")
    print("2) Play as O")
    print("3) Watch AI vs AI")
    sel = ask_int("Select: ", range(1, 4))

    cfg: Dict[str, str] = {"level": "hard"}
    if sel == 1:
        cfg["human"] = "X"
    elif sel == 2:
        cfg["human"] = "O"
    else:
        cfg["human"] = "-"

    print("\nAI difficulty:")
    print("1) Easy   (random)")
    print("2) Medium (depth-2)")
    print("3) Hard   (perfect)")
    lvl = ask_int("Select: ", range(1, 4))
    cfg["level"] = {1: "easy", 2: "medium", 3: "hard"}[lvl]

    return cfg

# ---------------------------------- main ------------------------------------
def main() -> None:
    scores = {"wins": 0, "losses": 0, "draws": 0}
    print("Press Ctrl+C to quit.\n")
    while True:
        setup = choose_setup()
        run_game(setup, scores)
        if setup["human"] != "-":
            print(f"\nScore  W:{scores['wins']}  L:{scores['losses']}  D:{scores['draws']}")
        again = input("Play again? (y/n): ").strip().lower()
        if again != "y":
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)
