# Arrow Game

## Description
Arrow Game is a fun, interactive computer vision-based game that uses hand tracking to simulate archery. The goal is to shoot arrows at moving heart targets using real-world arm movements.

## Features
- **Pose Detection**: Uses MediaPipe Pose to track arm movements.
- **Bow Simulation**: Draws a virtual bow based on hand position.
- **Arrow Shooting**: Players can shoot arrows by pulling back their hand.
- **Moving Targets**: Hearts move across the screen and need to be hit with arrows.
- **Scoring System**: Earn points for each successful hit.

## Requirements
- Python 3.7+
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- NumPy (`numpy`)

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/arrow-game.git
   cd arrow-game
   ```
2. Install dependencies:
   ```sh
   pip install opencv-python mediapipe numpy
   ```
3. Place `heart.png` in the project directory.

## How to Play
1. Run the game:
   ```sh
   python arrow_game.py
   ```
2. Follow the on-screen instructions:
   - Raise your right arm to draw the bow.
   - Pull back to charge the shot.
   - Release to fire an arrow.
   - Hit as many hearts as possible to score points!
3. Press `q` to exit the game.

## Controls
- **Enter Key**: Start the game.
- **Raise and move your right arm**: Aim and shoot.
- **Press `q`**: Quit the game.

## Future Improvements
- Add difficulty levels.
- Improve target animations.
- Introduce power-ups.

## Author
Arqam Hussain

## License
This project is open-source. Feel free to modify and contribute!

