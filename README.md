# War Card Game Automata

This project implements a simplified version of the classic **War Card Game** as an automata simulation.
The game is based on a set of rules and transitions that determine the behavior of the players and the game's progression.
The simulation continues until a winner emerge.

## Rules

1. Each player starts with half of the shuffled deck.
2. In each round, both players reveal the top card of their decks.
3. The player with the higher card value wins the round and takes both cards.
4. In case of a tie, a battle occurs, and the process repeats until a winner is determined.
5. The simulation continues until one player has all 52 cards, making them the winner.

## Customization

You can customize the game by modifying the following parameters in the `main.py` file:

- `FPS`: Frames per second for the automata simulation.
- `SPEED`: Time between each card movement (in seconds). Set to 0 for instantaneous moves.

## Credits

The sprites used in this project are from [danimaccari](https://dani-maccari.itch.io/)
