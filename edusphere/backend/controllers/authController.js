const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const config = require('config');
const { createUser, getUserByEmail } = require('../models/User'); // Adjust the path as necessary

exports.register = async (req, res) => {
  const { name, email, password } = req.body;

  try {
    const userCheck = await getUserByEmail(email);
    if (userCheck) {
      return res.status(400).json({ msg: 'User already exists' });
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    const newUser = await createUser(name, email, hashedPassword);

    const payload = {
      user: {
        id: newUser.id
      }
    };

    jwt.sign(
      payload,
      config.get('jwtSecret'),
      { expiresIn: 3600 },
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
};

exports.login = async (req, res) => {
  const { email, password } = req.body;

  try {
    const userCheck = await getUserByEmail(email);
    if (!userCheck) {
      return res.status(400).json({ msg: 'Invalid Credentials' });
    }

    const user = userCheck;

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ msg: 'Invalid Credentials' });
    }

    const payload = {
      user: {
        id: user.id
      }
    };

    jwt.sign(
      payload,
      config.get('jwtSecret'),
      { expiresIn: 3600 },
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
};
