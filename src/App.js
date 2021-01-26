import React, { useState, useEffect} from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import alanBtn from '@alan-ai/alan-sdk-web';
import background from "./images/download.png";
import './App.css';
import $ from 'jquery';
import { ListGroup } from 'react-bootstrap';


const alanKey = '08dd587b9900d0225d9ec940df3f5af82e956eca572e1d8b807a3e2338fdd0dc/stage';

var alan;

const App = () => {

  const [submit, setSubmit] = useState("");
  const [inputText, setInputText] = useState("");
  const [validated, setValidated] = useState(false);
  const [loading, setLoading] = useState(false);


      //Sets input Text
    const inputTextHandler = (e) =>{
      setInputText(e.target.value);
    };

      //Final Typed Query from user
    const submitHandler = (e) =>{
      if (e.target.checkValidity() === false) {

        e.preventDefault();

      }
      else {
        e.preventDefault();
        setSubmit(inputText);
        console.log(inputText);
        loadingAnimation();
        makePlaylist(inputText);
        setLoading(false);


      }

      setValidated(true);

    };

    //Need to make one function (instead of duplicate code)
    function loadingAnimation() {

      $('.title').addClass('animate__animated animate__fadeOut');
      $('.form-rounded').addClass('animate__animated animate__fadeOutUp');
      $('.submitBtn').addClass('animate__animated animate__fadeOutDown');
      setTimeout(function(){ setLoading(true); }, 1000);
      $('.spinner').addClass('animate__animated animate__fadeIn');


    }

    function refreshPage(){ 
      window.location.reload(); 
  }


  useEffect(() => {
    alan = alanBtn({
        key: alanKey,
        onCommand: ({command, song_info, search_str, ans}) => {
            if (command === 'listSearch'){
              playSong(song_info);
            }
            else if (command === 'makePlaylist'){
              loadingAnimation();
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
    if (inputText === "") {

    alan.activate();
    alan.callProjectApi("setClientData1", { value: response }, function (error, result) {
      if (error) {
          console.error(error);
          return;
      }
      console.log(result);
    });

  }
  var songArray = JSON.parse(response);
  console.log(songArray);
  setLoading(false);
  $('.spotifyButton').addClass("animate__animated animate__fadeInDown").attr("hidden", false);
  var songList = $('ul.songList').attr("hidden", false);
  songArray.forEach(element => {

    var li = $('<ListGroupItem as="li" bsClass="customList"/>')
        .addClass("animate__animated animate__fadeInUp")
        .appendTo(songList);
    var aaa = $('<a href=' + element['externalURL'] + ' target="_blank" rel="noopener noreferrer"' +'/>')
        .addClass('list-group-item')
        .text(element['title'] + ' by ' + element['artist'])
        .appendTo(li);
    
  });

  $('.animate__animated animate__fadeInDown').remove()
  $('.searchbar').remove()
  $('.submitBtn').remove()
  $('.title').removeClass("animate__animated animate__fadeOut")
  $('.title').css("margin-top", '40px')
  $('.title').addClass("animate__animated animate__fadeInDown")


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
          <div className="animate__animated animate__fadeIn">
            <h1 className="title">Seamless</h1>
          </div>
        <div className="animate__animated animate__fadeInDown">
          <Form id="searchForm" noValidate validated={validated} onSubmit={submitHandler}>
            <Form.Group className="searchbar">
              <Form.Control className="form-rounded" value={inputText} size="lg" type="text" placeholder="Enter an artist and song :)" onChange={inputTextHandler} required={true}/>
              <Form.Control.Feedback type="invalid">
                Please enter a song and artist.
              </Form.Control.Feedback>
            </Form.Group>
          </Form>
        </div>
        <div className="animate__animated animate__fadeInUp">
          <Button form="searchForm" className="submitBtn" size="lg" variant="success" type="submit">Submit</Button>{''}
        </div>
        <div className="addToSpotify">
          <Button className="spotifyButton" hidden={true} size="lg" variant="success" type="button" onClick={() => postPlaylist('True')}>Add to Spotify</Button>{''}
          <Button className="spotifyButton" hidden={true} size="lg" variant="success" type="button" onClick={refreshPage}>Create Another</Button>{''}
        </div>
        <div className="spinner" hidden={!loading}>
          <div className="rect1"></div>
          <div className="rect2"></div>
          <div className="rect3"></div>
          <div className="rect4"></div>
          <div className="rect5"></div>
        </div>
        <div className="animate-flicker" hidden={!loading}></div>
        <div>
          <ListGroup as="ul" className="songList" hidden={true}>
          </ListGroup>
        </div>
        </header>
        <footer className="footer">
          <div className="tech">
            <p></p>
          </div>
        </footer>
      </div>

  );
}

export default App;
