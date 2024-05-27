const express = require('express');
const path = require('path');
const axios = require('axios'); // Add axios for HTTP requests

const app = express();

// Set Pug as the template engine
app.set('view engine', 'pug');
app.set('views', path.join(__dirname, 'views'));

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Body parser middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json()); // Add JSON parser middleware

// Define routes
app.get('/', (req, res) => {
  res.render('index', { title: 'EduSphere' });
});

app.get('/login', (req, res) => {
  res.render('login', { title: 'Login' });
});

app.post('/login', async (req, res) => {
  // Handle login logic here
  const { email, password } = req.body;
  try {
    const response = await axios.post('http://localhost:5000/api/auth/login', { email, password });
    // Store the token in the session or cookie
    // Redirect to a protected page or dashboard
    res.redirect('/dashboard'); // Modify this as per your app structure
  } catch (error) {
    res.render('login', { title: 'Login', error: 'Invalid credentials' });
  }
});

app.get('/register', (req, res) => {
  res.render('register', { title: 'Register' });
});

app.post('/register', async (req, res) => {
// Handle registration logic here
app.post('/register', async (req, res) => {
    const { name, email, password, confirmPassword } = req.body;
    
    if (password !== confirmPassword) {
      return res.render('register', { title: 'Register', message: 'Passwords do not match' });
    }
  
    try {
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });
  
      const data = await response.json();
      if (!response.ok) {
        return res.render('register', { title: 'Register', message: data.msg || 'Registration failed' });
      }
  
      res.redirect('/login');
    } catch (error) {
      console.error(error);
      res.render('register', { title: 'Register', message: 'Server error' });
    }
  });
  
});
