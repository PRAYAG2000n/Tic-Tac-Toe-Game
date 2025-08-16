# Tic-Tac-Toe-Game
A polished console Tic-Tac-Toe written in Python that lets you:

* play against a computer opponent with three difficulty levels  
  *(Easy = random, Medium = shallow Minimax, Hard = perfect play with α-β pruning)*  
* watch **AI vs AI** showdowns at any speed you like  
* track wins, losses, and draws across multiple rounds

The code is a single, dependency-light file (`tic_tac_toe_advanced.py`) that starts instantly on any modern Python.

---

## Features

| Feature | Notes |
|---------|-------|
| **Three AI levels** | switchable at runtime |
| **Minimax + alpha-beta pruning** | hard level always plays perfectly |
| **Depth-limited Minimax** | medium level looks two plies ahead |
| **AI vs AI demo mode** | pick option 3 → fully automated match |
| **Scoreboard** | persists across rounds until you quit |
| **Colour support** | optional, via `colorama`, falls back gracefully |
| **Clean prompts** | no misaligned boards or confusing input loops |

---

## Quick start

```bash
git clone https://github.com/PRAYAG2000n/Tic-Tac-Toe-Game.git
cd Tic-Tac-Toe-Game          # step into the project folder
pip install -r requirements.txt   # only needed for colour output (colorama)
python tic_tac_toe_advanced.py    # launch the game
```

### What you’ll see

```
=== Advanced Tic-Tac-Toe ===
1. Play as X
2. Play as O
3. Watch AI vs AI
```

1 / 2 = human plays, 3 = robo-duel.  
Then choose the AI difficulty (1 Easy, 2 Medium, 3 Hard) and enjoy.

---

## How to play

| Action | Example |
|--------|---------|
| **Select a square** | Enter a number 1-9 when prompted (`Your move (X) 1-9:`). Squares count left-to-right, top-to-bottom. |
| **Run another round** | After the result, type **`y`** when asked *“Play again? (y/n)”*. |
| **Quit** | Press **`n`** at that prompt or hit **Ctrl-C** at any time. |

In AI-vs-AI mode the program cycles through the whole game automatically—no human input required.

---

## Requirements

* Python ≥ 3.8  
* *(Optional)* **colorama** ≥ 0.4 for colourful X’s and O’s  

Install extras with:

```bash
pip install -r requirements.txt
```

The game still works perfectly without Colourama; you just won’t get coloured glyphs.

---

## Repository structure

```
.
├── tic_tac_toe_advanced.py   # main (and only) program file
├── requirements.txt          # optional colour dependency
├── .gitignore                # ignore __pycache__ etc.
└── README.md                 # you are here
```

---
## Running the code in Jupyter Notebook
[![Watch the video](https://i3.ytimg.com/vi/6yaeinD-S-s/maxresdefault.jpg)](https://www.youtube.com/watch?v=6yaeinD-S-s)

## Continuous integration (optional)

Add this YAML under `.github/workflows/ci.yml` to run a tiny smoke-test on every push:

```yaml
name: Tic-Tac-Toe smoke-test
on: [push, pull_request]
jobs:
  run-game:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      # feed menu choices: 3 (AI vs AI) then 3 (Hard) → game runs headless
      - run: printf "3\n3\n" | python tic_tac_toe_advanced.py > /dev/null
```

---

## Contributing
```
Bug reports, feature requests, and pull requests are welcome—just open an issue or PR on GitHub.
```
---
