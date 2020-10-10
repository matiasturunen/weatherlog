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
    timeFrom: '',
    timeTo: '',
    dataEntries: 10,
    latestEntries: 10,
    isAuthorized: false,
    sensorsVisible: [],
    sensorsAvailable: [],
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
    updateCharts: function () {
      this.groupChartData();

      const tempCtx = document.getElementById('tempChart').getContext('2d');
      const tempChart = new Chart(tempCtx, {
          type: 'line',
          data: {
            labels: this.weatherDataGrouped.logged,
            datasets: [{
              label: 'Temperature',
              data: this.weatherDataGrouped.temp,
              borderColor: 'rgba(255, 25, 25, 0.2)',
              backgroundColor: 'rgba(235, 45, 67, 0.1)',
            }]
          },
          options: {
            events: ['click', 'mousemove']
          }
      });

      const humCtx = document.getElementById('humChart').getContext('2d');
      const humChart = new Chart(humCtx, {
          type: 'line',
          data: {
            labels: this.weatherDataGrouped.logged,
            datasets: [{
              label: 'Humidity',
              data: this.weatherDataGrouped.hum,
              borderColor: 'rgba(45, 74, 235, 0.2)',
              backgroundColor: 'rgba(45, 74, 235, 0.1)',
            }]
          },
          options: {
            events: ['click', 'mousemove']
          }
      });

      const presCtx = document.getElementById('presChart').getContext('2d');
      const presChart = new Chart(presCtx, {
          type: 'line',
          data: {
            labels: this.weatherDataGrouped.logged,
            datasets: [{
              label: 'Pressure',
              data: this.weatherDataGrouped.pres,
              borderColor: 'rgba(74, 235, 45, 0.2)',
              backgroundColor: 'rgba(74, 235, 45, 0.1)',
            }]
          },
          options: {
            events: ['click', 'mousemove']
          }
      });
    },
    groupChartData: function () {
      this.weatherDataGrouped.temp = [];
      this.weatherDataGrouped.hum = [];
      this.weatherDataGrouped.pres = [];
      this.weatherDataGrouped.logged = [];

      for (var i = 0; i < this.weatherData.length; i++) {
        this.weatherDataGrouped.temp.push(this.weatherData[i].temp)
        this.weatherDataGrouped.hum.push(this.weatherData[i].humidity)
        this.weatherDataGrouped.pres.push(this.weatherData[i].pressure)
        this.weatherDataGrouped.logged.push(this.weatherData[i].logged)
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
      apiGetLatestWeather(accessToken, this.latestEntries, this.sensorsVisible[0])
        .done(w => {
          this.weatherData = w;
          this.updateCharts();
          console.log('WW', w);
        })
        .fail(err => console.error(err));
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
