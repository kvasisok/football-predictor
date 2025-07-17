const express = require('express');
const app = express();

// Test route
app.get('/', (req, res) => {
    res.send('Vercel Express Server is Running!');
});

module.exports = app;
