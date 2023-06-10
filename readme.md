# VaLocker - Valorant Agent Locker

VaLocker is a Python program that allows you to automatically lock in your desired Valorant agent quickly and reliably. It helps you secure your favorite agent during the agent selection phase, saving you time and ensuring you don't miss out on playing your preferred character.

## Features

- Installs all necessary dependencies automatically.
- Provides a user-friendly GUI for easy interaction.
- Allows the window to be minimized into an icon.
- Load-to-lock time of 100ms on average.
- Supports map-specific agent locking.
- Safe mode adds random delays to the locking process for a more cautious approach.
    - Low 300-500ms
    - Medium 500-800ms
    - High 800-1000ms
- Hover mode allows you to select an agent without locking them.
- Random agent mode allows random agent selection from a pool, adding variety and reducing repetition.
- ExclusiSelect disables random agents after they're picked, ensuring a new agent every time.
- Tracks and displays average time to lock in agents.
- Auto-detects game end screen for set-and-forget relocking.
- Allows for multiple save files for different accounts and configurations.

## Installation

1. Clone the repository to your local machine.
2. Make sure you have Python 3.x installed.

## Usage

1. Run the `VaLocker.pyw` file to launch the application. If it's your first time running the program, it will automatically install the necessary dependencies. Wait for the installation process to complete.
2. Enable all your unlocked agents in the toggle agent screen.
2. Select your desired agent from the dropdown menu.
3. Choose any additional options or settings based on your preference.
4. Enable the instalocker by clicking on the button under "Instalocker" to initiate the agent locking process.
5. During the agent selection phase in Valorant, VaLocker will automatically lock in your chosen agent.

## Configuration

VaLocker provides a `user_settings.json` file in the data directory where you can customize certain aspects of the program. The `user_settings.json` file is created when running the program for the first time. The configuration file allows you to:

- Toggle icon feature
- Minimize on startup
- Instalocking on startup
- Enable safe mode on startup
- Alter safe mode strength on startup


## Contributing

Contributions to VaLocker are welcome! If you would like to contribute to the project, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and ensure the code passes all tests.
4. Commit your changes and push them to your forked repository.
5. Submit a pull request, describing your changes in detail.

## Acknowledgements

VaLocker utilizes the following libraries:

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - Customized version of the tkinter library.
- [PIL](https://python-pillow.org/) - Python Imaging Library for image manipulation.
- [pynput](https://pypi.org/project/pynput/) - Library for controlling and monitoring input devices.
- [pystray](https://github.com/moses-palmer/pystray) - Library for creating system tray icons.
- [tkinter](https://docs.python.org/3/library/tkinter.html) - Python's standard GUI library.
- [random](https://docs.python.org/3/library/random.html) - Built-in Python library for random number generation.
- [threading](https://docs.python.org/3/library/threading.html) - Built-in Python library for multi-threading.
- [json](https://docs.python.org/3/library/json.html) - Built-in Python library for working with JSON data.
- [os](https://docs.python.org/3/library/os.html) - Built-in Python library for interacting with the operating system.
- [random](https://docs.python.org/3/library/random.html) - Built-in Python library for random number generation.
- [threading](https://docs.python.org/3/library/threading.html) - Built-in Python library for multi-threading.
- [time](https://docs.python.org/3/library/time.html) - Built-in Python library for time-related functions.


## Contact

For any questions, issues, or feedback, please contact the project maintainer:

Discord: @e1bos

Feel free to reach out with any inquiries or suggestions you may have. I appreciate your interest in VaLocker!