// initialize chart and variables
google.charts.load('current', {'packages':['line']});
var grpTimer;
var gTable = document.getElementById('groupDataTable'); 

// now continuously get server updates
grpTimer = setInterval(updateGroups, 5000); // 5 seconds

// get activity update
updateGroups();

function debugStr(str) {
  var x = document.getElementById("debugStr");
  x.innerHTML = str;
}

function refreshGroups(s) {
  // prepare table
  var row = gTable.insertRow();
  console.log('small_viewer.js - refreshGroups - row:');
  console.log(row);
  console.log('small_viewer.js - refreshGroups - s:');
  console.log(s);
  var cellBleMac = row.insertCell(0);
  var cellTimestamp = row.insertCell(1);
  var cellBleRSSI = row.insertCell(2);

  // fill cells with data
  cellBleMac.innerHTML = s.hour;
  cellTimestamp.innerHTML = s.avg_temp;
  cellBleRSSI.innerHTML = s.avg_hum;
}

//============== Update Current Group's Table =================
function clearGroups() {
  // clear all except first row
  var x = gTable.rows.length;
  for (var i=x-1; i>0; i--)
    gTable.deleteRow(i);
}

// load the status of all table entries
function updateGroups() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      console.log("small_viewer.js - updateGroups - this.responseText:");
      console.log(this.responseText);
      var statsObj = JSON.parse(this.responseText);
      clearGroups();
      // received data, let's fill in the data for each group
      statsObj.mcdata.forEach(refreshGroups); 
    }
  };

  var jObj;
  console.log("window.parent.MAC");
  console.log(window.parent.MAC);
  jObj = {cmd:"UPDATETABLE", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);
}

// My IoT device's data
google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(drawWeather);

