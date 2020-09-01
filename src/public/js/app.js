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
  },
  mounted: function () {
    const accessToken = Cookies.get('accessToken');
    apiGetDatesMinmax(accessToken)
      .done(data => {
        console.log(data);
        this.datesmin = data.mi;
        this.datesmax = data.ma;

        apiGetWeatherHistory(accessToken, this.datesmin, this.datesmax, 20)
          .done(w => {
            this.weatherData = w;
            this.updateCharts();
            console.log('WW', w);
          })
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
          }
      });
    },
    groupChartData: function () {
      for (var i = 0; i < this.weatherData.length; i++) {
        this.weatherDataGrouped.temp.push(this.weatherData[i].temp)
        this.weatherDataGrouped.hum.push(this.weatherData[i].humidity)
        this.weatherDataGrouped.pres.push(this.weatherData[i].pressure)
        this.weatherDataGrouped.logged.push(this.weatherData[i].logged)
      }
    }
  }
});
