var audioContext = new AudioContext();
var recorder;
var exID;
var recLength;
var userRecUrl;
var userBlob;
var targetPitchData;
var playBar;
var chart;
var chartData;


var startUserMedia = function (stream) {
    var input = audioContext.createMediaStreamSource(stream);
    recorder = new Recorder(input);
};

window.onload = function init() {
    navigator.getUserMedia = (navigator.getUserMedia ||
                              navigator.webkitGetUserMedia ||
                              navigator.mozGetUserMedia ||
                              navigator.msGetUserMedia);
    navigator.getUserMedia({audio: true}, startUserMedia, function(e) { console.warn(e); });
};


var loadAndPlayFile = function (url) {
    var request = new XMLHttpRequest();
    request.open("GET", url, true);
    request.responseType = "arraybuffer";
    request.onload = function() {
        audioContext.decodeAudioData(request.response, function(audioBuffer) {
            var source = audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioContext.destination);
            source.start(0);
        });
    };
    request.send(); 
};

// turn base64-encoded audio data URL into a blob stored in an object URL so it can be played
var dataURItoObjURL = function (dataURI) {
    var byteString = atob(dataURI);
    var intArray = new Uint8Array(byteString.length);
    for (var i = 0; i < byteString.length; i++) {
        intArray[i] = byteString.charCodeAt(i);
    }
    var blob = new Blob([intArray], {type: 'audio/wav'});
    return (window.URL || window.webkitURL).createObjectURL(blob);
};


var handleRecord = function (exID, recLength) {
   if ($('.record.' + exID).html() == '<span class="glyphicon glyphicon-record"></span> Record') {
        startRecord(exID, recLength);
        setTimeout(function () { 
            stopRecord(exID); 
        }, (recLength * 1000));
    } else {
        stopRecord(exID);
        playBar.remove();
    }
};

var startRecord = function (exID, recLength) {
    recorder.clear();
    recorder.record();
    $('.record.' + exID).html('<span class="glyphicon glyphicon-stop"></span> Stop');
    animatePlaybar(recLength);
};

var stopRecord = function (exID) {
    recorder.stop();
    recorder.exportWAV(function (blob) {
        userBlob = blob;
        userRecUrl = (window.URL || window.webkitURL).createObjectURL(blob);
    });
    $('.record.' + exID).html('<span class="glyphicon glyphicon-record"></span> Record');
    $('.analyze.' + exID).removeAttr('disabled');
    $('.play-back.' + exID).removeAttr('disabled');
};


var analyzeUserPitch = function (blob, targetPitchData, exID) {
    $('.loading.' + exID).show();
    var reader = new FileReader();
    // this is triggered once the blob is read and readAsDataURL returns
    reader.onload = function (event) {
        var formData = new FormData();
        formData.append('user_rec', event.target.result);
        formData.append('ex_id', exID);
        $.ajax({
            type: "POST",
            url: '/analyze',
            data: formData, 
            processData: false,
            contentType: false,
            dataType: 'json',
            cache: false,
            success: function(response) {
                var attempt = response.attempt;
                if (!attempt.attempt_num) {
                    var attemptNum = 1;
                    if ($('.attempts').children().length) {
                        attemptNum += parseInt($('.attempts .attempt:last-child').attr('class').split(' ')[1]);
                    }
                    attempt.attempt_num = attemptNum;
                }
                addPlayDeleteAttemptBtns(attempt);
                chartData.push({
                    values: attempt.pitch_data,
                    key: 'Recording #' + attempt.attempt_num
                });
                updateGraph();
                $('.loading').hide();
            }
        });
    };
    reader.readAsDataURL(blob);
    recorder.clear();
};


var buildGraph = function (recLength) {
    nv.addGraph(function() {
        chart = nv.models.lineChart()
            .useInteractiveGuideline(true)
            .interpolate("basis")
            .xDomain([0, recLength]);      
    
        chart.xAxis
            .axisLabel('Time (s)')
            .tickFormat(d3.format(',.1f'));
    
        chart.yAxis
            .axisLabel('Pitch (Hz)')
            .tickFormat(d3.format(',d'));
    
        d3.select('.chart.' + exID + ' svg')
            .datum(chartData)
            .transition().duration(500)
            .call(chart);
    
        nv.utils.windowResize(chart.update);
        
        return chart;
    });
};

