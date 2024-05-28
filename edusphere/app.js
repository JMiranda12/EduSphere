const express = require('express');
const path = require('path');
const axios = require('axios');

const app = express();

// Set Pug as the template engine
app.set('view engine', 'pug');
app.set('views', path.join(__dirname, 'views'));

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Body parser middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Define routes
app.get('/', (req, res) => {
  res.render('index', { title: 'EduSphere' });
});

app.get('/login', (req, res) => {
  res.render('login', { title: 'Login' });
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const response = await axios.post('http://localhost:5000/api/auth/login', { email, password });
    res.redirect('/dashboard');
  } catch (error) {
    res.render('login', { title: 'Login', error: 'Invalid credentials' });
  }
});

app.get('/register', (req, res) => {
  res.render('register', { title: 'Register' });
});

app.post('/register', async (req, res) => {
  const { name, email, password, confirmPassword } = req.body;

  if (password !== confirmPassword) {
    return res.render('register', { title: 'Register', message: 'Passwords do not match' });
  }

  try {
    const response = await axios.post('http://localhost:5000/api/auth/register', {
      name, email, password
    });

    if (response.status !== 200) {
      return res.render('register', { title: 'Register', message: response.data.msg || 'Registration failed' });
    }

    res.redirect('/login');
  } catch (error) {
    console.error(error);
    res.render('register', { title: 'Register', message: 'Server error' });
  }
});

// New routes
app.get('/teachers/search', (req, res) => {
  res.render('teachers_search', { title: 'Search Teachers' });
});

app.get('/teachers/list', (req, res) => {
  res.render('teachers_list', { title: 'List of Teachers' });
});

app.get('/uc/document', (req, res) => {
  res.render('uc_document', { title: 'UC Document' });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
