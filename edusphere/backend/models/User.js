const pool = require('../config/db.js');


const createUser = async (name, email, password) => {
  const query = `
    INSERT INTO users (name, email, password)
    VALUES ($1, $2, $3)
    RETURNING *
  `;
  const values = [name, email, password];
  try {
    const res = await pool.query(query, values);
    return res.rows[0];
  } catch (err) {
    console.error('Error creating user:', err);
    throw err;
  }
};

// Get a user by email
const getUserByEmail = async (email) => {
  const query = `
    SELECT * FROM users WHERE email = $1
  `;
  const values = [email];
  try {
    const res = await pool.query(query, values);
    return res.rows[0];
  } catch (err) {
    console.error('Error getting user by email:', err);
    throw err;
  }
};

// Get a user by ID
const getUserById = async (id) => {
  const query = `
    SELECT * FROM users WHERE id = $1
  `;
  const values = [id];
  try {
    const res = await pool.query(query, values);
    return res.rows[0];
  } catch (err) {
    console.error('Error getting user by ID:', err);
    throw err;
  }
};

// Update a user
const updateUser = async (id, name, email, password) => {
  const query = `
    UPDATE users
    SET name = $1, email = $2, password = $3
    WHERE id = $4
    RETURNING *
  `;
  const values = [name, email, password, id];
  try {
    const res = await pool.query(query, values);
    return res.rows[0];
  } catch (err) {
    console.error('Error updating user:', err);
    throw err;
  }
};

// Delete a user by ID
const deleteUser = async (id) => {
  const query = `
    DELETE FROM users
    WHERE id = $1
    RETURNING *
  `;
  const values = [id];
  try {
    const res = await pool.query(query, values);
    return res.rows[0];
  } catch (err) {
    console.error('Error deleting user:', err);
    throw err;
  }
};

module.exports = {
  createUser,
  getUserByEmail,
  getUserById,
  updateUser,
  deleteUser,
};
