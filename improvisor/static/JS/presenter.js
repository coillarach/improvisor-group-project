var asset;

var navigBar = document.getElementById("navigBar");
var presenterView = document.getElementById("presenterView")
emptyViews();

var timer = 0;
var timePassed = 0;

var textFormats = ["txt", "csv"];
var imageFormats = ["jpg", "jpeg", "png", "bmp", "tiff"];

var bckgrnd_color = document.getElementById("data-color").getAttribute("data");

console.log(bckgrnd_color);
$("html").css("background", "none");
$("html").css("background-color", bckgrnd_color );

document.addEventListener("mousemove", function(){
    timer = 0;
    navigBar.classList.remove("hiddenNavigbar");
});

setInterval(function(){
    timer ++;
    if(timer>5) navigBar.classList.add("hiddenNavigbar");
}, 1000);

$(document).ready(function () {
    var socket = io();
    socket.emit('join');
    socket.on('presenter', function (receivedData) {
        console.log(receivedData);

        emptyViews();
        if (receivedData['assettype'] == "file"){
            var directory = receivedData['assetLocation'];
            var temp = directory.split(".");
            var extension = temp[temp.length-1].toLowerCase();

            if(extension == "pdf"){
                $('#embed_display').show();
                $('#embed_display').attr('src', directory);
            } else if (textFormats.includes(extension)) {
                $('#object_display').show();
                $('#object_display').attr('data', directory);
            } else if (imageFormats.includes(extension)) {
                $('#img_display').show();
                $('#img_display').attr('src', directory);
            }
        } else if(receivedData['assettype'] == "link"){
            $('#link_display').show();
            $('#link_display').html(receivedData['assetLink']);
            $('#link_display').attr('href', receivedData['assetLink']);
        }
    });
});

function emptyViews(){
    $(presenterView.children).attr("src", "");
    $(presenterView.children).attr("data", "");
    $(presenterView.children).attr("href", "");
    $(presenterView.children).html("");
    $(presenterView.children).hide();
}
