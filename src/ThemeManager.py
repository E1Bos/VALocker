import json
import colorsys

from ProjectUtils import FOLDER, GET_WORKING_DIR


class ThemeManager:
    """
    Manages the theme for the application and provides methods to set and retrieve the theme.
    """

    def __init__(self) -> None:
        self.theme = None
        self.working_dir = GET_WORKING_DIR()

        with open(f"src/{FOLDER.UI_FOLDER.value}/style.qss", "r") as style_file:
            self.style_sheet = style_file.read()

    def setTheme(self, theme_name: str) -> None:
        """
        Sets the theme for the application, and brightens the colors for hover effects.

        Args:
            theme_name (str): The name of the theme to set.
        """
        with open(
            f"{self.working_dir}/{FOLDER.THEMES.value}/{theme_name}-theme.json", "r"
        ) as theme_file:
            self.theme = json.load(theme_file)

        for element_to_brighten in [
            "@accent",
            "@button-enabled",
            "@button-disabled",
            "@foreground-highlight",
        ]:
            self.theme[f"@{element_to_brighten}-hover"] = self.brightenColor(
                self.theme[element_to_brighten], 1.1
            )

        for key, value in self.theme.items():
            self.style_sheet = self.style_sheet.replace(f"{key};", f"{value};")

    def brightenColor(self, hex_color: str, amount: int):
        """
        Brightens a given hex color by increasing its lightness.

        Args:
            hex_color (str): The hex color code to be brightened.
            amount (int): The amount by which to increase the lightness of the color.

        Returns:
            str: The brightened hex color code.

        """
        hex_color = hex_color.lstrip("#")

        rgb_color = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        h, l, s = colorsys.rgb_to_hls(
            rgb_color[0] / 255.0, rgb_color[1] / 255.0, rgb_color[2] / 255.0
        )

        # Increase the lightness
        l = max(min(l * amount, 1), 0)

        r, g, b = colorsys.hls_to_rgb(h, l, s)

        # Convert RGB back to hex
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    def getTheme(self):
        """
        Retrieves the current theme's style sheet.

        Returns:
            str: The style sheet of the current theme.
        """
        if self.theme:
            return self.style_sheet


if __name__ == "__main__":
    theme_manager = ThemeManager()
    theme_manager.setTheme("default")
