# Changelog

Date Format: YYYY-MM-DD

## Version 2.0.5 | 2024-07-10

### Added

- Various settings to the settings tab:
  - Startup
    - Enable Instalocker on startup
    - Enable Safe Mode on startup
    - Safe Mode strength on startup
  - General
    - Auto Start Tools (Enabled by default)
      > Will automatically start the tools thread if a tool is enabled and the tools thread is not running, and will automatically stop the tools thread if no tools are enabled.
    - Anti AFK movement type
      > The type of movement the anti-afk tool will use. Options are "Random Centered", "Random", "Circle", and "Strafe". Default is set to "Random Centered".

### Changes

- Updated rounded corners of some GUI elements to be more consistent with the rest of the GUI.
- Moved the `ANTI_AFK` enum to `Constants.py`
- Favorited save files have a thin accent border around them to make them stand out more.

### Fixed

- Favorited save files would be duplicated when manually updating VALocker.
- Renaming a favorited save file would not correctly rename it in the settings file causing it to no longer be favorited.
- Renaming the active save file would not correctly rename it in the settings file causing it to no longer be the active save file.
- Save files being ordered alphabetically by capital letter, then lowercase letter.
- Save files not being rendered after creating/renaming a safe file

> This is the first time trying out OTA config file updates, previous settings will be overwritten. I have implemented a feature to prevent this is the new update. If you have any issues, please let me know.

## Version 2.0.0 | 2024-06-15

### Changes

- Rewrote the entire program from scratch
- Moved save location to `%APPDATA%/VALocker`
- Swapped mss for betterDXcam, a fork of DXcam
- Improved how the UI looks
- Made GUI more responsive by adding button highlights
- Set tools thread to automatically start if a tool is enabled from the overview frame

## Added

- Automatic over the air updates for config files
- Automatic downloading for files that are missing/required
- Support for new resolutions
- Ability to customize the theme

## Removed

- Removed Specific Map tab
- Removed the ability to minimize to tray

## Version 1.6.0 | 2024-04-02

> Modified the repo to remove any instance of my full name. License has not changed, but goes under my username (E1Bos) instead of legal name. Changelog will still have information on previous commits but the commits have been squashed and all previous releases have been removed.

## Version 1.5.15 | 2024-04-01

### Fixed

- Can detect top of banner to return to the "Locking State". The color was slightly modified.

## Version 1.5.14 | 2024-03-28

### Added

- Added Clove to agent list.

### Fixed

- Slightly modified UI to fix width issue with the Safe Mode button.

## Version 1.5.13 | 2023-12-18

### Changed

- Removed unnecessary python dependencies and updated to Python 3.11.

## Version 1.5.12 | 2023-10-02

### Added

- Added Iso to agent list.

> I am currently working on a laptop, so there is a chance that VALocker isn't functioning properly. There is nothing I can do about this.

## Version 1.5.11 | 2023-09-28

### Fixed

- Fixed version number. VALocker v1.5.10 was stuck asking users to update their version, even though they were on the latest version. This was due to the version number being set to 1.5.9 instead of 1.5.10. This has been fixed with this new release.

## Version 1.5.10 | 2023-09-16

### Fixed

- Fixed the "On" button for safe mode being red if safe mode is enabled on startup and instalocking is disabled.
- Fixed the `user_settings.json` file not being created if it does not exist, leading to the program just crashing over and over.

## Version 1.5.9 | 2023-09-01

### Added

- Support for new Sunset map, old save files will automatically update themselves to include the new map without user input or data loss.
- Sunset image added to map images.

## Version 1.5.8 | 2023-08-29

### Added

- Anti AFK and Auto Drop Spike can now be enabled from the overview tab.
- New setting "Auto Start Tools" automatically enables the tools thread when specific tools are enabled. i.e. If you enable anti-afk, it will automatically enable the tools thread. This is enabled by default.

### Changed

- Overview tab is less cluttered, buttons that are just "Enabled" and "Disabled" have been had their label integrated into the button. Hover, Random Agents, and Map Specific are under the "Options" label.
- Button sizes have been increased on the overview tab.

### Fixed

- Toggle agent tab and random agent tab would not update when loading a save file or creating a new save file. This was due to the GUI being rewritten. This has been fixed.

## Version 1.5.7 | 2023-08-22

### Changed

- GUI boot speeds have been improved. The GUI should now load in ~1.5 seconds (confirmed running `VALocker.pyw`), compared to the previous ~5-6 seconds. Previously, the GUI had to be updated after being created to display the correct information. The GUI creation function has been modified and the GUI is now ready-to-go after being created.
- Hover mode no longer moves the mouse over the lock button. This stops you from accidentally clicking and locking your agent.
- Uses faster screenshot method, you should lock your agent even faster.
- Using the .get method, user settings are no longer reset to default values whenever new settings are added. All setting should persist between updates. If you are updating from a version prior to 1.5.7, your settings will be reset to default values. If you are updating from a version after 1.5.7, your settings will be preserved.

## Version 1.5.6 | 2023-08-14

