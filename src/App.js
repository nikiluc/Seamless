import React, { useState, useEffect, useRef} from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import alanBtn from '@alan-ai/alan-sdk-web';
import background from "./images/download.png";
import musicGif from "./images/jakeMusic.gif"
import './App.css';
import $ from 'jquery';
import { Container, ListGroup } from 'react-bootstrap';
import Row from 'react-bootstrap/Row';
import Image from 'react-bootstrap/Image';
import Modal from 'react-bootstrap/Modal';
import Popover from 'react-bootstrap/Popover';
import Overlay from 'react-bootstrap/Overlay';
import dotenv from 'dotenv';
import axios from 'axios';



dotenv.config({path:".env"});

const client_id=process.env.REACT_APP_client_id;
const client_secret=process.env.REACT_APP_client_secret;
let access_token;

const alanKey = process.env.REACT_APP_alanKey;

var alan;

const App = () => {

  const [inputText, setInputText] = useState("");
  const [validated, setValidated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [posted, setPosted] = useState(false);
  const [alert, showAlert] = useState(false);
  const [found, setFound] = useState(false);
  const ref = useRef(null);

  $(function() {

    window.$("#js-rotating").Morphext({
      // The [in] animation type. Refer to Animate.css for a list of available animations.
      animation: "animate__animated animate__fadeInUp",
      // An array of phrases to rotate are created based on this separator. Change it if you wish to separate the phrases differently (e.g. So Simple | Very Doge | Much Wow | Such Cool).
      separator: ",",
      // The delay between the changing of each phrase in milliseconds.
      speed: 2500,
      complete: function () {
          // Called after the entrance animation is executed.
      }
  });

    axios('https://accounts.spotify.com/api/token', {
      headers: {
         'Content-Type' : 'application/x-www-form-urlencoded',
         'Authorization' : 'Basic ' + Buffer.from(client_id + ':' + client_secret).toString('base64')     
       },
      data: 'grant_type=client_credentials',
      method: 'POST'
     })
     .then(tokenResponse => {      
        access_token = tokenResponse.data.access_token;
      });

    window.$('#autocomplete').autocomplete({
      source: function(request, response) {

      let query = request.term.toLowerCase().split(" ").join('+');

          axios(`https://api.spotify.com/v1/search?q=${query}&type=track&market=US`, {
            method: 'GET',
            headers: { 'Authorization' : 'Bearer ' + access_token},
            
          })
          .then(trackResponse => {
              //const song_info = trackResponse.data.tracks.items[0]
              response($.map(trackResponse.data.tracks.items.slice(0, 5), function(item) {
                return {
                    label: item.name + " by " + item.artists[0].name,
                    value: item.name + " " + item.artists[0].name, //change to id
                    id: item.id
                }

            }))
        }).catch(error => {
            console.log(error.response)
      });
  

  },
  minLength: 1,
  select: function(event, ui) {
      window.$("#autocomplete").val(ui.item.value);
      window.location.href = "#" + ui.item.value;
      console.log(ui.item.value);
      setInputText(ui.item.value);
      
  },
});

});

      //Sets input Text
  const inputTextHandler = (e) =>{
    setInputText(e.target.value);
    setFound(false);
    //console.log(e.target.value);
  };

    //Final Typed Query from user
  const submitHandler = (e) =>{
    if (e.target.checkValidity() === false) {

    }
    else {

      console.log('QUERY', inputText);

      let query = inputText.toLowerCase().split(" ").join('+');

      axios(`https://api.spotify.com/v1/search?q=${query}&type=track&market=US`, {
        method: 'GET',
        headers: { 'Authorization' : 'Bearer ' + access_token},
        
      })
      .then(trackResponse => {
        if (trackResponse.data.tracks.items.length >= 1) {
          e.preventDefault();
          console.log(inputText);
          loadingAnimation();
          makePlaylist(inputText);
          setLoading(false);
        }
        else {

          e.preventDefault();
          setFound(true);
          setValidated(false);

        }

    }).catch(error => {
        console.log(error.response)
  });
 
    }
    e.preventDefault();
    setValidated(true);
  };

  function loadingAnimation() {

    $('.title').addClass('animate__animated animate__fadeOut');
    $('.form-rounded').addClass('animate__animated animate__fadeOutUp');
    $('.submitBtn').addClass('animate__animated animate__fadeOutDown');
    setTimeout(function(){ setLoading(true); }, 2000);
    $('.music').addClass('animate__animated animate__fadeIn');
    $('.spinner').addClass('animate__animated animate__fadeIn');


  }

  function loadResults(songArray){

    $('.music').removeClass('animate__animated animate__fadeIn');
    $('.spinner').removeClass('animate__animated animate__fadeIn');
    $('.music').addClass('animate__animated animate__fadeOut');
    $('.spinner').addClass('animate__animated animate__fadeOut');
  
    $('.spotifyButton').addClass("animate__animated animate__fadeInDown").attr("hidden", false);
  
    var songList = $('ul.songList').addClass("animate__animated animate__fadeIn").attr("hidden", false);
    songArray.forEach(element => {
  
      var li = $('<ListGroupItem as="li" bsClass="customList"/>')
          .addClass("animate__animated animate__fadeInUp")
          .appendTo(songList);
       $('<a href=' + element['externalURL'] + ' target="_blank" rel="noopener noreferrer"' +'/>')
          .addClass('list-group-item')
          .text(element['title'] + ' by ' + element['artist'])
          .appendTo(li);
      
    });
    setLoading(false);
    $('.animate__animated animate__fadeInDown').remove()
    $('.searchbar').remove()
    $('.submitBtn').remove()
    $('.title').removeClass("animate__animated animate__fadeOut")
    $('.title').css("margin-top", '80px')
    $('.title').addClass("animate__animated animate__fadeInDown")

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
}, )

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
      //throw Error(response.statusText);
      showAlert(true);
      setTimeout(function(){ refreshPage(); }, 4000);
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

  loadResults(songArray);

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
  setPosted(true);
  alan.playText("Done.");

}


  return (
      <div style={{height: '100%', backgroundImage:`linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.3)), url(${background})`, backgroundSize: 'cover', backgroundPosition: 'center', backgroundRepeat: 'no-repeat'}}>
        <div className="main-div">
          <div className="animate__animated animate__fadeIn">
            <h1 className="title" id="titleLink" >Seamless</h1>
          </div>
        <div className="animate__animated animate__fadeInDown">
        <div ref={ref}>
          <Form id="searchForm" ref={ref} noValidate validated={validated} onSubmit={submitHandler}>
            <Form.Group className="searchbar">
              <Form.Control className="form-rounded" id="autocomplete" value={inputText} size="lg" type="text" placeholder="Enter an artist and song :)" onChange={inputTextHandler} required={true}/>
              <Form.Control.Feedback type="invalid">
                Please enter a song and artist.
              </Form.Control.Feedback>
            </Form.Group>
          </Form>
          </div>
        </div>
        <div className="animate__animated animate__fadeInUp">
          <Button form="searchForm" className="submitBtn" size="lg" variant="success" type="submit">Submit</Button>{''}
          <Overlay show={found} target={ref.current} placement="right">
              <Popover id="popover-basic">
              <Popover.Content>
                <strong>Uh oh</strong> we couldn't find your song. Please try a different song!
              </Popover.Content>
            </Popover>
          </Overlay>
        </div>
        <div className="addToSpotify">
          <Container>
            <Row className="justify-content-center" md="auto" >
              <Button className="spotifyButton" hidden={true} size="lg" variant="success" type="button" disabled={posted} onClick={() => { setPosted(true); postPlaylist('True'); }}>{posted ? 'Done!':'Add to Spotify' }</Button>{''}
              <Button className="spotifyButton" hidden={true} size="lg" variant="success" type="button" onClick={refreshPage}>Create Another</Button>{''}
            </Row>
           </Container>
        </div>
        <div className="errorModal">
          <Modal size="lg" show={alert} >
            <Modal.Header closeButton>
              <Modal.Title>Error</Modal.Title>
            </Modal.Header>
            <Modal.Body>Oops! Something went wrong. Refreshing the page in a few seconds...</Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={ () => {showAlert(false);}}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
        </div>
        <div>
          <Image className="music" src={musicGif} roundedCircle={true} hidden={!loading}></Image>
        </div>
        <span hidden={!loading} id="js-rotating">Studying similar artists..., You have an awesome taste in music!,
         Finding great songs..., Putting you on to new sounds..., Thanks for using Seamless :), Elvis?? That's not right...,
         Back on track!...sorta?, Brining you quality music...</span>
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
        </div>
        <footer className="footer">
          <div className="tech">
            <p></p>
          </div>
        </footer>
      </div>

  );
}

export default App;
