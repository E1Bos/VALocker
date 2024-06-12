<h1 align="center">
  VALocker | VALORANT Agent Locker
</h1>

<br>
<div align="center">
  <img alt="License" src="https://img.shields.io/github/license/E1Bos/VALocker?color=brightgreen">
  <img alt="GitHub release version" src="https://img.shields.io/github/v/release/E1Bos/VALocker?color=blue">
  <img alt="GitHub all releases" src="https://img.shields.io/github/downloads/E1Bos/VALocker/total?color=yellow">
  <a href="https://ko-fi.com/G2G8O67MO"><img alt="Kofi donate link" src="https://ko-fi.com/img/githubbutton_sm.svg" height=20px></a>
</div>
<br>

VALocker is a program written in Python that allows you to automatically lock any VALORANT agent quickly and reliably. It helps you secure your favorite agent during the agent selection phase, saving you time and ensuring you don't miss out on playing your preferred character.

**Regarding Updates**: Don't expect many updates to VALocker in the coming months. I am now studying full-time at university and don't know if I will have the time to play Valorant or/and work on VALocker. I intend to release VALocker V2 soon, with a more intuitive GUI, an easier-to-maintain file structure, auto-update capability, and the ability to play on other window resolutions.

📋 **Changelog:** For a detailed list of changes, improvements, and bug fixes, refer to the [Changelog](changelog.md) file.

> **Disclaimer:**
> This program is not affiliated with or endorsed by Riot Games or VALORANT. The software is provided "as is" without any warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## 📰 New in v2.0.0

- Overhauled the entire UI, making it more responsivem consistent, and adding support for custom themes.
- All data files are now stored in `%APPDATA%\VALocker`, making the location of the executable irrelevant, and allowing for easy updates.
- Over-the-air updates for all config files. No need to redownload the project zip file and replace all files.
- All elements are dynamically rendered, meaning resizing the window (while not recommended, due to the lag of tkinter) is possible.
- Added loggers for all functions, making diagnosing issues easier.

## 📚 Features

### 🖥️ GUI

- User friendly GUI for easy interaction.
- Support for easy-to-modify custom themes.
- Can be run as an executable, no Python installation required.

### 🔄 Updates

- Automatically downloads all necessary config files.
- Automatically checks for updates when the program is opened with an hour minimum between checks.

### 🔒 Instalocking

- Automatically locks in your desired agent during the agent selection phase.
- Locks an agent in ~70ms on average from when the agent selection screen first appears.
- Automatically detects when you are no longer in game and switches to "Locking" mode.
- Hover mode allows you to select an agent without locking them, great for competitive.
- Safe mode adds random delays to the locking process:
  - Low 300-500ms
  - Medium 500-800ms
  - High 800-1000ms