### Added

- New Setting, "Anti AFK Drops Spike". When Anti AFK is enabled, the spike will be automatically dropped while you are AFK. This gives your team a fighting chance if they drop you the spike while AFK. Its disabled by default.
- Tools will stop running if the user is spectating a player, however, detection stops when chat is open, and may be disabled when multiple chat messages are sent, so it may not be 100% accurate.
- New setting "Detect Opened Chat (KB)" uses a keyboard listener to detect when the enter and esc keys are pressed. Pressing the enter key will toggle between the program thinking the chat is open and closed, and pressing the esc key will signal that the chat is closed. This is enabled by default. When the chat is flagged as opened, tools will not function, so you can type without tools interfering. This setting is enabled by default.
  > This implementation **WILL NOT** work perfectly. Pressing enter to autofill when private messaging someone will trick the program into thinking the chat is closed. Use the tab key instead. Clicking on the chat box will **not** flag the chat as opened. I am working on an implementation that works using visuals, but it is not ready yet. VALocker **cannot** detect is the focused window, so if you alt-tab out of the game, and use your keyboard, the chat flag may change, and tools may run and interfere with other applications.
  > Detection only starts **after** tools are enabled. If you enable tools while the chat is open, VALocker will not detect the chat as open. To ensure that the chat is detected as closed, make sure to press the esc key.
  - When visual detection is added, this setting will switch between detection through visuals and detection through keyboard inputs.

### Fixed

- VALocker would not switch to "Locking" when not ranked and playing comp.

## Version 1.5.5 | 2023-08-08

### Added

- Type of anti-afk movement now configurable in the settings tab. The options are "Forward", "Strafe", "Circle", "Random", and "Random Centered. VALocker will be unable to detect when you return from being AFK while it is moving your character, so longer movement cycles such as "Circle" may not be ideal, however, it offers more movement. Default is set to "Forward".
- Start minimized not toggleable if minimize to tray is disabled.

### Fixed

- VALocker would not switch back to "Locking" right after a game because the text was moved slightly. This has been fixed.

## Version 1.5.4 | 2023-08-01

### Added

- VALocker now checks for the latest version on startup. If a new version is available, a popup will appear with a link to the latest release.
- Stats are now saved in a separate "stats.json" file, when VALocker is updated, your stats will not be lost.

### Changed

- Default keybinds now stored in the config.json file instead of its own file.

## Version 1.5.3 | 2023-08-01

### Added

- Added settings tab, allowing the user to change most settings without having to edit the user settings file.

## Version 1.5.2 | 2023-07-11

### Added

- "LOCKING_CONFIRMATIONS" and "MENU_CONFIRMATIONS" to user settings. This lets you change how many consecutive frames VALocker needs to detect you being in the agent selection screen or menu screen.

### Changed

- Default locking confirmations changed from 2 to 3.

## Version 1.5.1 | 2023-07-11

### Fixed

- Instalocker would select wrong agent when a new agent was unlocked. The coords were not recalculated.
- Fixed padding on tools tab.

## Version 1.5.0 | 2023-07-08

### Added

- VALocker automatically clones the VALORANT log file, keybinds file, and user game settings file to find which account is currently being used, then grabs any custom keybinds from that account. If keybinds such as Mouse Buttons are used, this feature may fail and "GRAB_KEYBINDS" should be set to false in the user settings file. This feature is enabled by default.
- Added new tool, "Anti AFK". This feature will press your movement keys every 5 seconds to prevent you from being kicked for being AFK. This feature is can be enabled in the tools tab. The anti-afk method can be changed to move the user around forward and backwards, to move the user in a circle, or press random movement keys. Currently the anti-afk mode is hard-coded to circle, but when the settings tab is fully implemented, this will be configurable.
- VALocker now grabs your current game resolution. At the moment, it brings up a error message if the resolution is not 1920x1080, but in the future this feature will be expanded to detect the game resolution and adjust the pixel data accordingly.
- If the instalocker is running, tools will only run if the instalocker is in the "In Game" state. This is to prevent tools from running while attempting to lock.

## Version 1.4.3 | 2023-07-05

### Changes

- Updated almost all game methods (locking, waiting, tools, etc.) to compare pixel data instead of image data. This should improve performance, reduces file size, and makes implementing new tools easier. Maps are still compared using image data, as I'm not sure how to compare pixel data for maps yet.
- Updated the layout of the tools tab to appear similar to the save file tab.

## Version 1.4.2 | 2023-07-03

### Fixed

- Occasionally, while flashed, the instalocker would return to "Locking", this has been fixed by requiring multiple consecutive frames to match before returning to "Locking".

## Version 1.4.1 | 2023-06-29

### Added

- Tools tab added, with features that are not related to locking agents but more improving the Valorant experience.
- Tools run independently of the locking thread, so you can use tools without locking agents. To enable them, go to the tools tab and ensure the button at the top of the screen says "Tools Enabled".
- New tool, auto drop spike, automatically detects when you are the spike carrier and drops the spike. This is useful if you don't want to be the spike carrier, but don't want to drop the spike manually, or if players keep dropping you the spike. If you pick up the spike on site, or if you are planting, the spike will not be dropped. I plan to update it in the future so that it automatically disables when you are the last player alive.

