Changelog
=========

## [1.1.1] 2023-06-19

### Fixed
- [Bug] Fixed bug where the "All" checkbox would not update if random agents are selected by role.
- [Bug] Fixed bug where the "None" checkbox would not update if random agents are selected by role.


## [1.1.0] 2023-06-19

### Changes
- [Update] Updating the GUI uses match-case statements. GUI updates are much faster.
- [Update] The label for the current save file is now a button and when clicked, it will open the save file tab.

## [1.0.2] 2023-06-17

### Fixed
- [Bug] Fixed bug where when instalocker is waiting for the end of a game, and the instalocker is stopped, it will stop searching for the end of the game when re enabled.

## [1.0.1] 2023-06-15

### Changes
- [Update] Text of new save button has been replaced with an icon.

## [1.0.0] 2023-06-15

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