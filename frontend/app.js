const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

const API_URL = process.env.API_URL;
const FRONTEND_PORT = process.env.FRONTEND_PORT

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: "something went wrong" });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.json(response.data);
  } catch (err) {
    if (err.response && err.status === 404){
    res.status(404).json({ error: "Job not found" })};
    res.status(400).json({ error: "something went wrong" });
  }
});

app.listen(FRONTEND_PORT, () => {
  console.log('Frontend running on port 3000');
});
