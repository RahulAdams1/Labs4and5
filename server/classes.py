from enum import Enum
import hashlib
import os


class Mine:
    def __init__(self, x: int, y: int, msn: str | None = None) -> None:
        self.x = x
        self.y = y
        self.msn = msn if (msn is not None) else f"MSN{x}{y}"

    def __setitem__(self, key, value):
        return setattr(self, key, value)
    
class Rover:
    Status = Enum('Status', ['Not_Started', 'Finished', 'Moving', 'Eliminated'])

    def __init__(self, id: int, move_cmds: str, path):
        self.id = id
        self.x = 0
        self.y = 0
        self.direction = 2 #direction: 0,1,2,3 = N,E,S,W
        self.move_cmds = move_cmds
        self.path = path
        self.status = self.Status.Moving

    def __str__(self):
        return f"Rover {self.id} | Pos: ({self.x}, {self.y}) | Status: {self.status}"
    
    def move(self, moveCmds: str, mapDimensions: list[int], minesDict: dict, animate: bool=False) -> None:
        for moveCmd in moveCmds:
            # Get the dict key by concatenating x and y with a space in between
            minesDictKey = ' '.join([str(self.x), str(self.y)])
            mineSerialNum = minesDict[minesDictKey] 
            print(mineSerialNum)
            match moveCmd:
                case 'L':
                    self.direction -= 1 if self.direction > 0 else -3 # loop back to 3 if turning left at 0
                case 'R':
                    self.direction += 1 if self.direction < 3 else -3 # loop back to 0 if turning right at 3
                case 'M':
                    if mineSerialNum:  # If rover wants to move, but is currently on a mine
                        demine_req = {
                            'msn': mineSerialNum,
                            'coords': [self.x, self.y],
                            'rover_id': self.id
                        }


                    match self.direction:
                        case 0:
                            if self.y > 0:
                                self.y -= 1
                        case 1:
                            if self.x < mapDimensions[1]-1:
                                self.x += 1
                        case 2:
                            if self.y < mapDimensions[0]-1:
                                self.y += 1
                        case 3:
                            if self.x > 0:
                                self.x -= 1                         
                case 'D':
                    if mineSerialNum:
                        h = hashlib.sha256()
                        validPin = False
                        i = 0

                        while(~validPin):
                            tempKey = str(mineSerialNum)+str(i)
                            h.update(bytes(tempKey, 'utf-8'))
                            hashResult = h.hexdigest()
                            #print(f"testing tempKey = {tempKey}, hashResult = {hashResult}")

                            if hashResult[:4] == '0000':
                                validPin = True
                                break
                            i += 1
                case _: 
                    print('ERROR in Rover.move(): unknown move command')

            # Assign correct symbol to path indication rover position and direction
            dirSymbol = ' '
            match self.direction:
                case 0:
                    dirSymbol = '^'
                case 1:
                    dirSymbol = '>'
                case 2:
                    dirSymbol = 'v'
                case 3:
                    dirSymbol = '<'    
            self.path[self.y][self.x] = dirSymbol
            
            # animate the path of rover
            if animate:
                print(f"Rover {self.id} movement:")
                for list in self.path:
                    print(list)
                print(f"\nLast instr: {moveCmd} | Rover direction: {self.direction}")
                print(moveCmds)
                global moveCmdsIndexStr
                print(moveCmdsIndexStr)
                #time.sleep(1)
                os.system('cls')
                moveCmdsIndexStr = "".join([moveCmdsIndexStr, '^'])

if __name__ == "__main__":
    rover1 = Rover(1, None)
    print(rover1)