Changelog
=========

## v1.2.3 | 2023-10-2

### Added
- [Release] Added automatic releases and automatic compilation to exe. Releases can be found [here](https://github.com/E1Bos/VALocker/releases)

## v1.2.2 | 2023-10-2

### Added
- [Feature] Error dialogue boxes now show "Ok" and "Cancel". Ok will reopen the input box, and cancel will close the input box, allowing the user to try again if they wish.
- [Feature] 'Esc' key can now be used to close the input box or error box. 'Return' will prompt the user to try again.

### Updated
- [Feature] Updated renaming and creating save files. If input is valid, previous input will be displayed in the input box. Also added error for unsupported characters. i.e. \ / : * ? " < > |

## v1.2.1 | 2023-06-22

### Added
- [Feature] Added "PERSISTENT_RANDOM_AGENTS" to user settings. When enabled, adjusting your random agents while exclusiselect is enabled will revert to the selected agents prior to enabling exclusiselect. When disabled, adjusting your random agents while exclusiselect is enabled will update the random agent list and will keep any changes made by exclusiselect.

### Fixed
- [Bug] Fixed bug where exclusiselect would not update the GUI when selecting an agent.
- [Bug] Fixed bug where exclusiselect would not deselect randomly selected agent checkbox.

## v1.1.1 | 2023-06-19

### Fixed
- [Bug] Fixed bug where the "All" checkbox would not update if random agents are selected by role.
- [Bug] Fixed bug where the "None" checkbox would not update if random agents are selected by role.


## v1.1.0 | 2023-06-19

### Changes
- [Update] Updating the GUI uses match-case statements. GUI updates are much faster.
- [Update] The label for the current save file is now a button and when clicked, it will open the save file tab.

## v1.0.2 | 2023-06-17

### Fixed
- [Bug] Fixed bug where when instalocker is waiting for the end of a game, and the instalocker is stopped, it will stop searching for the end of the game when re enabled.

## v1.0.1 | 2023-06-15

### Changes
- [Update] Text of new save button has been replaced with an icon.

## v1.0.0 | 2023-06-15

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

<!-- ### Fixed
- [Bug] 
- [Bug]  -->

### Removed
- [Feature] Old method of creating new save files and selecting save files.
- [Feature] Old save file combobox on overview tab, replaced with separate save file selection.