const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const rateLimit = require('express-rate-limit');
const path = require('path');
require('dotenv').config();

// Import routes
const mainRoutes = require('./routes/main');
const apiRoutes = require('./routes/api');
const messagesRoutes = require('./routes/messages');
const webhooksRoutes = require('./routes/webhooks');

const app = express();

// Security middleware
app.use(helmet({
    contentSecurityPolicy: false // Allow inline styles and scripts for compatibility
}));

// CORS
app.use(cors());

// Compression
app.use(compression());

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 1000, // limit each IP to 1000 requests per windowMs
    message: 'Too many requests from this IP, please try again later.'
});
app.use(limiter);

// Logging
app.use(morgan('combined'));

// Body parsing
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true, limit: '10mb' }));
app.use(cookieParser());

// Session configuration
app.use(session({
    secret: process.env.SESSION_SECRET || 'crystal-bay-travel-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: process.env.NODE_ENV === 'production',
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
}));

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Static files
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.use('/', mainRoutes);
app.use('/api', apiRoutes);
app.use('/api/messages', messagesRoutes);
app.use('/webhooks', webhooksRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(err.status || 500);
    res.render('error', {
        error: err.message || 'Internal server error',
        error_code: err.status || 500,
        active_page: 'error'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404);
    res.render('error', {
        error: 'Page not found',
        error_code: 404,
        active_page: 'error'
    });
});

module.exports = app;