const app = new Vue({
  el: '#app-login',
  data: {
    username: '',
    password: '',
    message: '',
  },
  methods: {
    submitLogin: function () {
      const user = {
        username: this.username,
        password: this.password,
      }
      apiLogin(user)
        .done(data => {
          // Save token
          Cookies.set('accessToken', data.token);
          Cookies.set('userId', data.userId);

          // Redirect to next page
          $(location).attr('href','app.html');
        })
        .fail(err => {
          if (err.status == 401) {
            this.message = 'Invalid credentials';
          }
        });
    }
  }
});
