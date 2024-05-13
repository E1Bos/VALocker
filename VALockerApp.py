import sys
sys.path.append("src")

from VALocker import VALocker

if __name__ == "__main__":
    locker = VALocker()
    locker.mainloop()
