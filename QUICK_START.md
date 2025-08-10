# Crystal Bay Travel - Quick Start Guide

## 🚀 3 Ways to Get Started

### Option 1: One-Line Installation (Python)
```bash
git clone https://github.com/azrailbeat/crystalbay.git && cd crystalbay && chmod +x start_python.sh && ./start_python.sh
```

### Option 2: One-Line Installation (Docker)
```bash
git clone https://github.com/azrailbeat/crystalbay.git && cd crystalbay && chmod +x start.sh && ./start.sh
```

### Option 3: Manual Setup
```bash
git clone https://github.com/azrailbeat/crystalbay.git
cd crystalbay
cp .env.example .env
# Edit .env with your settings
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## ⚡ What You Get

After installation, access:

- **🏠 Dashboard**: http://localhost:5000
- **🏨 Tour Booking**: http://localhost:5000/tours  
- **👥 Lead Management**: http://localhost:5000/leads
- **🔧 SAMO Testing**: http://localhost:5000/samo-testing
- **⚙️ Settings**: http://localhost:5000/unified-settings

## 🔑 Essential Configuration

### Minimum Setup (.env file)
```env
DATABASE_URL=postgresql://your-db-connection
SAMO_OAUTH_TOKEN=your-samo-token
OPENAI_API_KEY=your-openai-key
FLASK_SECRET_KEY=your-secret-key
```

### Working Example (.env)
```env
DATABASE_URL=postgresql://neondb_owner:npg_Y4g4VaRYSjnv@ep-weathered-glade-a25ajc8n.eu-central-1.aws.neon.tech/neondb?sslmode=require
SAMO_OAUTH_TOKEN=27bd59a7ac67422189789f0188167379
OPENAI_API_KEY=sk-proj-your-key-here
FLASK_SECRET_KEY=crystal-bay-production-secret-2025
```

## 🎯 Get Your API Keys

### 1. Database (Neon DB - Free)
1. Go to [neon.tech](https://neon.tech)
2. Sign up and create project
3. Copy connection string

### 2. SAMO Travel API
1. Contact SAMO support
2. Request OAuth token
3. Ask for IP whitelisting

### 3. OpenAI API (Required for AI)
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create API key
3. Add to .env file

## ✅ Success Check

Your setup works when:
1. `curl http://localhost:5000/health` returns status "healthy"
2. Dashboard loads at http://localhost:5000
3. SAMO testing shows connection (even 403 is OK)

## 🔧 Troubleshooting

### Python Issues
```bash
# Install Python 3.11+
sudo apt install python3.11 python3.11-venv  # Ubuntu
brew install python@3.11                      # macOS

# Fix virtual environment
rm -rf venv && python3 -m venv venv && source venv/bin/activate
```

### Port Issues
```bash
# Kill existing process on port 5000
sudo lsof -i :5000
sudo kill -9 <PID>
```

### Database Issues  
```bash
# Test connection
psql $DATABASE_URL
# If fails, check DATABASE_URL format
```

## 🐳 Docker Alternative

If Python setup fails, use Docker:
```bash
docker-compose up -d
# Access: http://localhost:5000
```

## 📋 System Requirements

**Minimum:**
- Python 3.11+
- 512 MB RAM  
- 1 GB storage
- Internet connection

**Recommended:**
- Ubuntu 22.04 LTS
- 2 GB RAM
- 10 GB SSD storage

---

**Need help?** Check the full [README.md](README.md) or [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions!