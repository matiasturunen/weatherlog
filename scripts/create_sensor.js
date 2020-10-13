import * as db from '../src/server/db';

const args = process.argv.slice(2);
if (args[0] && args[1]) {
  db.createSensor(args[0], args[1])
    .then(id => console.log('Created sensor', id, 'with name \'' + args[0] + '\' and identifier \'' + args[1] + '\'.'))
} else {
  console.log('Must give 2 positional arguments. Name and identifier. Example: create_sensor.js Outside \'CC:72:6B:45:B7:A2\'')
}