# VALocker - Valorant Agent Locker

VALocker is a Python program that allows you to automatically lock in your desired Valorant agent quickly and reliably. It helps you secure your favorite agent during the agent selection phase, saving you time and ensuring you don't miss out on playing your preferred character.

## Features

- Provides a user-friendly GUI for easy interaction.
- Installs all necessary dependencies automatically.
- Allows the window to be minimized into an icon.
- Load-to-lock time of 100ms on average.
- Auto-detects game end screen for set-and-forget relocking.
- Supports map-specific agent locking.
- Random agent mode allows random agent selection from a pool, adding variety and reducing repetition.
- ExclusiSelect disables random agents after they're picked, ensuring a new agent every time.
- Hover mode allows you to select an agent without locking them.
- Safe mode adds random delays to the locking process for a more cautious approach.
  - Low 300-500ms
  - Medium 500-800ms
  - High 800-1000ms
- Tracks and displays average time to lock and last lock in real time.
- Selects random part of agent and locking button to deter detection.
- Allows for multiple save files for different accounts and configurations.

## Installation

1. Clone the repository to your local machine.
2. Make sure you have Python 3.x installed.

## Usage

1. Run `VALocker.pyw` to launch the application. If it's your first time running the program, it will automatically install the necessary dependencies. Wait for the installation process to complete. If using the executable, simply run `VALocker.exe`.
2. Enable all your unlocked agents in the toggle agent screen.
3. Select your desired agent from the dropdown menu.
4. Choose any additional options or settings based on your preference.
5. Enable the instalocker by clicking on the button under "Instalocker" to initiate the agent locking process.
6. During the agent selection phase in Valorant, VALocker will automatically lock in your chosen agent.

## Configuration

VALocker provides a `user_settings.json` file in the data directory where you can customize certain aspects of the program. The `user_settings.json` file is created when running the program for the first time. The configuration file allows you to:

- Toggle icon feature
- Minimize on startup
- Instalocking on startup
- Enable safe mode on startup
- Alter safe mode strength on startup


## Contributing

Contributions to VALocker are welcome! If you would like to contribute to the project, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure the code passes all tests.
4. Commit your changes and push them to your forked repository.
5. Submit a pull request, describing your changes in detail.

## Acknowledgements

VALocker utilizes the following libraries:

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - Customized version of the tkinter library.
- [json](https://docs.python.org/3/library/json.html) - Built-in Python library for working with JSON data.
- [os](https://docs.python.org/3/library/os.html) - Built-in Python library for interacting with the operating system.
- [PIL](https://python-pillow.org/) - Python Imaging Library for image manipulation.
- [pystray](https://github.com/moses-palmer/pystray) - Library for creating system tray icons.
- [pynput](https://pypi.org/project/pynput/) - Library for controlling and monitoring input devices.
- [random](https://docs.python.org/3/library/random.html) - Built-in Python library for random number generation.
- [threading](https://docs.python.org/3/library/threading.html) - Built-in Python library for multi-threading.
- [time](https://docs.python.org/3/library/time.html) - Built-in Python library for time-related functions.
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python's standard GUI library.


## Contact

For any questions, issues, or feedback, please contact the project maintainer:

Discord: @e1bos

Feel free to reach out with any inquiries or suggestions you may have. I appreciate your interest in VALocker!