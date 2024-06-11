const express = require('express');
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const { JSDOM } = require('jsdom');
const docxtemplater = require('docxtemplater');
const PizZip = require('pizzip');
const mammoth = require('mammoth');
const { Pool } = require('pg');
const { exec } = require('child_process');

const app = express();

const pool = new Pool({
  user: 'masteradmin',
  host: 'eduspheredb.c5km4ii2op0l.eu-west-3.rds.amazonaws.com',
  database: 'edusphereDB',
  password: 'adminadmin',
  port: 5432,  
});

// Pug
app.set('view engine', 'pug');
app.set('views', path.join(__dirname, 'views'));


app.use(express.static(path.join(__dirname, 'public')));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Routes
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

app.get('/teachers/search', (req, res) => {
  res.render('teachers_search', { title: 'Search Teachers' });
});


app.get('/teachers/add', (req, res) => {
  res.render('add_teacher', { title: 'Add Teacher' });
});


app.post('/teachers/add', (req, res) => {
  const cienciaID = req.body.ciencia_id;
  
  // Path to Python script
  const scriptPath = path.join(__dirname, 'scripts', 'scrape_and_insert.py');
  
  // Execute the Python script with the provided Ciencia ID
  exec(`python ${scriptPath} ${cienciaID}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing script: ${error.message}`);
      return res.status(500).render('add_teacher', { title: 'Add Teacher', error: `Error adding teacher: ${error.message}` });
    }
    if (stderr) {
      console.error(`Script stderr: ${stderr}`);
      return res.status(500).render('add_teacher', { title: 'Add Teacher', error: `Script error: ${stderr}` });
    }
    console.log(`Script stdout: ${stdout}`);
    res.render('add_teacher', { title: 'Add Teacher', success: 'Teacher added successfully' });
  });
});

// Teachers list
app.get('/teachers/list', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM teachers');
    const teachers = result.rows;
    res.render('teachers_list', { title: 'List of Teachers', teachers });
  } catch (error) {
    console.error('Error fetching teachers:', error);
    res.render('teachers_list', { title: 'List of Teachers', teachers: [] });
  }
});

app.get('/uc/document', (req, res) => {
  res.render('uc_document', { title: 'UC Document' });
});

app.post('/uc/document', (req, res) => {
  const formData = req.body;

  // Save the form data to a Word document
  const docTemplate = fs.readFileSync(path.resolve(__dirname, 'templates', 'document-template.docx'), 'binary');
  const zip = new PizZip(docTemplate);
  const doc = new docxtemplater(zip);

  doc.setData(formData);
  doc.render();

  const buf = doc.getZip().generate({ type: 'nodebuffer' });
  const wordFilePath = path.resolve(__dirname, 'output', 'document.docx');
  fs.writeFileSync(wordFilePath, buf);

  // Not working - PDF 
  const convertToPDF = async (inputPath, outputPath) => {
    try {
      const result = await mammoth.convertToHtml({ path: inputPath });
      const html = result.value;

      const { PDFDocument } = require('pdf-lib');
      const pdfDoc = await PDFDocument.create();
      const page = pdfDoc.addPage();
      page.drawText(html, {
        x: 50,
        y: page.getHeight() - 50,
        size: 12
      });

      const pdfBytes = await pdfDoc.save();
      fs.writeFileSync(outputPath, pdfBytes);
    } catch (err) {
      console.error('Error converting to PDF:', err);
    }
  };

  const pdfFilePath = path.resolve(__dirname, 'output', 'document.pdf');
  convertToPDF(wordFilePath, pdfFilePath);

  res.send('Form submitted successfully!');
});

// Route to handle AI prompts
app.post('/api/ai', async (req, res) => {
  const { prompt } = req.body;
  try {
    const response = await axios.post('http://localhost:8080/v1/chat/completions', {
      model: "lmstudio-ai/gemma-2b-it-GGUF",
      messages: [{ role: "user", content: prompt }]
    });
    res.json({ response: response.data.choices[0].message.content });
  } catch (error) {
    res.status(500).json({ error: 'Error generating AI response' });
  }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
