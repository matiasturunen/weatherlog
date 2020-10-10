import pg from 'pg-promise';

// Load enviroment variables from the file, if the app status is not production
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

function createVariation(value) {
  if (Math.random() < 0.5) {
    return value * Math.random(); // Random is always between 0 and 1. This will return smaller number
  }
  return value * (1 + Math.random()); // Return bigger than original
}

export function createDummyData(sensor) {
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
  let ld = [];
  let first = true;
  lineReader.on('line', function (line) {
    if (!first) {
      ld = line.split(',');
      promises.push(db.none(`INSERT INTO weather (temp, humidity, pressure, logged, sensor)
        VALUES ($1,$2,$3,$4,$5)`, [createVariation(ld[3]), createVariation(ld[5]), createVariation(ld[10]), ld[0], sensor])
      );
    } else {
      first = false;
    }
  });

  return Promise.all(promises);
}

if (require.main === module) {
  const args = process.argv.slice(2);
  if (!args[0]) {
    console.log('First argument should be sensor id')
  } else {
    createDummyData(args[0])
      .catch(err => console.error('Failed to create dummy data: ', err));
  }
}
