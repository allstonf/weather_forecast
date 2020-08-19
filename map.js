// variable declarations
var markers = [];
var infowindow;
var exinfowindow;
var plantinfowindow;
var MAC = 1;
var SWITCH_STATE = -1;
var map;

toggleMarker = document.getElementById('toggle')
toggleMarker.addEventListener('click', function() {
  SWITCH_STATE = -1 * SWITCH_STATE
  console.log('markers before deletion:');
  console.log(markers);
  deleteMarkers();
  console.log('markers after deletion:');
  console.log(markers);
  updateMarkers();
});

function deleteMarkers() {
  markers.forEach((mark) => {mark.setMap(null)})
  markers = [];
}

function addMarker(obj) {
  console.log('map.js - addMarker - obj:');
  console.log(obj);
  dev_lat = parseFloat(obj['dev_lat'])
  dev_long = parseFloat(obj['dev_long'])
  var loc = {lat: dev_lat, lng: dev_long};
  var marker = new google.maps.Marker({
    position: loc,
    map: map,
    title: `Device of Group ${obj['groupID']}`
  });

  // zoom if clicked example
  marker.addListener('click', function() {
    MAC = obj['mac']
    map.setZoom(18);
    map.setCenter(marker.getPosition());
    exinfowindow.open(map, marker);
    plantinfowindow.open(map, marker);
  });
  
  // display info on mouseover
  marker.addListener('mouseover', function() {
    // do a popup with current info
    var currentInfo = `<p><i>Most Recent Time:</i> ${obj['lastseen']}</p>`
    currentInfo += `<p><i>MAC Address:</i> ${obj['mac']}</p>`
    currentInfo += `<p><i>Group #:</i> ${obj['groupID']}</p>`
    infowindow.setContent(currentInfo)
    infowindow.open(map, marker);
  });
  
  // hide info if move moved away
  marker.addListener('mouseout', function() {
    // remove popup 
    infowindow.close();
  });
  markers.push(marker)
}

function updateMarkers() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      console.log("map.js - updateMarkers - this.responseText:");
      console.log(this.responseText);
      var statsObj = JSON.parse(this.responseText);
      console.log(statsObj);
      statsObj.devices.forEach(addMarker); 
    }
  };

  let curGroup = 'all'
  if (SWITCH_STATE == -1) {
    curGroup = '07'
  }

  jObj = {cmd:"GETLOCATIONS", gid:curGroup};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);
}

function initMap() {
  var ourClass = "null";
  infowindow = new google.maps.InfoWindow({
    content: ourClass,
    maxWidth: 300
  });
  
  var exLink = '<iframe width=1070 height=400 src="http://dsc-iot.ucsd.edu/gid07/small_viewer.html"></iframe>';

  exinfowindow = new google.maps.InfoWindow({
    content: exLink,
    maxWidth: 2000,
    maxHeight: 600
  });

  // var contentString;

  // plantinfowindow = new google.maps.InfoWindow({
  //   content: exLink,
  //   maxWidth: 2000,
  //   maxHeight: 600
  // });
  
  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 15,
    center: {lat: 38.7972, lng: -121.282},
    title: 'UCSD DSC190 IoT Device Map'
  });
  updateMarkers();
}