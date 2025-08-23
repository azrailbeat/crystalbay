const app = require('./app');
const { initializeDatabase } = require('./models');

const PORT = process.env.PORT || 5000;

async function startServer() {
    try {
        // Initialize database connection
        await initializeDatabase();
        console.log('Database connection established');

        // Start server
        app.listen(PORT, '0.0.0.0', () => {
            console.log(`Crystal Bay Travel server running on port ${PORT}`);
            console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});

startServer();