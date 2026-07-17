import dotenv from 'dotenv';
import app from './app.js'; // Use .js extension since we use NodeNext module resolution

// Load environment variables
dotenv.config();

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`[server]: Server is running at http://localhost:${PORT}`);
});
