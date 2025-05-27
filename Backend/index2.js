import Express from 'express';
import { exec } from 'child_process';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import cors from 'cors';
import dotenv from 'dotenv';
import './db/connection.js';  // Initialize database connection
import userRoutes from './routes/userRoutes.js';

dotenv.config();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = Express();
app.use(cors({
  origin: '*',  // Be more restrictive in production
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(Express.json());
const PORT = process.env.PORT || 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    const uploadPath = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadPath)) {
      fs.mkdirSync(uploadPath, { recursive: true });
    }
    cb(null, uploadPath);
  },
  filename: function(req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    // Accept only image files
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

// Mount user routes
app.use('/api', userRoutes);

app.get('/', (req, res) => {
  res.send('Hello World!');
});

// Endpoint to analyze skin tone
app.post('/analyze-skin-tone', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No image file provided' });
  }

  // Path to the uploaded file
  const imagePath = req.file.path;
  
  // Path to the Python script
  const scriptPath = path.join(__dirname, 'Python_Scripts', 'Face_Skin_Tone.py');
  
  // Execute Python script with the image path as an argument
  exec(`python "${scriptPath}" "${imagePath}"`, (error, stdout, stderr) => {
    // Delete the uploaded file after processing
    fs.unlink(imagePath, (err) => {
      if (err) console.error(`Error deleting file: ${err}`);
    });

    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return res.status(500).json({ error: 'Failed to analyze image' });
    }
    
    if (stderr) {
      console.error(`Python script stderr: ${stderr}`);
    }
    
    try {
      // Try to parse the output as JSON
      const results = JSON.parse(stdout);
      res.json(results);
    } catch (e) {
      console.error(`Failed to parse Python output: ${e.message}`);
      res.status(500).json({ 
        error: 'Failed to parse analysis results',
        raw: stdout 
      });
    }
  });
});

// Update user skin tone endpoint
app.post('/update-user-skin-tone/:id', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No image file provided' });
  }

  try {
    const userId = req.params.id;
    const imagePath = req.file.path;
    const scriptPath = path.join(__dirname, 'Python_Scripts', 'Face_Skin_Tone.py');
    
    exec(`python "${scriptPath}" "${imagePath}"`, async (error, stdout, stderr) => {
      // Delete the uploaded file after processing (privacy protection)
      fs.unlink(imagePath, (err) => {
        if (err) console.error(`Error deleting file: ${err}`);
      });

      if (error) {
        console.error(`Error executing Python script: ${error.message}`);
        return res.status(500).json({ error: 'Failed to analyze image' });
      }
      
      try {
        // Parse the Python script output
        const results = JSON.parse(stdout);
        
        if (results.faces && results.faces.length > 0) {
          const faceData = results.faces[0]; // Use the first detected face
          
          // Find and update the user
          const user = await User.findById(userId);
          if (!user) {
            return res.status(404).json({ error: 'User not found' });
          }
          
          // Update the user's fashion data with skin tone information
          user.fashion_data = {
            ...user.fashion_data,
            skin_tone: faceData.skin_tone,
            undertone: faceData.undertone
          };
          
          await user.save();
          
          // Return the updated user
          res.json(user);
        } else {
          res.status(400).json({ error: 'No face detected in the image' });
        }
      } catch (e) {
        console.error(`Failed to parse Python output: ${e.message}`);
        res.status(500).json({ error: 'Failed to parse analysis results' });
      }
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});