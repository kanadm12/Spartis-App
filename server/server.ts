import express from 'express';
import path from 'path';
import multer from 'multer'; // Import multer
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// --- New Multer Configuration ---
// This tells multer to store uploaded files in a directory called 'uploads'
const upload = multer({ dest: 'uploads/' });

// --- Your Existing Ping Endpoint ---
app.get('/api/ping', (req, res) => {
  res.send('pong from server');
});

// --- New File Upload Endpoint ---
// This endpoint will handle the POST request from your frontend
// 'upload.single('file')' is the middleware that processes the file
app.post('/api/process-nifti', upload.single('file'), (req, res) => {
  // req.file contains information about the uploaded file
  console.log('File received on backend:', req.file);

  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  // For now, we'll just send back a dummy file_id as the frontend expects
  const file_id = req.file.filename; 
  res.json({ message: 'File uploaded successfully!', file_id: file_id });
});


// --- Serves the React frontend's static files for production ---
app.use(express.static(path.join(__dirname, '..', 'dist')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});