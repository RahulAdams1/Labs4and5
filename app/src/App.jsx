import { useState, useEffect, useRef } from 'react'
import { useSnackbar } from 'notistack'
import useWebSocket, { ReadyState } from 'react-use-websocket'
import axios from 'axios';

import roverLogo from './assets/rover-64px.png'
import Canvas from './components/Canvas'
import Rover from './components/rover'
import Mine from './components/mine';

function App() {


  const [roverMap, setRoverMap] = useState();
  const [minesArr, setMinesArr] = useState();
  const mapRef = useRef();
  const minesRef = useRef();
  mapRef.current = roverMap;
  minesRef.current = minesArr;

  const [rover1, setRover1] = useState({ rover: new Rover(1, 0, 0) });

  const { enqueueSnackbar, closeSnackbar } = useSnackbar();

  const { sendJsonMessage, sendMessage, lastMessage, readyState, getWebSocket} = useWebSocket(
    "ws://localhost:8000/ws",
    {onMessage: (e) => {
      const dataObj = JSON.parse(e.data);
      console.log(dataObj)

      // Handle successful demine
      if(dataObj.res == 'demineSuccess') {
        const mineObj = dataObj.detail;
        enqueueSnackbar(`Successfully demined mine with id ${mineObj.id} at (${mineObj.x},${mineObj.y})`, {variant: 'success'});

        const newMinesArr = minesRef.current.filter((mine) => {
          return mine.id != mineObj.id;
        })
        
        setMinesArr(newMinesArr);
      }
    }}  
  );

  function handleKeyDown(e) {
    //console.log(e)
    //sendMessage(e.key);
    
    const updatedRover = rover1.rover;

    if(rover1.rover.status != 4) {
      switch (e.key) {
        case 'w':
          // Check if rover is trying to move from mine
          let roverDied = false;
          //console.log(minesRef.current)
          for (const mine of Object.entries(minesRef.current)) {
            const mineObj = mine[1];
            if (updatedRover.x == mineObj.x && updatedRover.y == mineObj.y){
              enqueueSnackbar('Rover moved before sucessful demine *explosion*', { variant: 'error' });
              updatedRover.status = 4;
              roverDied = true;
              
              // Update minesArr
              const newMinesArr = [...minesRef.current];
              newMinesArr.forEach((m) => {
                if(m.id === mineObj.id){
                  m.isActive = false;
                }
              })
              setMinesArr(newMinesArr);

              break;
            }
          }
          if(roverDied) {
            break;
          }
          // Check if rover is trying to move out of bounds of map
          if ((updatedRover.direction == 0 && updatedRover.y > 0) ||
            (updatedRover.direction == 1 && updatedRover.x < mapRef.current[0].length - 1) ||
            (updatedRover.direction == 2 && updatedRover.y < mapRef.current.length - 1) ||
            (updatedRover.direction == 3 && updatedRover.x > 0)
          ) {
            updatedRover.move('M');
          }
          break;
        case 'a':
          updatedRover.move('L');
          break;
        case 'd':
          updatedRover.move('R');
          break;
        case ' ':
          for (const mine of Object.entries(minesRef.current)) {
            const mineObj = mine[1];
            if (updatedRover.x == mineObj.x && updatedRover.y == mineObj.y){
              enqueueSnackbar(`Server demining at (${mineObj.x},${mineObj.y})`, {variant: 'info'})

              
              sendJsonMessage({
                request: 'demine',
                detail: mineObj
              });
              break;
            }
          }
          break;
        default:
          enqueueSnackbar('Space to Demine, WASD to morve', {variant: 'info'})
          break;
      }
    }
    setRover1({ rover: updatedRover })
  }

  useEffect(() => {
    // Get rover map and mines dict from server
    axios.get('http://localhost:8000/map')
    .then( res => {
      setRoverMap(res.data.roverMap);
    })
    .catch( err => {
      console.log(err);
    })

    // Get rover map and mines dict from server
    axios.get('http://localhost:8000/mines')
    .then( res => {
      const tempArr = [];
      for (const mine of Object.entries(res.data.all_mines)) {
        const mineObj = mine[1];
        //console.log(mine)
        tempArr.push(new Mine(mine[0], mineObj.x, mineObj.y, mineObj.msn));
      }
      setMinesArr(tempArr);
    })
    .catch( err => {
      console.log(err);
    })

    document.addEventListener('keydown', handleKeyDown);

    return function cleanup() {
      document.removeEventListener('keydown', handleKeyDown);
    }
  }, []);

  return (
    <>
      
      <h1>COE892 Lab5-6</h1>

      { roverMap && minesArr ? (
        <Canvas map={roverMap} mines={minesArr} rover={rover1.rover} />
      ) : (
        <div>Getting rover map</div>
      )}
      
    </>
  )
}

export default App
