import * as auth from '../src/server/auth';
import * as db from '../src/server/db';

const args = process.argv.slice(2);
db.findUser({ username: args[0] })
  .then(user => auth.createAccesstoken(user, 7200000))
  .then(token => console.log('User:', args[0], 'token:', token))
  .catch(err => console.error(err));