import pg from 'pg-promise';

// Load enviroment variables from the file, if the app status is not production
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

export function createDummyData() {
  const pgp = pg();

  const dblib = require('../src/server/db.js');

  const dburl = process.env.DATABASE_URL;
  const db = pgp(dburl);

  const path = require('path');
  const filePath = path.join(__dirname, 'weatherHistory.csv');

  const lineReader = require('readline').createInterface({
    input: require('fs').createReadStream(filePath)
  });

  const promises = [];
  let linedata = [];
  let first = true;
  lineReader.on('line', function (line) {
    if (!first) {
      linedata = line.split(',');
      promises.push(db.none(`INSERT INTO weather (temp, humidity, pressure, logged)
        VALUES ($1,$2,$3,$4)`, [linedata[3], linedata[5], linedata[10], linedata[0]])
      );
    } else {
      first = false;
    }
  });

  return Promise.all(promises);
}

if (require.main === module) {
  createDummyData()
    .catch(err => console.error('Failed to create dummy data: ', err));
}
