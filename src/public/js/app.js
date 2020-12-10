const app = new Vue({
  el: '#app-main',
  data: {
    datesmin: '',
    datesmax: '',
    weatherData: [],
    weatherDataGrouped: {
      temp: [],
      hum: [],
      pres: [],
      logged: [],
    },
    weatherDataMultiSensor: [
      {
        sensor: 0,
        temp: [],
        hum: [],
        pres: [],
        logged: [],
      },
    ],
    timeFrom: '',
    timeTo: '',
    dataEntries: 10,
    latestEntries: 10,
    isAuthorized: false,
    sensorsVisible: [],
    sensorsAvailable: [],
    currentCharts: [],
    chartBorderColors: [
      'rgba(255, 25, 25, 0.2)',
      'rgba(45, 74, 235, 0.2)',
      'rgba(74, 235, 45, 0.2)',
    ],
    chartBackgroundColors: [
      'rgba(235, 45, 67, 0.1)',
      'rgba(45, 74, 235, 0.1)',
      'rgba(74, 235, 45, 0.1)',
    ],
  },
  mounted: function () {
    const accessToken = Cookies.get('accessToken');
    Promise.all([apiGetDatesMinmax(accessToken), apiGetAvailableSensors(accessToken)])
      .then(values => {
        data = values[0];
        sensors = values[1];

        console.log('DATA', data);
        console.log('SENS', sensors);

        this.isAuthorized = true;

        this.datesmin = data.mi;
        this.datesmax = data.ma;

        // Update date selectors to have only values that are in DB
        $('#weather-timeFrom').attr('min', this.datesmin.slice(0, -5)); // Trim timezone
        $('#weather-timeFrom').attr('max', this.datesmax.slice(0, -5));
        $('#weather-timeTo').attr('min', this.datesmin.slice(0, -5));
        $('#weather-timeTo').attr('max', this.datesmax.slice(0, -5));

        this.sensorsAvailable = sensors;

        apiGetWeatherHistory(accessToken, this.datesmin, this.datesmax, this.dataEntries, this.sensorsAvailable[0].id)
          .done(w => {
            this.weatherData = w;
            this.updateCharts();
            console.log('WW', w);
          })
          .fail(err => console.error(err));

      })
    apiGetDatesMinmax(accessToken)
      .done(data => {
      })
      .fail(err => console.error(err));
  },
  methods: {
    getSensor: function (id) {
      console.log('ID', id);
      for (var i = 0; i < this.sensorsAvailable.length; i++) {
        if (this.sensorsAvailable[i].id == id) {
          return this.sensorsAvailable[i];
        }
      }
      return new Error('No sensor found with id: ' + id);
    },
    getChartBorderColor: function (index) {
      if (index >= this.chartBorderColors.length) {
        return this.chartBorderColors[(index % this.chartBorderColors.length)];
      } else {
        return this.chartBorderColors[index];
      }
    },
    getChartBackgroundColor: function (index) {
      if (index >= this.chartBackgroundColors.length) {
        return this.chartBackgroundColors[(index % this.chartBackgroundColors.length)];
      } else {
        return this.chartBackgroundColors[index];
      }
    },
    createChart: function (htmlElement, labels, datasets) {
      const ctx = document.getElementById(htmlElement).getContext('2d');
      const chrt = new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: datasets,
          },
          options: {
            events: ['click', 'mousemove']
          }
      });
      this.currentCharts.push(chrt);
    },
    updateCharts: function () {
      // Destroy previous charts to avoid flickering
      for (var i = 0; i < this.currentCharts.length; i++) {
        this.currentCharts[i].destroy();
        console.log('Destroyed chart');
      }
      this.currentCharts = [];

      this.groupChartData();

      if (this.sensorsVisible.length == 1) {
        this.createChart('tempChart', this.weatherDataGrouped.logged, [{
          label: 'Temperature',
          data: this.weatherDataGrouped.temp,
          borderColor: 'rgba(255, 25, 25, 0.2)',
          backgroundColor: 'rgba(235, 45, 67, 0.1)',
        }]);

        this.createChart('humChart', this.weatherDataGrouped.logged, [{
          label: 'Humidity',
          data: this.weatherDataGrouped.hum,
          borderColor: 'rgba(45, 74, 235, 0.2)',
          backgroundColor: 'rgba(45, 74, 235, 0.1)',
        }]);

        this.createChart('presChart', this.weatherDataGrouped.logged, [{
          label: 'Pressure',
          data: this.weatherDataGrouped.pres,
          borderColor: 'rgba(74, 235, 45, 0.2)',
          backgroundColor: 'rgba(74, 235, 45, 0.1)',
        }]);
      } else {
        const tempDatasets = [];
        const humDatasets = [];
        const presDatasets = [];

        for (var i = 0; i < this.weatherDataMultiSensor.length; i++) {
          tempDatasets.push({
            label: this.getSensor(this.weatherDataMultiSensor[i].sensor).name,
            data: this.weatherDataMultiSensor[i].temp,
            borderColor: this.getChartBorderColor(i),
            backgroundColor: this.getChartBackgroundColor(i),
          });

          humDatasets.push({
            label: this.getSensor(this.weatherDataMultiSensor[i].sensor).name,
            data: this.weatherDataMultiSensor[i].hum,
            borderColor: this.getChartBorderColor(i+1),
            backgroundColor: this.getChartBackgroundColor(i+1),
          });

          presDatasets.push({
            label: this.getSensor(this.weatherDataMultiSensor[i].sensor).name,
            data: this.weatherDataMultiSensor[i].pres,
            borderColor: this.getChartBorderColor(i+2),
            backgroundColor: this.getChartBackgroundColor(i+2),
          });
        }

        this.createChart('tempChart', this.weatherDataMultiSensor[0].logged, tempDatasets);
        this.createChart('humChart', this.weatherDataMultiSensor[0].logged, humDatasets);
        this.createChart('presChart', this.weatherDataMultiSensor[0].logged, presDatasets);
      }

    },
    groupChartData: function () {
      this.weatherDataGrouped.temp = [];
      this.weatherDataGrouped.hum = [];
      this.weatherDataGrouped.pres = [];
      this.weatherDataGrouped.logged = [];

      if (this.sensorsVisible.length == 1) { // Only 1 sensor
        for (var i = 0; i < this.weatherData.length; i++) {
          this.weatherDataGrouped.temp.push(this.weatherData[i].temp)
          this.weatherDataGrouped.hum.push(this.weatherData[i].humidity)
          this.weatherDataGrouped.pres.push(this.weatherData[i].pressure)
          this.weatherDataGrouped.logged.push(this.weatherData[i].logged)
        }
      } else {
        this.weatherDataMultiSensor = [];
        for (var i = 0; i < this.weatherData.length; i++) {
          const sensorData = {
            sensor: 0,
            temp: [],
            hum: [],
            pres: [],
            logged: [],
          };
          sensorData.sensor = this.weatherData[i][0].sensor
          
          for(var j = 0; j < this.weatherData[i].length; j++) {
            sensorData.temp.push(this.weatherData[i][j].temp);
            sensorData.hum.push(this.weatherData[i][j].humidity);
            sensorData.pres.push(this.weatherData[i][j].pressure);
            sensorData.logged.push(this.weatherData[i][j].logged);
          }
          this.weatherDataMultiSensor.push(sensorData);
        }
      }
    },
    loadWeather: function () {
      const accessToken = Cookies.get('accessToken');
      if (!this.dataEntries || this.dataEntries < 2 || this.dataEntries > 1000) {
        this.dataEntries = 10;
      }

      apiGetWeatherHistory(accessToken, this.timeFrom, this.timeTo, this.dataEntries, this.sensorsVisible[0])
        .done(w => {
          this.weatherData = w;
          this.updateCharts();
          console.log('WW', w);
        })
        .fail(err =>{
          console.error('apiGetWeatherHistory', err);
          if (err.status = 404) {
            appendError(err.responseText)
          }
        });
    },
    loadLatestWeather: function () {
      const accessToken = Cookies.get('accessToken');
      if (!this.latestEntries || this.latestEntries < 2 || this.latestEntries > 1000) {
        this.latestEntries = 10;
      }
      if (this.sensorsVisible.length == 1) {
        apiGetLatestWeather(accessToken, this.latestEntries, this.sensorsVisible[0])
          .done(w => {
            this.weatherData = w;
            this.updateCharts();
            console.log('WW', w);
          })
          .fail(err => console.error(err));
      } else {
        this.weatherData = [];

        const promises = [];
        for (var i = 0; i < this.sensorsVisible.length; i++) {
          promises.push(apiGetLatestWeather(accessToken, this.latestEntries, this.sensorsVisible[i])
            .done(w => {
              this.weatherData.push(w);
              return Promise.resolve();
            })
            .fail(err => {
              console.error(err);
              return Promise.reject(err);
            }))
        }
        Promise.all(promises)
          .then(() => this.updateCharts())
          .catch(err => console.error(err));
      }
    },
    logout: function () {
      console.log('Logout');
      const accessToken = Cookies.get('accessToken');
      apiLogout(accessToken)
        .done(() => {
          Cookies.remove('accessToken');
          $(location).attr('href','index.html');
        })
        .fail(err => {
          console.error(err);
          $(location).attr('href','index.html');
        })
    }
  }
});
