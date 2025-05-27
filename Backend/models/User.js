import mongoose from 'mongoose';

// Fashion data sub-schema
const fashionDataSchema = new mongoose.Schema({
  body_shape: { type: String, trim: true },
  skin_tone: { type: String, trim: true },
  undertone: { type: String, trim: true },
  personality_type: { type: String, trim: true },
  // Define other fashion-related fields as needed
}, { 
  strict: false, // This allows storing additional fields not defined in the schema
  _id: false // Don't create a separate ID for the subdocument
});

// Main user schema
const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
  age: {
    type: Number,
    min: 13, // Assuming minimum age requirement
    max: 120
  },
  fashion_data: {
    type: fashionDataSchema,
    default: {}
  }
}, {
  timestamps: true, // Adds createdAt and updatedAt fields
  strict: false // Allows for flexible schema expansion
});

// Create a model from the schema
const User = mongoose.model('User', userSchema);

export default User;