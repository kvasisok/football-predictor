const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000; // Используем проверенный свободный порт

// Middleware
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Server Error');
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Сервер запущен на http://localhost:${PORT}`);
});