- Works irrespective of how many agents you have unlocked (See [guide](#guide) for more information).
- **_(PLANNED, NOT IMPLEMENTED YET)_** Support for map-specific agent locking.

### 🕵️‍♂️ Anti-Detection

- Selects random part of agent and locking button so movement can't be predicted.
- Analyzes screenshots, taken hundreds of times per second to determine what is going on within the game, a safer approach which reduces the risk of bans significantly compared to other aggressive methods such as direct memory reading or API abuse.

### 🎲 Random Agent Selection

- Random agent mode allows random agent selection from a pool, for when you get bored of playing the same agent.
- ExclusiSelect (ES) mode disables random agents after they're picked, ensuring you don't get the same agent twice.
  - When ES is disabled, it refreshes random agent selections to what they were prior to ES being enabled.

### 📊 Stats

- Tracks the time to lock, total locks, and times locking a specific agent.
- Displays all stats in real time.

### 💾 Saves

- Allows for multiple save files for different accounts and/or configurations.
- Each save has its own selected agent, toggled agents, and random agents, allowing for more flexibility.

### 🔧 Tools

- Features non-instalocking related tools to improve quality of life. Tools only work when the instalocker is disabled, when the status says "In Game".
- Auto Drop Spike automatically drops the spike when you are holding it.
- Anti-AFK moves you around a random amount with a random delay.
  - Anti-AFK can be enabled with the instalocker functionality while queuing, allowing you to take a break from your computer and return without being kicked for inactivity or failing to pick an agent in time.
  - Anti-AFK automatically disables if your movement keys are pressed. Or, if "GRAB_KEYBINDS" is set to false in the user settings file, if "WASD" are pressed, ensuring it doesn't interefere with your game while you play.
- Automatically grabs your keybinds to ensure that the correct keys are pressed when using tools (can be disabled).

> Tools are still a work in progress. Feel free to suggest any tools you would like to see implemented.

## ⚙️ Installation

VALocker automatically downloads all config files and places them in the %APPDATA% folder, this makes the location of the executable irrelevant. The executable can be placed anywhere on your computer, and it will still function correctly.

### 💻 Executable

1. Download `VALocker.zip` from the [releases](https://github.com/E1Bos/VALocker/releases) page.
2. Extract `VALocker.exe` to a location of your choice.
3. Run `VALocker.exe` to launch the application.

### 🐍 Python

> I strongly reccommend using the executable version of VALocker, as it is easier to use, and doesn't require Python to be installed on your machine. Files will still be automatically downloaded, even if you cloned the repository.

1. Clone the repository to your local machine.
2. Make sure you have Python 3.x installed.
3. Run `pip install -r requirements.txt` to install all necessary dependencies.
4. Run `VALockerApp.pyw` to launch the application.

### 🔄 Updating

VALocker automatically checks for updates when it is opened and it's been at least an hour since it last checked for updates. All config files are automatically downloaded.

When a new release is available

1. Download the latest version from the [releases](https://github.com/E1Bos/VALocker/releases) page.
2. Close VALocker if it is currently running.
3. Extract `VALocker.exe` from the zip file.
4. Run `VALocker.exe` to launch the updated application, all config files are stored in the %APPDATA%.

## 🚀 Guide

1. Run `VALocker.exe` to launch the application. Allow the program to download all necessary files.
2. Head to the `Agent Toggle tab` on the left and select all agents that you have unlocked.
3. Head to the `Overview tab`, and select your desired agent from the dropdown menu.
4. Choose any additional options or settings based on your preference, such as the Hover mode or Safe mode by clicking their corresponding button.
5. Turn the instalocker on by clicking on the button under the label `Instalocker`. When the button says `Stopped` VALocker will not attempt to lock any agent. When the button says `Running`, VALocker will try to determine when you are queuing for a game.
6. The button labeled `Status` shows which task the instalocker is trying to complete. When it shows `Locking`, it will attempt to lock your agent if it detects the agent selection screen. When it says `Waiting`, it will try to determine when you are done with your current game. If the button shows `None`, the instalocker is stopped. Click on this button to swap the task.
7. During the agent selection phase in VALORANT, VALocker will automatically lock in your chosen agent. _Moving your mouse during this may make VALocker pick the incorrect agent or fail to click anything_.
8. The button labeled `Status` should now show `Waiting`. It will automatically switch to `Locking` when it detects you are done with your game.

### Other Functions

#### Random Agents

The `Random Agents tab` allows VALocker to select a random agent from a group of agents you select.

VALocker will only randomize its selection if at least 1 agent is selected in the `Random Agent tab` and `Random Agent` is enabled in the `Overview tab`.

ExclusiSelect (ES) mode disables random agents after they're picked, ensuring you don't get the same random agent twice. When an agent is locked while ES is enabled, its checkbox will be unselected. This shows which agents are still in the pool. When ES is disabled, it refreshes random agent selections to what they were prior to ES being enabled.

#### Save Files

The `Save Files tab` is used to change which save is active.

Add a new save using the `+` on the bottom right. Saves can be favorited, bringing them to the top, renamed, or deleted. The default save file can only be favorited.

Adding a new save file will require reconfiguring the `Agent Toggle tab`. Clicking on the name of your save file in the `Overview tab` will also direct you to the Save Files tab.

#### Tools

The `Tools tab` is used to enabled and disable the various QOL (Quality of Life) addons VALocker supports. Tools only work when the instalocker status is "Waiting" or "None".

Tools can be enabled and disabled, but are only active when the button above shows `Tools: Enabled` (the very long button).

Tools will automatically become active if the `Activate Tools Automatically` setting is enabled (default).

#### Settings

The `Settings tab` can be used to modify the various settings VALocker has.

## ❗ Important Information
- Without configuring VALocker, it will **ONLY** work if VALORANT is running at `1920x1080`.
- VALocker will not work if your framerate is uncapped. An uncapped framerate leads to the VALORANT UI not rendering properly.
- Programs like AMD Radeon Image Sharpening or Nvidia Freestyle that modify the game's visuals should be disabled as they can alter the VALORANT UI and interfere with VALockers screenshot detection.

## 🔧 Configuration

<!-- TODO: REWRITE -->

VALocker provides a `user_settings.yaml` file in the data directory where you can customize certain aspects of the program. The `user_settings.json` file is created when running the program for the first time.

Settings should be changed via the settings tab. There are 3 settings that can only be changed in the `user_settings.json` file:

- `"LOCKING_CONFIRMATIONS`: Defaulted to `3`. This determines how many times VALocker needs to detect the agent selection screen before locking the agent. This is to prevent false positives.
- `"MENU_CONFIRMATIONS"`: Defaulted to `3`. This provides the same functionality as locking_confirmations but for the main menu.
- `"FAST_MODE_TIMINGS"`: Defaulted to `[0.02, 0.02, 0.02]`. When safe mode is disabled, this determines the time between `[0]`: moving the mouse and selecting the agent, `[1]`: selecting the agent and moving over the lock button, and `[2]`: clicking the lock button. Making these values any smaller may lead to VALORANT not registering the mouse input. These values are in seconds.

Please only edit these values if you know what you are doing.

## 📏 Display Size Compatibility

I plan to add support for other display sizes in the future, but for now, VALocker only supports a resolution of 1920x1080. If you would like to see support for other display sizes, please let me know by [creating an issue](https://github.com/E1Bos/VALocker/issues).

## 🖼️ Images

<!-- TODO: UPDATE IMAGES -->

| ![overview_tab](images/readme_images/overview_tab.png)         | ![agent_toggle_tab](images/readme_images/agent_toggle_tab.png) | ![random_agent_tab](images/readme_images/random_agent_tab.png) |
| -------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------------- |
| ![map_specific_tab](images/readme_images/map_specific_tab.png) | ![save_file_tab](images/readme_images/save_file_tab.png)       | ![tools_tab](images/readme_images/tools_tab.png)               |
| ![settings_tab](images/readme_images/settings_tab.png)         |

## 🎥 Video Demo

<!-- TODO: UPDATE VIDEO -->

https://github.com/E1Bos/VALocker/assets/66886116/d1567740-3efe-408d-af09-fe2d2bf87f14

## 🤝 Contributing

Thank you for considering contributing to this project!

Please note that while I am actively maintaining and updating this project, I may not actively review or accept pull requests for changes or additions.

You are still welcome to fork this project and make your own modifications or enhancements. Feel free to experiment, customize, or extend the project based on your needs.

If you encounter any issues or bugs, please [create an issue](https://github.com/E1Bos/VALocker/issues) on the GitHub repository. I will do my best to address them when possible and provide support.

I appreciate your interest in this project!

## 🎉 Acknowledgements

VALocker utilizes the following libraries:

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - Customized version of the tkinter library.
- [PIL](https://python-pillow.org/) - Python Imaging Library for image manipulation.
- [pystray](https://github.com/moses-palmer/pystray) - Library for creating system tray icons.
- [pynput](https://pypi.org/project/pynput/) - Library for controlling and monitoring input devices.

## 📧 Contact

If you have any questions, feedback, or general inquiries, you may contact me at:

Discord: `@e1bos`

Feel free to reach out through the provided contact information for non-issue related matters or general discussions. However, for any project-related issues, I kindly ask that you [add an issue](https://github.com/E1Bos/VALocker/issues) to report and discuss them.

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the [LICENSE](LICENSE) file for more information.
