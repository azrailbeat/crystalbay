const { createClient } = require('@supabase/supabase-js');
const { Pool } = require('pg');

// Supabase client
let supabase = null;
let pgPool = null;

// In-memory fallback data stores
const memoryStorage = {
    leads: [],
    bookings: [],
    agents: [],
    settings: {
        samo_api: {
            api_url: 'https://booking.crystalbay.com/export/default.php',
            oauth_token: '27bd59a7ac67422189789f0188167379',
            timeout: 30,
            user_agent: 'Crystal Bay Travel Integration/1.0'
        }
    },
    leadInteractions: [],
    aiConfig: {
        model: 'gpt-4o',
        temperature: 0.2,
        active: true
    }
};

async function initializeDatabase() {
    try {
        // Initialize Supabase if credentials are available
        const supabaseUrl = process.env.SUPABASE_URL;
        const supabaseKey = process.env.SUPABASE_KEY;
        
        if (supabaseUrl && supabaseKey) {
            supabase = createClient(supabaseUrl, supabaseKey);
            console.log('Supabase client initialized successfully');
        } else {
            console.warn('SUPABASE_URL or SUPABASE_KEY not set. Using memory storage fallback.');
        }

        // Initialize PostgreSQL pool if DATABASE_URL is available
        if (process.env.DATABASE_URL) {
            pgPool = new Pool({
                connectionString: process.env.DATABASE_URL,
                ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
            });
            
            // Test connection
            const client = await pgPool.connect();
            await client.query('SELECT NOW()');
            client.release();
            console.log('PostgreSQL connection established');
        }
    } catch (error) {
        console.error('Database initialization failed:', error);
        console.warn('Using in-memory storage as fallback');
    }
}

function isSupabaseAvailable() {
    return supabase !== null;
}

function isDatabaseAvailable() {
    return pgPool !== null;
}

// Export database clients and utility functions
module.exports = {
    supabase,
    pgPool,
    memoryStorage,
    initializeDatabase,
    isSupabaseAvailable,
    isDatabaseAvailable
};