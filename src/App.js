import React, { useState, useEffect, useRef } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import useForm from 'react-hook-form';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import alanBtn from '@alan-ai/alan-sdk-web';
import background from "./images/download.png";
import './App.css';


const alanKey = '08dd587b9900d0225d9ec940df3f5af82e956eca572e1d8b807a3e2338fdd0dc/stage';

var alan;

const App = () => {

  const [submit, setSubmit] = useState("");
  const [inputText, setInputText] = useState("");


      //Sets input Text
      const inputTextHandler = (e) =>{
        setInputText(e.target.value);
    };

      //Final Query from user
      const submitHandler = (e) =>{
        e.preventDefault();
        setSubmit(inputText);
        console.log(inputText);
        if (inputText != "") {
          makePlaylist(inputText);
        }
        setInputText("");
    };



  useEffect(() => {
    alan = alanBtn({
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
        rootEl: document.getElementById("alan-btn")
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
    if (inputText == "") {

    alan.activate();
    alan.callProjectApi("setClientData1", { value: response }, function (error, result) {
      if (error) {
          console.error(error);
          return;
      }
      console.log(result);
    });

  }
  else {
    postPlaylist("True");
  }
    
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
    console.log(response);
}).catch(function(error) {
    console.log(error);
});
}

  return (
      <div style={{height: '100%', backgroundImage:`linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.3)), url(${background})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundRepeat: 'no-repeat'}}>
        <header className="App-header">
        <Form id="searchForm">
          <Form.Row className="searchbar">
            <Form.Control className="form-rounded" value={inputText} size="lg" type="text" placeholder="Search" onChange={inputTextHandler}/>
          </Form.Row>
        </Form>
        <Button form="searchForm" className="submitBtn" size="lg" variant="success" type="submit" onClick={submitHandler}>Submit</Button>
        </header>
      </div>

  );
}

export default App;
