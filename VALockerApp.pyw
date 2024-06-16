"""
Main entry point for the VALocker application.
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

from VALocker import VALocker

if __name__ == "__main__":
    locker = VALocker()
    locker.mainloop()
