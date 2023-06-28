# VALocker - VALORANT Agent Locker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

VALocker is a program written in Python that allows you to automatically lock any VALORANT agent quickly and reliably. It helps you secure your favorite agent during the agent selection phase, saving you time and ensuring you don't miss out on playing your preferred character.

📋 **Changelog:** For a detailed list of changes, improvements, and bug fixes, refer to the [Changelog](changelog.md) file.

> **Disclaimer:**
> This program is not affiliated with or endorsed by Riot Games or VALORANT. The software is provided "as is" without any warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## 📚 Features
- Provides a user-friendly GUI for easy interaction.
- Can be run as an executable, no Python installation required.
- Installs all necessary dependencies automatically.
- Allows the window to be minimized into an icon.
- Load-to-lock time of 70ms on average.
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
- Allows for multiple save files for different accounts and/or configurations.
- Utilizes screenshot analysis to obtain game data, ensuring a safer approach and reducing the risk of bans compared to other aggressive methods such as direct memory reading.

## ⚙️ Installation
### Executable
1. Download `VALocker.zip` from the [releases](https://github.com/E1Bos/VALocker/releases) page.
2. Extract the file to a location of your choice.
3. Run `VALocker.exe` to launch the application.

### Python
1. Clone the repository to your local machine.
2. Make sure you have Python 3.x installed.
3. Run `VALocker.pyw` to launch the application, dependancies will be installed automatically.

## 🚀 Usage
1. Run `VALocker.exe` to launch the application. If you are running the Python version, run `VALocker.pyw` instead, dependancies will be installed automatically.
2. Enable all your unlocked agents in the toggle agent screen.
3. Select your desired agent from the dropdown menu.
4. Choose any additional options or settings based on your preference.
5. Enable the instalocker by clicking on the button under "Instalocker" to initiate the agent locking process, the button should switch from "Stopped" to "Running", and the button titled "Current Task" should change to "Locking Agent".
6. During the agent selection phase in VALORANT, VALocker will automatically lock in your chosen agent.
7. Once the agent is locked, the button under "Current Task" will change to "In Game", once it detects the end of the game, it will automatically switch to "Locking". The mode can be changed at any time by clicking on the button.

**Note:** VALocker relies on specific display settings for accurate functionality. Please ensure that your VALORANT game is running at a screen resolution of 1920x1080 with letterbox enabled. Deviating from these settings may result in incorrect behavior of the program.

## 🔧 Configuration
VALocker provides a `user_settings.json` file in the data directory where you can customize certain aspects of the program. The `user_settings.json` file is created when running the program for the first time. The configuration file allows you to:

- Toggle icon feature
- Minimize on startup
- Instalocking on startup
- Enable safe mode on startup
- Alter safe mode strength on startup

## 📏 Display Size Compatibility
I plan to add support for other display sizes in the future, but for now, VALocker only supports a resolution of 1920x1080. If you would like to see support for other display sizes, please let me know by [creating an issue](https://github.com/E1Bos/VALocker/issues).

## 🖼️ Images
|![overview_tab](images/readme_images/overview_tab.png)|![agent_toggle_tab](images/readme_images/agent_toggle_tab.png)|![random_agent_tab](images/readme_images/random_agent_tab.png)|
|-|-|-|
|![map_specific_tab](images/readme_images/map_specific_tab.png)|![save_file_tab](images/readme_images/save_file_tab.png)|

## 🎥 Video Demo

https://github.com/E1Bos/VALocker/assets/66886116/d1567740-3efe-408d-af09-fe2d2bf87f14

## 🤝 Contributing
Thank you for considering contributing to this project! I greatly appreciate your interest and support.

Please note that while I will be actively maintaining and updating this project, I may not actively review or accept pull requests for changes or additions at this time.

You are still welcome to fork this project and make your own modifications or enhancements. Feel free to experiment, customize, or extend the project based on your needs.

If you encounter any issues or bugs, please feel free to [create an issue](https://github.com/E1Bos/VALocker/issues) on the GitHub repository. I will do my best to address them and provide support.

Thank you for your understanding, and I appreciate your interest in this project!

## 🎉 Acknowledgements
VALocker utilizes the following libraries:

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - Customized version of the tkinter library.
- [PIL](https://python-pillow.org/) - Python Imaging Library for image manipulation.
- [pystray](https://github.com/moses-palmer/pystray) - Library for creating system tray icons.
- [pynput](https://pypi.org/project/pynput/) - Library for controlling and monitoring input devices.

## 📧 Contact
If you have any questions, feedback, or general inquiries, you may contact me at:

Discord: @e1bos

Feel free to reach out through the provided contact information for non-issue related matters or general discussions. However, for any project-related issues, I kindly ask that you [add an issue](https://github.com/E1Bos/VALocker/issues) to report and discuss them.

Thank you for your understanding and cooperation.

## 📜 License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). Please see the [LICENSE](LICENSE) file for more information.
