import unittest

from VALocker import VALocker
from FileManager import FileManager
from Updater import Updater
from Constants import FOLDER, FILE, LOCKING_CONFIG



class TestFileCompatibility(unittest.TestCase):
    
    latest_version = VALocker.VERSION
    files_to_test = [
        FILE.AGENT_CONFIG,
        FILE.SETTINGS,
        LOCKING_CONFIG.CONFIG_1920_1080_16_9,
        LOCKING_CONFIG.CONFIG_1650_1080_16_10,
        LOCKING_CONFIG.CONFIG_1280_1024_5_4,
    ]

    def test_file_compatibility(self):
        
        
        file_manager = FileManager()
        file_manager.setup()
        
        updater = Updater(VALocker.VERSION, file_manager)
        
        for file in self.files_to_test:
            self.assertTrue(
                updater.meets_required_version(file),
            )

if __name__ == "__main__":
    unittest.main()