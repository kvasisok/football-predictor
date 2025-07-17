const express = require('express');
const app = express();

// Middleware для обработки ошибок
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Корневой маршрут
app.get('/', (req, res) => {
  try {
    res.send('Server is working');
  } catch (err) {
    console.error('Root route error:', err);
    res.status(500).send('Internal Error');
  }
});

// Обязательно для Vercel
module.exports = app;

// Локальный запуск
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => console.log(`Local: http://localhost:${PORT}`));
}