var updateGraph = function (userPitchData, attemptNum) {
    d3.select('.chart.' + exID + ' svg')
        .datum(chartData)
        .transition().duration(500);
    
    chart.update();
};

var animatePlaybar = function (recLength) {
    var svg = d3.selectAll(".chart svg");
    playBar = svg.append("line")
        .attr("x1", 60)
        .attr("y1", 20)
        .attr("x2", 60)
        .attr("y2", 500)
        .attr("stroke-width", 1)
        .attr("stroke", "black");
    playBar.transition()
        .attr("x1", 900)   // width of graph
        .attr("x2", 900)
        .duration(recLength*1000)
        .ease("linear")
        .transition()
        .delay(recLength*1000)
        .duration(200)
        .remove();
};


var addPlayDeleteAttemptBtns = function (attempt) {
    newPlayBtn = $('<button>').attr('class', 'btn btn-primary play-attempt btn-sm')
        .html('<span class="glyphicon glyphicon-play"></span> Play')
        .on('click', function (evt) {
            loadAndPlayFile(dataURItoObjURL(attempt.audio_data));
            animatePlaybar(recLength);
        });
    newDelBtn = $('<button>').attr('class', 'btn btn-danger del-attempt btn-sm')
        .html('<span class="glyphicon glyphicon-remove"></span> Delete')
        .on('click', function (evt) {
            if (attempt.id) {
                $.post('/delete-attempt', {id: attempt.id}, function () {
                    loadTab(exID, recLength);
                });
            } else {
                var attemptContainer = $('.attempt.' + attempt.attempt_num);
                var idx = attemptContainer.index();
                attemptContainer.remove();
                chartData.splice(idx + 1, 1);
                updateGraph();
            }
        });
    var attemptDiv = $('<div>').attr('class', 'attempt ' + attempt.attempt_num)
        .append('<b>#' + attempt.attempt_num + '</b> ', newPlayBtn, ' ', newDelBtn, '<br><br>');
    $('.attempts').append(attemptDiv);
};


var loadTab = function (exID, recLength) {
    $.post('/targetdata', {sentence: exID}, function (response) {
        targetPitchData = response.target_pitch_data;
        var attempts = response.attempts;
        chartData = [{
            key: 'Target intonation',
            values: targetPitchData
        }];
        buildGraph(recLength);
        $('.chart').show();
        $('.attempts').empty();
        for (i = 0; i < attempts.length; i++) {
            var attempt = attempts[i];
            addPlayDeleteAttemptBtns(attempt);
            chartData.push({
                key: 'Recording #' + attempt.attempt_num,
                values: attempt.pitch_data
            });
        }
    });
};

var switchTabs = function (exID, recLength) {
    $('.chart.' + exID).hide();
    loadTab(exID, recLength);
};


// when page loads
$(document).ready(function () {
    $('#tabs').tab();
    $('.loading').hide();
  
    // disable playback & compare buttons until user has recorded in that tab
    $('.play-back').attr('disabled','disabled');
    $('.analyze').attr('disabled','disabled');

    // when play button is pressed, play sample sentence & animate play bar across graph
    $('.play').on('click', function (evt) {
        loadAndPlayFile("/sounds/" + exID + ".wav");
        animatePlaybar(recLength);
    });

    // for play buttons in overview tab, retrieve exID from classes & play that file
    $('.ov-play').on('click', function (evt) {
        exID = $(this).attr("class").split(' ')[3];
        loadAndPlayFile("/sounds/" + exID + ".wav");
    });

    // when playback button is pressed, play user's recording
    $('.play-back').on('click', function (evt) {
        loadAndPlayFile(userRecUrl);
        animatePlaybar(recLength);
    });

    // when Record/Stop button is pressed
    $('.record').on('click', function (evt) {
        handleRecord(exID, recLength);
    });

    // when Compare button is pressed, analyze user's recording & show graph
    $('.analyze').on('click', function (evt) {
        analyzeUserPitch(userBlob, targetPitchData, exID);
        $('.play-back').attr('disabled','disabled');
        $('.analyze').attr('disabled','disabled');
    });
});

$(document).on('hidden.bs.tab', 'a[data-toggle="tab"]', function (e) {
    // re-disable playback & compare buttons when user navigates away from tab
    $('.play-back').attr('disabled','disabled');
    $('.analyze').attr('disabled','disabled'); 
});
