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

function apiGetWeatherHistory(accessToken, timeFrom, timeTo, n, sensor) {
  if (n) {
    console.log('PARAMS', timeFrom, timeTo, n, sensor)
    return $.ajax({
      type: 'GET',
      url: '/api/weatherhistory/partial',
      data: {
        accessToken: accessToken,
        timeFrom: timeFrom,
        timeTo: timeTo,
        n: n,
        sensor: sensor,
      }
    });
  } else {
    return $.ajax({
      type: 'GET',
      url: '/api/weatherhistory',
      data: {
        accessToken: accessToken,
        timeFrom: timeFrom,
        timeTo: timeTo,
        sensor: sensor,
      }
    });
  }
}

function apiGetLatestWeather(accessToken, n, sensor) {
  return $.ajax({
    type: 'GET',
    url: '/api/weatherhistory/latest',
    data: {
      accessToken: accessToken,
      n: n,
      sensor: sensor,
    }
  });
}

function apiGetAvailableSensors(accessToken) {
  return $.ajax({
    type: 'GET',
    url: '/api/sensors',
    data: { accessToken: accessToken }
  })
}
