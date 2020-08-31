const app = new Vue({
  el: '#app-main',
  data: {
    datesmin: '',
    datesmax: '',
  },
  mounted: function () {
    const accessToken = Cookies.get('accessToken');
    apiGetDatesMinmax(accessToken)
      .done(data => {
        console.log(data);

      })
      .fail(err => console.error(err));
  },
  methods: {
  }
});
