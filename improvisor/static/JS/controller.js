var currentResults = document.getElementById("currentRow");
var frequentResults = document.getElementById("frequentRow");
var storageBool = storageAvailable('localStorage');
//annyang.start({
//    autoRestart: true
//});
var socket;
$(document).ready(function () {
  socket = io();
});

// ############### ARTYOM ############################
// const artyom = new Artyom();
// var recognisedTags = []; // will store recognised tags so they can be removed from the next result
// // the list is cleared when there is a gap in speech
// // the tags will be pulled from the server
// var recognisedTagsUsed = [];
// var tagset = fetchTagset();
//
// var settings = {
//   continuous: true, // Don't stop never because i have https connection
//   onResult: function (text) {
//     // converts the result to lower case to match the tags
//     text = text.toLowerCase();
//
//     if(text == ""){
//       recognisedTagsUsed = [];
//     }
//
//     // checking if the list is not empty before iterating through it!
//     if(recognisedTagsUsed.length != 0){
//       recognisedTagsUsed.forEach(function(item){
//         text = text.replace(item, "");
//       });
//     }
//     // prints the result with recognised tags removed
//     console.log("Recognized text: ", text);
//     // goes through the tags and checks if they are in the text
//     tagset.forEach(function(tag){
//       if(text.toLowerCase().includes(tag)){
//         // adds the new recognised tag into the recognisedTag list
//         recognisedTags.push(tag);
//         console.log(recognisedTags);
//         text.replace(tag, "");
//       }
//     });
//
//     // this will also empty what's currently in the recognised tags
//     if(recognisedTags){
//       makeAjaxRequest();
//       recognisedTagsUsed = recognisedTagsUsed.concat(recognisedTags);
//       recognisedTags = [];
//     }
//   },
//
//
//
//
//
//   onStart: function () {
//     console.log("Dictation started by the user");
//   },
//   onEnd: function () {
//     console.log("Dictation stopped by the user");
//   }
// };
//
// var UserDictation = artyom.newDictation(settings);
//
// function startArtyom() {
//   // Make sure artyom is deactvated before dictation..
//   artyom.fatality()
//   // Activate dictation object
//   UserDictation.start();
// };
//
// function stopArtyom() {
//   console.log("Stopped Artyom");
//   UserDictation.stop();
// }



//################# ANNYANG START ########################

if (annyang) {
  console.log('Annyang ...');
  var recognisedTags = []; // will store recognised tags so they can be removed from the next result
  // the list is cleared when there is a gap in speech
  // the tags will be pulled from the server
  var recognisedTagsUsed = [];
  var tagset = fetchTagset();



  annyang.addCallback('result', function(phrases) {
    var text = phrases[0];
    text = text.toLowerCase();


    // checking if the list is not empty before iterating through it!
    if(recognisedTagsUsed.length != 0){
      recognisedTagsUsed.forEach(function(item){
        text = text.replace(item, "");
      });
    }
    // prints the result with recognised tags removed
    console.log("Recognized text: ", text);
    // goes through the tags and checks if they are in the text
    tagset.forEach(function(tag){
      if(text.toLowerCase().includes(tag)){
        // adds the new recognised tag into the recognisedTag list
        recognisedTags.push(tag);
        console.log(recognisedTags);
        text.replace(tag, "");
      }
    });

    // this will also empty what's currently in the recognised tags
    if(recognisedTags){
      makeAjaxRequest();
      recognisedTagsUsed = recognisedTagsUsed.concat(recognisedTags);
      recognisedTags = [];
    }


  });

  annyang.addCallback('end', function() {
    if(recognisedTagsUsed.length != 0){
      recognisedTagsUsed = [];
    }
  });


  // Start listening. You can call this here, or attach this call to an event, button, etc.



  $("#start").click(function () {
    $(".control").toggleClass('hidden');
    //noSleep.enable();
    //startArtyom();
    annyang.start({ autoRestart: true, continuous: false});
    var  recognition = annyang.getSpeechRecognizer();
    recognition.interimResults = true;
    console.log("Started listening");
  });

  // Stop listening button
  $("#stop").click(function () {
    $(".control").toggleClass('hidden');
    //noSleep.disable();
    //stopArtyom();
    annyang.pause();
    console.log("Stopped listening");
  });


}






//################# ANNYANG END ########################








// Start listening button
// $("#start").click(function () {
//   $(".control").toggleClass('hidden');
//   //noSleep.enable();
//   //startArtyom();
//   console.log("Started listening");
// });
//
// // Stop listening button
// $("#stop").click(function () {
//   $(".control").toggleClass('hidden');
//   //noSleep.disable();
//   //stopArtyom();
//   console.log("Stopped listening");
// });

