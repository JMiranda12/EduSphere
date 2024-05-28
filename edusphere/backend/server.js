const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const config = require('config');

// Create a new pool instance
const pool = new Pool({
  user: config.get('dbUser'),
  host: config.get('dbHost'),
  database: config.get('dbName'),
  password: config.get('dbPassword'),
  port: config.get('dbPort'),
});

const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// Routes
app.use('/api/auth', require('./routes/auth'));

// Route to get all teachers
app.get('/api/teachers', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM teachers');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});

app.get('/api/teachers/:id', async (req, res) => {
  const teacherId = req.params.id;

  try {
    const teacherResult = await pool.query('SELECT * FROM teachers WHERE id = $1', [teacherId]);
    const educationResult = await pool.query('SELECT * FROM education WHERE teacher_id = $1', [teacherId]);
    const publicationsResult = await pool.query('SELECT * FROM publications WHERE teacher_id = $1', [teacherId]);

    if (teacherResult.rows.length > 0) {
      const teacher = teacherResult.rows[0];
      teacher.education = educationResult.rows;
      teacher.publications = publicationsResult.rows;
      res.json(teacher);
    } else {
      res.status(404).json({ error: 'Teacher not found' });
    }
  } catch (error) {
    console.error('Error fetching teacher details:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
// Start the server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
