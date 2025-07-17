const express = require('express');
const path = require('path');
const app = express();

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Test API endpoint
app.get('/api/status', (req, res) => {
    res.json({ 
        status: 'working',
        version: '1.0',
        timestamp: new Date().toISOString()
    });
});

// All other routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`API test endpoint: http://localhost:${PORT}/api/status`);
});

module.exports = app;
