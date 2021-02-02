import React, { useState, useEffect} from 'react';
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
import Alert from 'react-bootstrap/Alert';
import Modal from 'react-bootstrap/Modal'


const alanKey = '08dd587b9900d0225d9ec940df3f5af82e956eca572e1d8b807a3e2338fdd0dc/stage';

var alan;

const App = () => {

  const [submit, setSubmit] = useState("");
  const [inputText, setInputText] = useState("");
  const [validated, setValidated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [posted, setPosted] = useState(false);
  const [alert, showAlert] = useState(false);

  //Trying to set up autocomplete....will finish tomorrow
  $(function() {

    window.$('#autocomplete').autocomplete({
      source: function(request, response) {
      window.$.ajax({
          type: "GET",
          url: "https://api.spotify.com/v1/search",
          dataType: "json",
          data: {
              type: "artist",
              limit: 3,
              contentType: "application/json; charset=utf-8",
              format: "json",
              q: request.term
          },
          success: function(data) {
              response($.map(data.artists.items, function(item) {
                  return {
                      label: item.name,
                      value: item.name,
                      id: item.id
                  }
              }));
          }
      });
  },
  minLength: 3,
  select: function(event, ui) {
      $("#autocomplete").val(ui.item.value);
      window.location.href = "#" + ui.item.value;
  },
});

});


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
      var aaa = $('<a href=' + element['externalURL'] + ' target="_blank" rel="noopener noreferrer"' +'/>')
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
          <Form id="searchForm" noValidate validated={validated} onSubmit={submitHandler}>
            <Form.Group className="searchbar">
              <Form.Control className="form-rounded" id="autocomplete" value={inputText} size="lg" type="text" placeholder="Enter an artist and song :)" onChange={inputTextHandler} required={true}/>
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
