import React, { useState, useEffect, useRef } from 'react';
import alanBtn from '@alan-ai/alan-sdk-web';
import $ from "jquery";

const alanKey = '08dd587b9900d0225d9ec940df3f5af82e956eca572e1d8b807a3e2338fdd0dc/stage';


const App = () => {

  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    alanBtn({
        key: alanKey,
        onCommand: ({command, song_info, search_str, ans}) => {
            if (command === 'listSearch'){
              playSong(song_info);
            }
            else if (command === 'makePlaylist'){
              makePlaylist(search_str);
            }
            else if (command === 'postPlaylist') {
              postPlaylist(ans);
          }
        },
    })
}, [])

function playSong(song_info) {
  console.log(song_info);
  window.open(song_info.external_urls.spotify);
}

function makePlaylist(search_str) {
  console.log(search_str);
  fetch('/playlist', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'Application/JSON',
    },
    body: JSON.stringify({search_str}),
  }).then(function(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response.text();
}).then(function(response) {
    console.log(response);
    alanBtn().callProjectApi("setClientData1", { value: response }, function (error, result) {
      if (error) {
          console.error(error);
          return;
      }
      console.log(result)
      alanBtn().activate();
    });
  });
}

function postPlaylist(ans) {
  console.log(ans);
  fetch('/postPlaylist', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'Application/JSON',
    },
    body: JSON.stringify({ans}),
  }).then(function(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response.text();
}).then(function(response) {
    alanBtn().deactivate();
    console.log(response);
}).catch(function(error) {
    console.log(error);
});
}

  return (
    <div>
    </div>

  );
}

export default App;
