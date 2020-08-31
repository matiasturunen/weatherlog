function apiLogin(user) {
  return $.ajax({
    type: "POST",
    url: '/api/login',
    data: user,
  });
}

function apiLogout(accessToken) {
  return $.ajax({
    type: "POST",
    url: "/api/logout",
    data: { accessToken: accessToken },
  });
}

function apiGetDatesMinmax(accessToken) {
  return $.ajax({
    type: 'GET',
    url: '/api/datesminmax',
    data: { accessToken: accessToken },
  });
}