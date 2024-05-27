const config = require('config');
const { Pool } = require('pg');

const pool = new Pool({
  user: config.get('dbUser'),
  host: config.get('dbHost'),
  database: config.get('dbName'),
  password: config.get('dbPassword'),
  port: config.get('dbPort'),
});

pool.connect()
  .then(() => console.log('Connected to the PostgreSQL database'))
  .catch(err => console.error('Connection error', err.stack));

module.exports = pool;