function makeAjaxRequest(){
  //only works if local storage is a available in the browser
  if (storageBool) {
    console.log("localStorage available");

    var mentionedTags = localStorage.getItem('mentionedTags');
    if (mentionedTags) {
      $.ajax({
        type: "POST",
        url: "/compare_phrases",
        data: {
          'recognisedTags': JSON.stringify(recognisedTags),
          'mentionedTags': mentionedTags
        },
        timeout: 60000,
        success: function (data) {
          var retrieved = JSON.parse(data);
          console.log(retrieved);
          updateResults(retrieved['assetResults']);
          localStorage.setItem('mentionedTags', JSON.stringify(retrieved[
            'mentionedTags']));
          }
        });
      } else {
        $.ajax({
          type: "POST",
          url: "/compare_phrases",
          data: {
            'recognisedTags': JSON.stringify(recognisedTags),
          },
          timeout: 60000,
          success: function (data) {
            var retrieved = JSON.parse(data);
            console.log(retrieved);
            updateResults(retrieved['assetResults']);
            localStorage.setItem('mentionedTags', JSON.stringify(retrieved[
              'mentionedTags']));
            }
          });
        }
      }
    }

    function updateResults(assets) {
      frequentResults.innerHTML = "";
      for (asset in assets['frequent']) {
        var image = document.createElement("IMG");
        image.src = "/static/resources/images/" + assets['frequent'][asset]['thumbnail'];
        image.setAttribute("data-id", assets['frequent'][asset]['id']);
        image.classList.add("assetThumbnail");
        image.classList.add("animated");
        image.classList.add("faster");
        frequentResults.appendChild(image);
      }
      currentResults.innerHTML = "";
      for (asset in assets['current']) {
        var image = document.createElement("IMG");
        image.src = "/static/resources/images/" + assets['current'][asset]['thumbnail'];
        image.setAttribute("data-id", assets['current'][asset]['id']);
        image.classList.add("assetThumbnail");
        image.classList.add("animated");
        image.classList.add("faster");
        currentResults.appendChild(image);
      }
      applyGestureControls();
    }

    function storageAvailable(type) {
      try {
        var storage = window[type];
        var x = '_storage_test__';
        storage.setItem(x, x);
        storage.removeItem(x);
        return true;
      } catch (e) {
        return e instanceof DOMException && (
          e.code === 22 ||
          e.code === 1014 ||
          e.name === 'QuotaExceededError' ||
          e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
          storage.length !== 0;
        }
      }

      function flushRecentTags(){
        storedTags = JSON.parse(localStorage.getItem('mentionedTags'));
        console.log(storedTags);
        storedTags['recent'] = {};
        localStorage.setItem('mentionedTags', JSON.stringify(storedTags));
      }

      function fetchTagset(){
        var tmp = null;
        $.ajax({
          async: false,
          url: "/fetch_tagset",
          timeout: 60000,
          success: function (data) {
            tmp = JSON.parse(data);
          }
        });
        return tmp;
      }

      function applyGestureControls() {
        $('.assetThumbnail').each(function () {
          var gestures = new Hammer(this);
          // enable swipe detection for all directions
          gestures.get('swipe').set({
            direction: Hammer.DIRECTION_ALL,
            threshold: 1,
            velocity: 0.1
          });
          var element = $(this);
          // listen to events...
          gestures.on("swipeup tap", function (ev) {
            // Swipe up gesture
            if (ev.type == "swipeup") {
              element.removeClass("fadeIn");
              element.addClass("slideOutUp");
              var assetID = element.attr('data-id');
              socket.emit('event', assetID);
              flushRecentTags();
              console.log("sent ID " + assetID + " to socketIO");
              // Add the asset back to the display
              setTimeout(function () {
                // Reset element state (css class transitions)
                element.removeClass("element-increase");
                element.removeClass("element-reset");
                element.removeClass("slideOutUp");
                element.addClass("fadeIn");
              }, 500);
            }
            // Tap gesture
            if (ev.type == "tap") {
              // If the element is already zoomed in
              if (element.hasClass("element-increase")) {
                element.addClass("element-reset");
                element.removeClass("element-increase");
              } else {
                // Reset all elements
                $(".assetThumbnail").removeClass("element-increase");
                $(".assetThumbnail").removeClass("element-reset");
                // Increase size of selected element
                element.addClass("element-increase");
              }
            }
          });
        });
      }

      // Prevent chrome popup menu on hold (android)
      var ua = navigator.userAgent.toLowerCase();
      var isAndroid = ua.indexOf("android") > -1; //&& ua.indexOf("mobile");
      if (isAndroid) {
        window.oncontextmenu = function (event) {
          event.preventDefault();
          event.stopPropagation();
          return false;
        };
      }
