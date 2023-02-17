# Valocker

## Running the Program
Run 'valocker.pyw' to start the program. The program will start as a window, and when closed it will minimize into an icon and run into the background. To fully close the program, right click on the icon and click on the "Exit" option or select the "Exit" option from the GUI.

---

## Enabling/Disabling Instalocking

In order to enable or disable the instalocking feature, click the button under the label "Instalocker" in the "Overview" tab. The button will toggle between disaled and enabled. You can see which mode the program is on, "Locking" or "Waiting" by checking the button below that titled "Current Task". When in the Valorant loading screen, ensure the program is in "Locking". The "Waiting" mode will attempt to find the main menu at a slower rate, ensuring better gameplay during your Valorant game.

---

## Enabling/Disabling Agents

In order to select a certain agent, open the "Toggle Agents' tab. Here you can toggle which agents you do and don't have unlocked. This step is necessary to ensure the correct calculations are done and the right agent is instalocked.

---

## Selecting Agents

On the "Overview" tab, select the dropdown under "Default Agent" to pick which agent the program will instalock. The instalocker will only show agents you have unlocked so it is vital that you select the correct agents. This will select the same agent no matter what map or gamemode.


### Map Specific Agents

To enable map specific agent selection, select the button under "Map Specific", then toggle which agent should be selected for each map in the "Map Specific" tab.

---

## Safe Mode

To enable "Safe Mode" toggle it with the dedicated button in the "Overview" tab. When enabled, you can switch between the modes "Low", "Medium", and "High". It will randomize the segment of the agent box and lock button to click and will add a delay depending on the mode selected. "Low" will lock an agent in 0.3s to 0.5s. "Med" or "Medium" will lock an agent in 0.5s to 0.8s. "High" will lock an agent in 0.8s to 1.1s. Note that with "Safe Mode" enabled, someone else may lock an agent faster than you.

---

# Instalocker Graphic Settings

## General Graphic Settings

- Display Mode: Fullscreen or Windowed Fullscreen
- Resolution: 1920x1080
- Aspect Ratio: Letterbox

The resolution must be set to 1920x1080 for the program to work. The quality settings do not matter. I also recommend you disable improve quality and experimental sharpening. 

---

## Before First Use

Since the program clicks pixels on your screen,  you need to ensure you have the correct scale set inside instalocker.py. Having the wrong scale will cause the program to click the wrong pixels.

> Find your display scale by **right clicking your desktop**
> and selecting **Display Settings**. Find **Scale** (under
> Scale & Layout on Windows 11), and change the value
> **DISPLAY_SCALE** in *config.json*.
>
> i.e.
> - 100% = 1
> - 75% = 0.75
> - 125% = 1.25

---

# Important Notes

The program will not function well if you have a slow internet connection or computer. It can only instalock as fast as you load into the agent select screen and will only run as fast as your computer lets it. Having too many programs running in the background may slow down it down.

> Moving the mouse while in the agent select screen will cause the program to not work properly. Make sure you do not move your mouse while first loading into the agent select screen.

---

# Future Features

- Support for other resolutions and aspect ratios

---

# Known Issues

- The program will not work if you have a different screen resolution or aspect ratio. Support for other resolutions and aspect ratios may be added in the future.