## Version 1.4.0 | 2023-06-28

### Added

- Support for new agent "Deadlock".
- New option in user_settings, "FAST_MODE_TIMINGS", the set delay between each action when safe mode is disabled. Default is set to 0.2, 0.2, 0.2. This can be changed if your computer is slower and is struggling to keep up with the default timings. Setting the numbers too low or to zero may cause issues while locking, such as button presses not being registered by Valorant.

### Fixed

- Fixed bug where icons would not update after locking or detecting the end of a game.
- Fixed various minor bugs.

## Version 1.3.2 | 2023-06-25

### Added

- New custom icons, the old icons were a rip off of the Valorant icons. The new icons are custom made to show "VL", which is short for VALocker. When disabled, the icons will be greyed out. When enabled, the icon will be colored. While VALocker is set to "Locking", the icon features a lock. While VALocker is set to "In Game", the icon features an hourglass. The icons are displayed in the taskbar, and in the system tray. The icons are also displayed in the GUI, in the top left corner of the window.
- New config option "HIDE_DEFAULT_SAVE_FILE" allows the user to hide the default save file from the save file tab. This is useful if you have a lot of save files or don't like how the default file is displayed right after the favorited files. This is set to true by default, and can be changed in the user settings file.

### Removed

- Old icons, which were somewhat confusing when Valorant was running.

## Version 1.3.0 | 2023-06-24

### Added

- Navigation bar on the left side of the GUI. This will allow for easier navigation between tabs.

### Changed

- The Exit button has been moved to the bottom of the navigation bar, so that the GUI can be closed from any tab.
- The UI is a lot more consistent. All tabs have the same padding and checkboxes are properly aligned.
- Theme changed from "blue" to "dark-blue". This is a lot easier on the eyes, and looks a lot better.
- Font changed from "Arial" to "Roboto".

### Fixed

- Fixed bug where the role checkboxes in the random agent tab would not deselect when a new agent was unlocked in the agent toggle tab.
- Fixed bug where map dropdown would expand when an agent with a long name was selected. (i.e. Brimstone)

## Version 1.2.5 | 2023-06-24

### Added

- Added automatic releases and automatic compilation to exe. Releases can be found [here](https://github.com/E1Bos/VALocker/releases).

## Version 1.2.2 | 2023-06-22

### Added

- Error dialogue boxes now show "Ok" and "Cancel". Ok will reopen the input box, and cancel will close the input box, allowing the user to try again if they wish.
- 'Esc' key can now be used to close the input box or error box. 'Return' will prompt the user to try again.

### Updated

- Updated renaming and creating save files. If input is valid, previous input will be displayed in the input box. Also added error for unsupported characters. i.e. `\ / : \* ? " < > |`

## Version 1.2.1 | 2023-06-22

### Added

- Added "PERSISTENT_RANDOM_AGENTS" to user settings. When enabled, adjusting your random agents while exclusiselect is enabled will revert to the selected agents prior to enabling exclusiselect. When disabled, adjusting your random agents while exclusiselect is enabled will update the random agent list and will keep any changes made by exclusiselect.

### Fixed

- Fixed bug where exclusiselect would not update the GUI when selecting an agent.
- Fixed bug where exclusiselect would not deselect randomly selected agent checkbox.

## Version 1.1.1 | 2023-06-19

### Fixed

- Fixed bug where the "All" checkbox would not update if random agents are selected by role.
- Fixed bug where the "None" checkbox would not update if random agents are selected by role.

## Version 1.1.0 | 2023-06-19

### Changes

- Updating the GUI uses match-case statements. GUI updates are much faster.
- The label for the current save file is now a button and when clicked, it will open the save file tab.

## Version 1.0.2 | 2023-06-17

### Fixed

- Fixed bug where when instalocker is waiting for the end of a game, and the instalocker is stopped, it will stop searching for the end of the game when re enabled.

## Version 1.0.1 | 2023-06-15

### Changes

- Text of new save button has been replaced with an icon.

## Version 1.0.0 | 2023-06-15

### Added

- New save file tab. All save files are displayed in a scrollable window.
- To be able to quickly find the current save file, it is highlighted in green.
- Ability to favorite save files, which will be displayed at the top of the save file tab, and cannot be deleted. They can be unfavorited, which will remove them from the top of the list, but they will still be displayed in the list of save files. They are stored in "user_settings.json" under "FAVORITED_SAVE_FILES".
- Ability to rename save files with the use of a popup window.
- Ability to delete save files, requiring confirmation from a popup window. Favorited save files, the selected save file, and the default file cannot be deleted.
- Ability to create new save files.
- Added changelog.

### Changed

- Current save file label is displayed where the old selection combobox was.

### Removed

- Old method of creating new save files and selecting save files.
- Old save file combobox on overview tab, replaced with separate save file selection.