function drawWeather() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.mcdata);
      }
  };

  var jObj;
  jObj = {cmd:"GETMCDATA", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('weather_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Hour');
    data.addColumn('number', "Average Temperature");
    data.addColumn('number', "Average Humidity");

    data.addRows(obj);

    var materialOptions = {
      chart: {
        title: "Average Temperature and Humidity from Group's Device"
      },
      width: 900,
      height: 500,
      series: {
        // Gives each series an axis name that matches the Y-axis below.
        0: {axis: 'Temperature'},
        1: {axis: 'Humidity'}
      },
      axes: {
        // Adds labels to each axis; they don't have to match the axis names.
        y: {
          Temperature: {label: 'Temperature (Celsius)'},
          Humidity: {label: 'Humidity'}
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.charts.Line(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Meteostat API data
google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(drawMeteostatWeather);

function drawMeteostatWeather() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.meteostatdata);
      }
  };

  var jObj;
  jObj = {cmd:"GETMETEOSTATDATA", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('meteostat_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Hour');
    data.addColumn('number', "Average Temperature");
    data.addColumn('number', "Average Humidity");

    data.addRows(obj);

    var materialOptions = {
      chart: {
        title: 'Average Temperature and Humidity Forecast from Meteostat'
      },
      width: 900,
      height: 500,
      series: {
        // Gives each series an axis name that matches the Y-axis below.
        0: {axis: 'Temperature'},
        1: {axis: 'Humidity'}
      },
      axes: {
        // Adds labels to each axis; they don't have to match the axis names.
        y: {
          Temperature: {label: 'Temperature (Celsius)'},
          Humidity: {label: 'Humidity'}
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.charts.Line(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Temperature comparison data
google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(drawTemperatureComparison);

function drawTemperatureComparison() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log('small_viewer.js - drawTemperatureComparison - this.responseText:');
          console.log(this.responseText);
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.temperatures);
      }
  };

  var jObj;
  jObj = {cmd:"GETTEMPERATURES", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('temperature_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Hour');
    data.addColumn('number', "Group Temperature");
    data.addColumn('number', "Temperature Forecast");

    data.addRows(obj);

    var materialOptions = {
      chart: {
        title: "Average Temperature between Group's Device and Forecast"
      },
      width: 900,
      height: 500,
      series: {
        // Gives each series an axis name that matches the Y-axis below.
        0: {axis: 'Group'},
        1: {axis: 'Forecast'}
      },
      axes: {
        // Adds labels to each axis; they don't have to match the axis names.
        y: {
          Group: {label: 'Group Temperature (Celsius)'},
          Forecast: {label: 'Temperature Forecast (Celsius)'}
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.charts.Line(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Humidity comparison data
google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(drawHumidityComparison);

function drawHumidityComparison() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log('small_viewer.js - drawHumidityComparison - this.responseText:');
          console.log(this.responseText);
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.humidities);
      }
  };

  var jObj;
  jObj = {cmd:"GETHUMIDITIES", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('humidity_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Hour');
    data.addColumn('number', "Group Humidity");
    data.addColumn('number', "Humidity Forecast");

    data.addRows(obj);

    var materialOptions = {
      chart: {
        title: "Average Humidity between Group's Device and Forecast"
      },
      width: 900,
      height: 500,
      series: {
        // Gives each series an axis name that matches the Y-axis below.
        0: {axis: 'Group'},
        1: {axis: 'Forecast'}
      },
      axes: {
        // Adds labels to each axis; they don't have to match the axis names.
        y: {
          Group: {label: 'Group Humidity'},
          Forecast: {label: 'Humidity Forecast'}
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.charts.Line(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Compare Temperatures data
google.charts.load('current', {'packages':['bar', 'corechart']});
google.charts.setOnLoadCallback(compareTemperatures);

function compareTemperatures() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log('small_viewer.js - compareTemperatures - this.responseText:');
          console.log(this.responseText);
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.comparetemperatures);
      }
  };

  var jObj;
  jObj = {cmd:"COMPARETEMPERATURES", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('comparetemperatures_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'People');
    data.addColumn('number', 'Root Mean Square Error (RMSE)');
    data.addColumn('number', 'Mean Absolute Error (MAE)');
    data.addColumn('number', 'Mean Absolute Percentage Error (MAPE)');

    data.addRows(obj);

    var materialOptions = {
      title: "Comparing Temperature Accuracy Between Group and Class",
      chartArea: {width: '50%'},
      colors: ['#b0120a', '#00008B', '#ffab91'],
      hAxis: {
        title: 'Metric Value',
        minValue: 0,
        textStyle: {
          bold: true,
          fontSize: 12,
          color: '#4d4d4d'
        },
        titleTextStyle: {
          bold: true,
          fontSize: 18,
          color: '#4d4d4d'
        }
      },
      vAxis: {
        title: 'People (Group or Class)',
        textStyle: {
          fontSize: 14,
          bold: true,
          color: '#848484'
        },
        titleTextStyle: {
          fontSize: 14,
          bold: true,
          color: '#848484'
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.visualization.BarChart(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Compare Humidities data
google.charts.load('current', {'packages':['bar', 'corechart']});
google.charts.setOnLoadCallback(compareHumidities);

function compareHumidities() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log('small_viewer.js - compareHumidities - this.responseText:');
          console.log(this.responseText);
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.comparehumidities);
      }
  };

  var jObj;
  jObj = {cmd:"COMPAREHUMIDITIES", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('comparehumidities_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'People');
    data.addColumn('number', 'Root Mean Square Error (RMSE)');
    data.addColumn('number', 'Mean Absolute Error (MAE)');
    data.addColumn('number', 'Mean Absolute Percentage Error (MAPE)');

    data.addRows(obj);

    var materialOptions = {
      title: "Comparing Humidity Accuracy Between Group and Class",
      chartArea: {width: '50%'},
      colors: ['#b0120a', '#00008B', '#ffab91'],
      hAxis: {
        title: 'Metric Value',
        minValue: 0,
        textStyle: {
          bold: true,
          fontSize: 12,
          color: '#4d4d4d'
        },
        titleTextStyle: {
          bold: true,
          fontSize: 18,
          color: '#4d4d4d'
        }
      },
      vAxis: {
        title: 'People (Group or Class)',
        textStyle: {
          fontSize: 14,
          bold: true,
          color: '#848484'
        },
        titleTextStyle: {
          fontSize: 14,
          bold: true,
          color: '#848484'
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.visualization.BarChart(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Temperature offset data
google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(drawTemperatureOffsets);

function drawTemperatureOffsets() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log('small_viewer.js - drawTemperatureOffsets - this.responseText:');
          console.log(this.responseText);
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.offsettemperatures);
      }
  };

  var jObj;
  jObj = {cmd:"OFFSETTEMPERATURES", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('temperature_offset_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Hour');
    data.addColumn('number', "Group Temperature Offset");
    data.addColumn('number', "Class Temperature Offset");

    data.addRows(obj);

    var materialOptions = {
      chart: {
        title: "Comparing Temperature Offsets Between Group and Class Throughout the Day"
      },
      width: 900,
      height: 500,
      series: {
        // Gives each series an axis name that matches the Y-axis below.
        0: {axis: 'Group'},
        1: {axis: 'Class'}
      },
      axes: {
        // Adds labels to each axis; they don't have to match the axis names.
        y: {
          Group: {label: 'Group Temperature Offset (Celsius)'},
          Class: {label: 'Class Temperature Offset (Celsius)'}
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.charts.Line(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}

// Humidity offset data
google.charts.load('current', {'packages':['line', 'corechart']});
google.charts.setOnLoadCallback(drawHumidityOffsets);

function drawHumidityOffsets() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log('small_viewer.js - drawHumidityOffsets - this.responseText:');
          console.log(this.responseText);
          var statsObj = JSON.parse(this.responseText);
          weather(statsObj.offsethumidities);
      }
  };

  var jObj;
  jObj = {cmd:"OFFSETHUMIDITIES", devmac:window.parent.MAC};
  var jStr = JSON.stringify(jObj);
  var urlStr = "http://dsc-iot.ucsd.edu/api_gid07/API2.py";
  xmlhttp.open("POST", urlStr, true);
  xmlhttp.setRequestHeader('Content-Type', 'application/json');
  xmlhttp.send(jStr);

  function weather(obj) {
    var chartDiv = document.getElementById('humidity_offset_chart');
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Hour');
    data.addColumn('number', "Group Humidity Offset");
    data.addColumn('number', "Class Humidity Offset");

    data.addRows(obj);

    var materialOptions = {
      chart: {
        title: "Comparing Humidity Offsets Between Group and Class Throughout the Day"
      },
      width: 900,
      height: 500,
      series: {
        // Gives each series an axis name that matches the Y-axis below.
        0: {axis: 'Group'},
        1: {axis: 'Class'}
      },
      axes: {
        // Adds labels to each axis; they don't have to match the axis names.
        y: {
          Group: {label: 'Group Humidity Offset (Celsius)'},
          Class: {label: 'Class Humidity Offset (Celsius)'}
        }
      }
    };

    function drawMaterialChart() {
      var materialChart = new google.charts.Line(chartDiv);
      materialChart.draw(data, materialOptions);
    }

    drawMaterialChart();
  }
}
