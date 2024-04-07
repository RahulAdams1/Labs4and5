import hashlib
import json
from fastapi import FastAPI, HTTPException, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from classes import Mine, Rover

# Global variables
roverMap = [[0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0],
            [0, 0, 1, 0, 0],];

minesDict = {
    1: Mine(2, 3),     
    2: Mine(1, 2),     
}

mine_id_count = 2
rover_id_count = 1

roversList = [Rover(id=1, move_cmds="LRMM", path=None)]


# Initialize FastAPI app
app = FastAPI()

# CORS policy: allow all
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI server for COE892 Labs 4 and 5: Rover Control"}

#==================== Map routes ====================#
@app.get("/map")
async def get_map():
    global roverMap
    return {"roverMap": roverMap} 

@app.put("/map", status_code=204, response_class=Response)
async def update_map():
    global roverMap 
    roverMap = [[0, 0, 0], [0, 12, 0],[0, 0, 0]]
    
#==================== Mine routes ====================#
@app.get("/mines")
async def get_mines_all():
    global minesDict
    return {"all_mines": minesDict}

@app.get("/mines/{mine_id}")
async def get_mine_by_id(mine_id: int):
    global minesDict
    if mine_id not in minesDict:
        raise HTTPException(status_code=404, detail="Mine not found")
    return {"retrieved_mine": minesDict[mine_id]}

@app.delete("/mines/{mine_id}")
async def delete_mine_by_id(mine_id: int):
    global minesDict
    if mine_id not in minesDict:
        raise HTTPException(status_code=404, detail="Mine not found")
    
    return {"deleted_mine": minesDict.pop(mine_id)}

@app.post("/mines/")
async def create_mine(x: int, y: int, msn: str):
    global minesDict, mine_id_count

    mine_id_count += 1
    new_mine = {mine_id_count: Mine(x, y, msn)}
    minesDict.update(new_mine)
    return {"created_mine": new_mine}

@app.put("/mines/{mine_id}")
async def update_mine(mine_id: int, x: int | None = None, y: int | None = None, msn: str | None = None):
    global minesDict
    if mine_id not in minesDict:
        raise HTTPException(status_code=404, detail="Mine not found")
    
    attrs_to_update = {key: value for key, value in locals().items() if key != 'mine_id' and value is not None}

    for attr, value in attrs_to_update.items():
        minesDict[mine_id][attr] = value
    
    return {"updated_mine": minesDict[mine_id]}

#==================== Rover routes ====================#
@app.get("/rovers")
async def get_all_rovers():
    global roversList
    return {"all_rovers": roversList}

@app.get("/rovers/{rover_id}")
async def get_rover_by_id(rover_id: int):
    global roversList
    for rover in roversList:
        if rover.id == rover_id:
            return {"retrieved_rover": rover}
        
    raise HTTPException(status_code=404, detail="Rover not found")

@app.post("/rovers")
async def create_rover(move_cmds: str):
    global roversList, rover_id_count
    rover_id_count += rover_id_count
    new_rover = Rover(id=rover_id_count, move_cmds=move_cmds, path=None)
    roversList.append(new_rover)

    return {"created_rover": new_rover}

@app.delete("/rovers/{rover_id}")
async def delete_rover_by_id(rover_id: int):
    global roversList
    for rover in roversList:
        if rover.id == rover_id:
            roversList.remove(rover)
            return {"deleted_rover": rover}
        
    raise HTTPException(status_code=404, detail="Rover not found")

@app.put("/rovers/{rover_id}")
async def send_movecmds_by_id(rover_id: int, move_cmds: str):
    global roversList
    for rover in roversList:
        if rover.id == rover_id:
            if rover.status == rover.Status.Not_Started or rover.status == rover.Status.Finished:
                raise HTTPException(status_code=409, detail=f"Cannot issue move cmds while rover status is {rover.status.name}")
            rover.move_cmds=move_cmds
            return f"Rover with id = {rover.id} was issued move_cmds = {move_cmds}"
        
    raise HTTPException(status_code=404, detail="Rover not found")

@app.post("/rovers/{rover_id}/dispatch")
async def dispatch_rover_by_id(rover_id: int):
    global roversList
    for rover in roversList:
        if rover.id == rover_id:
            return f"Rover with id = {rover.id} was dispatched"
        
    raise HTTPException(status_code=404, detail="Rover not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        res = {}
        data = await websocket.receive_text()
        print(f'Data received from client: {data}')

        dataDict = json.loads(data);

        # Process demine request
        if dataDict['request'] == 'demine':
            print("INFO: received demine request from client, processing it now...")
            mine = dataDict['detail']

            h = hashlib.sha256()
            validPin = False
            i = 0
            mineSerialNum = dataDict['detail']['msn']

            while(~validPin):
                tempKey = str(mineSerialNum)+str(i)
                h.update(bytes(tempKey, 'utf-8'))
                hashResult = h.hexdigest()
                print(f"testing tempKey = {tempKey}, hashResult = {hashResult}")

                if hashResult[:4] == '0000':
                    validPin = True
                    break
                i += 1
            res = {
                "res": "demineSuccess",
                "detail": mine
            }
            
        print(f"INFO: sending res={res} to client")
        await websocket.send_json(res)