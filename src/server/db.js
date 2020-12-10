import pg from 'pg-promise';
import crypto from 'crypto';
import _ from 'lodash';
import { createErrorPromise } from './lib';

import { cryptPassword } from './lib';

// Load enviroment variables from the file, if the app status is not production
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const dburl = process.env.DATABASE_URL;
const pgp = pg();

const db = pgp(dburl);

export function create_user(name, password, email) {
  password = password || crypto.randomBytes(40).toString('hex');

  const sql = 'INSERT INTO users (username, password, email) VALUES ($1,$2,$3) RETURNING id;';

  return cryptPassword(password)
    .then(p => db.one(sql, [name, p, email], evt => evt.id));
}

export function findUser(params) {
  if (!params) {
    return createErrorPromise('Invalid params', 400); // Must have some params
  }

  const queryPieces = [];
  const queryParams = {};

  let query = 'SELECT * FROM users';

  if (params.email) {
    queryPieces.push('email=${email}');
    queryParams.email = params.email;
  }

  if (params.username) {
    queryPieces.push('username=${username}');
    queryParams.username = params.username;
  }

  if (queryPieces.length != 0) {
    const where = _.join(queryPieces, ' AND ');
    query += ` WHERE ${where} `;
  } else {
    return createErrorPromise('Invalid params', 400); // Must have some query pieces. Without them, it will return first user entity.
  }
  return db.one(query, queryParams);
}

export function saveAccesstoken(user, token) {
  const sql =  'INSERT INTO access_token (token, expires, user_id) VALUES (${token},${expires},${user_id});';

  return db.none(sql, {
    token: token.token,
    expires: token.expires,
    user_id: user.id,
  });
}

export function deleteAccesstokensForUser(user_id) {
  const sql = 'DELETE FROM access_token WHERE user_id=$1;';

  return db.none(sql, [user_id]);
}

export function findUserWithToken(access_token) {
  const sql = `SELECT DISTINCT u.id, u.username, u.email FROM users u \
    INNER JOIN access_token a ON a.user_id=u.id \
    WHERE a.token=$1`;

  return db.one(sql, [access_token.token]);
}

export function getWeatherData(timeFrom, timeTo, sensor) {
  return db.many(`SELECT * FROM weather WHERE logged >= $1 AND logged <= $2 AND sensor=$3`, [timeFrom, timeTo, sensor]);
}

export function getDatesMinMax() {
  return db.one(`SELECT MIN(logged) AS mi, MAX(logged) AS ma FROM weather`);
}

export function getWeatherDataPartial(timeFrom, timeTo, n, sensor) {
  if (n < 2) {
    return createErrorPromise('Invalid N', 400);
  }
  return db.many(`
    WITH w AS (
      SELECT *, ROW_NUMBER() OVER(ORDER BY logged ASC) AS row
      FROM weather
      WHERE logged >= $1 AND logged <= $2 AND sensor=$4
    )

    SELECT * FROM w
    WHERE row % ((SELECT COUNT(*) FROM w) / $3) = 0
    ORDER BY logged ASC
  `, [timeFrom, timeTo, n, sensor]);
}

export function createWeather(temp, hum, pres, sensor) {
  const logged = new Date();
  return db.none('INSERT INTO weather (temp, humidity, pressure, logged, sensor) VALUES ($1, $2, $3, $4, $5)', [temp, hum, pres, logged, sensor]);
}

export function getWeatherDataLatest(n, sensor) {
  if (n < 2) {
    return createErrorPromise('Invalid N. Must be greater or equal to 2', 400);
  } else if (n > 1000) {
    return createErrorPromise('Invalid N. Must be less or equal to 1000', 400);
  }
  // Select n latest values and then sort ascending by logged
  return db.many(`
    WITH w AS (SELECT * FROM weather WHERE sensor=$2 ORDER BY logged DESC LIMIT $1)

    SELECT * FROM w ORDER BY logged ASC
  `, [n, sensor]);
}

export function getAvailableSensors() {
  return db.many('SELECT * FROM sensor');
}

export function createSensor(name, identifier) {
  return db.one('INSERT INTO sensor (name, identifier) VALUES ($1, $2) RETURNING id', [name, identifier]);
}
