from scripts.home import Home
from scripts.manager import Manager

if __name__ == '__main__':
    rno = Home().run() # gets room number
    if rno:
        Manager(rno) # opens manager
