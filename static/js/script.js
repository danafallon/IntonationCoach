// Audio player setup

var buf = null;

//create AudioContext
var context = new AudioContext;

//load and decode wav file - can't use ajax bc it doesn't support responseType?
function loadFile(url) { 
    var request = new XMLHttpRequest(); 
    request.open("GET", url, true); 
    request.responseType = "arraybuffer"; 
    request.onload = function() { 
        //decode the loaded data 
        context.decodeAudioData(request.response, function(buffer) { 
            buf = buffer;
            // call playSound() once buffer is loaded
            playSound();
        }); 
    }; 
    request.send(); 
} 

//play the loaded file 
function playSound() { 
    //create a source node from the buffer 
    var src = context.createBufferSource();  
    src.buffer = buf; 
    //connect to the final output node (the speakers) 
    src.connect(context.destination); 
    //play immediately 
    src.start(0); 
} 


// Recorder setup (using Recorder.js)

var recorder;
var userRecUrl;
var userBlob;

function startUserMedia(stream) {
  var input = context.createMediaStreamSource(stream);
  recorder = new Recorder(input);
}

window.onload = function init() {
  navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);
  navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
      console.log('Error: ', e);
    });
};

// create object url for blob when exportWAV is called
function myCallback(blob) {
  userRecUrl = (window.URL || window.webkitURL).createObjectURL(blob);
  userBlob = blob;
}

// change buttons & trigger animation when user clicks record button
function handleRecord(exID, recLength) {
  if ($('.record.'+exID).html() == "Record") {
    recorder.record();
    $('.record.'+exID).html("Stop");
    animatePlaybar(recLength);
  } else {
    recorder.stop();
    recorder.exportWAV(myCallback);
    $('.record.'+exID).html("Record");
    $('.analyze.'+exID).removeAttr('disabled');
    $('.play-back.'+exID).removeAttr('disabled');
  }
};

var targetPitchData;

// send user's recording & sentence id to server, assign pitch data from response to variables, build graph
function showUserPitch(blob, targetPitchData, exID) {
    $('.loading.'+exID).show();
  var reader = new FileReader();
  // this is triggered once the blob is read and readAsDataURL returns
  reader.onload = function (event) {
    var formData = new FormData();
    formData.append('user_rec', event.target.result);
    $.ajax({
      type: "POST",
      url: '/analyze',
      data: formData, 
      processData: false,
      contentType: false,
      dataType: 'json',
      cache: false,
      success: function(response) {
        userPitchData = JSON.parse(response['user']);
        updateGraph(targetPitchData, userPitchData, exID);
      }
    });
  }
  reader.readAsDataURL(blob);

  recorder.clear();
};
  
var chart;

// build graph with NVD3
function buildGraph(targetPitchData, exID, recLength) {
  nv.addGraph(function() {
    chart = nv.models.lineChart()
      .useInteractiveGuideline(true)
      .interpolate("basis")
      .forceX([0, recLength]);      
    
    chart.xAxis
      .axisLabel('Time (s)')
      .tickFormat(d3.format(',.1f'));
    
    chart.yAxis
      .axisLabel('Pitch (Hz)')
      .tickFormat(d3.format(',d'));
    
    d3.select('.chart.'+exID+' svg')
      .datum(targetData(targetPitchData))
      .transition().duration(500)
      .call(chart);
    
    nv.utils.windowResize(chart.update);
    
    return chart;
  });
}

// add user's pitch data to graph
function updateGraph(targetPitchData, userPitchData, exID) {
  d3.select('.chart.'+exID+' svg')
    .datum(allData(targetPitchData, userPitchData))
    .transition().duration(500);
    
    chart.update();
    $('.loading').hide();
}

// create dataset with just target pitch data
function targetData(targetPitchData) {
  return [
    {
      values: targetPitchData,
      key: 'Target intonation'
    }
  ];
}

// create dataset with target & user pitch data 
function allData(targetPitchData, userPitchData) {
  return [
    {
      values: targetPitchData,
      key: 'Target intonation'
    },
    {
      values: userPitchData,
      key: 'Your intonation',
      color: '#ff7f0e'
    }
  ];
}

function animatePlaybar(recLength) {
  // create playbar
  var svg = d3.selectAll(".chart svg");
  var playBar = svg.append("line")
    .attr("x1", 60)
    .attr("y1", 20)
    .attr("x2", 60)
    .attr("y2", 500)
    .attr("stroke-width", 1)
    .attr("stroke", "black");
  // animate playbar
  playBar.transition()
    .attr("x1", 1120)   // sub in width of graph
    .attr("x2", 1120)   // " " "
    .duration(recLength*1000)     // sub in length of recording
    .ease("linear")
    .transition()
      .delay(recLength*1000)      // length of recording again
      .duration(200)
      .remove();
}

// initialize variables that will be reassigned each time a tab is shown
var exID;
var recLength;

// get target pitch data from server & build graph (will be called each time a tab is shown)
function loadTab(exID, recLength) {
  $.post('/targetdata', { sentence: exID }, function(response) {
    targetPitchData = JSON.parse(response['target']);
    buildGraph(targetPitchData, exID, recLength);
  });
}


// when page loads:
$(document).ready(function () {
  $('#tabs').tab();
  $('.loading').hide();
  
  // disable playback & compare buttons until user has recorded in that tab
  $('.play-back').attr('disabled','disabled');
  $('.analyze').attr('disabled','disabled');

  // when play button is pressed, play sample sentence & animate play bar across graph
  $('.play').on('click', function(evt) {
    loadFile("/sounds/"+exID+".wav");
    animatePlaybar(recLength);
  });

  // when playback button is pressed, play user's recording
  $('.play-back').on('click', function(evt) {
    loadFile(userRecUrl);
    animatePlaybar(recLength);
  });

  // when Record/Stop button is pressed
  $('.record').on('click', function(evt) {
    handleRecord(exID, recLength);
  });

  // when Compare button is pressed, analyze user's recording & show graph
  $('.analyze').on('click', function(evt) {
    showUserPitch(userBlob, targetPitchData, exID);
  });
});

$(document).on('hidden.bs.tab', 'a[data-toggle="tab"]', function (e) {
  // re-disable playback & compare buttons when user navigates away from tab
  $('.play-back').attr('disabled','disabled');
  $('.analyze').attr('disabled','disabled'); 
});






