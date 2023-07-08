Changelog
=========

Date Format: YYYY-MM-DD

## Version 1.4.3 - 2023-07-05

### Changes
- [Feature] Updated almost all game methods (locking, waiting, tools, etc.) to compare pixel data instead of image data. This should improve performance, reduces file size, and makes implementing new tools easier. Maps are still compared using image data, as I'm not sure how to compare pixel data for maps yet.
- [Feature] Updated the layout of the tools tab to appear similar to the save file tab.

## Version 1.4.2 - 2023-07-03

### Fixed
- [Bug] Occasionally, while flashed, the instalocker would return to "Locking", this has been fixed by requiring multiple consecutive frames to match before returning to "Locking".

## Version 1.4.1 - 2023-06-29

### Added
- [Feature] Tools tab added, with features that are not related to locking agents but more improving the Valorant experience.
- [Feature] Tools run independently of the locking thread, so you can use tools without locking agents. To enable them, go to the tools tab and ensure the button at the top of the screen says "Tools Enabled".
- [Feature] New tool, auto drop spike, automatically detects when you are the spike carrier and drops the spike. This is useful if you don't want to be the spike carrier, but don't want to drop the spike manually, or if players keep dropping you the spike. If you pick up the spike on site, or if you are planting, the spike will not be dropped. I plan to update it in the future so that it automatically disables when you are the last player alive.

## Version 1.4.0 - 2023-06-28

### Added
- [Feature] Support for new agent "Deadlock".
- [Feature] New option in user_settings, "FAST_MODE_TIMINGS", the set delay between each action when safe mode is disabled. Default is set to 0.2, 0.2, 0.2. This can be changed if your computer is slower and is struggling to keep up with the default timings. Setting the numbers too low or to zero may cause issues while locking, such as button presses not being registered by Valorant.

### Fixed
- [Bug] Fixed bug where icons would not update after locking or detecting the end of a game.
- [Bug] Fixed various minor bugs.

## Version 1.3.2 - 2023-06-25

### Added
- [Feature] New custom icons, the old icons were a rip off of the Valorant icons. The new icons are custom made to show "VL", which is short for VALocker. When disabled, the icons will be greyed out. When enabled, the icon will be colored. While VALocker is set to "Locking", the icon features a lock. While VALocker is set to "In Game", the icon features an hourglass. The icons are displayed in the taskbar, and in the system tray. The icons are also displayed in the GUI, in the top left corner of the window.
- [Feature] New config option "HIDE_DEFAULT_SAVE_FILE" allows the user to hide the default save file from the save file tab. This is useful if you have a lot of save files or don't like how the default file is displayed right after the favorited files. This is set to true by default, and can be changed in the user settings file.

### Removed
- Old icons, which were somewhat confusing when Valorant was running.

## Version 1.3.0 - 2023-06-24

### Added
- [UI] Navigation bar on the left side of the GUI. This will allow for easier navigation between tabs.

### Changed
- [UI] The Exit button has been moved to the bottom of the navigation bar, so that the GUI can be closed from any tab.
- [UI] The UI is a lot more consistent. All tabs have the same padding and checkboxes are properly aligned.
- [UI] Theme changed from "blue" to "dark-blue". This is a lot easier on the eyes, and looks a lot better.
- [UI] Font changed from "Arial" to "Roboto". 

### Fixed
- [UI] Fixed bug where the role checkboxes in the random agent tab would not deselect when a new agent was unlocked in the agent toggle tab.
- [UI] Fixed bug where map dropdown would expand when an agent with a long name was selected. (i.e. Brimstone)


## Version 1.2.5 - 2023-06-24

### Added
- [Feature] Added automatic releases and automatic compilation to exe. Releases can be found [here](https://github.com/E1Bos/VALocker/releases).


## Version 1.2.2 - 2023-06-22

### Added
- [Feature] Error dialogue boxes now show "Ok" and "Cancel". Ok will reopen the input box, and cancel will close the input box, allowing the user to try again if they wish.
- [Feature] 'Esc' key can now be used to close the input box or error box. 'Return' will prompt the user to try again.

### Updated
- [Feature] Updated renaming and creating save files. If input is valid, previous input will be displayed in the input box. Also added error for unsupported characters. i.e. \ / : * ? " < > |


## Version 1.2.1 | 2023-06-22

### Added
- [Feature] Added "PERSISTENT_RANDOM_AGENTS" to user settings. When enabled, adjusting your random agents while exclusiselect is enabled will revert to the selected agents prior to enabling exclusiselect. When disabled, adjusting your random agents while exclusiselect is enabled will update the random agent list and will keep any changes made by exclusiselect.

### Fixed
- [Bug] Fixed bug where exclusiselect would not update the GUI when selecting an agent.
- [Bug] Fixed bug where exclusiselect would not deselect randomly selected agent checkbox.


## Version 1.1.1 | 2023-06-19

### Fixed
- [Bug] Fixed bug where the "All" checkbox would not update if random agents are selected by role.
- [Bug] Fixed bug where the "None" checkbox would not update if random agents are selected by role.


## Version 1.1.0 | 2023-06-19

### Changes
- [Update] Updating the GUI uses match-case statements. GUI updates are much faster.
- [Update] The label for the current save file is now a button and when clicked, it will open the save file tab.


## Version 1.0.2 | 2023-06-17

### Fixed
- [Bug] Fixed bug where when instalocker is waiting for the end of a game, and the instalocker is stopped, it will stop searching for the end of the game when re enabled.


## Version 1.0.1 | 2023-06-15

### Changes
- [Update] Text of new save button has been replaced with an icon.


## Version 1.0.0 | 2023-06-15

### Added
- [Feature] New save file tab. All save files are displayed in a scrollable window.
- [Feature] To be able to quickly find the current save file, it is highlighted in green.
- [Feature] Ability to favorite save files, which will be displayed at the top of the save file tab, and cannot be deleted. They can be unfavorited, which will remove them from the top of the list, but they will still be displayed in the list of save files. They are stored in "user_settings.json" under "FAVORITED_SAVE_FILES".
- [Feature] Ability to rename save files with the use of a popup window.
- [Feature] Ability to delete save files, requiring confirmation from a popup window. Favorited save files, the selected save file, and the default file cannot be deleted.
- [Feature] Ability to create new save files.
- [Feature] Added changelog.

### Changed
- [Update] Current save file label is displayed where the old selection combobox was.

### Removed
- [Feature] Old method of creating new save files and selecting save files.
- [Feature] Old save file combobox on overview tab, replaced with separate save file selection.
