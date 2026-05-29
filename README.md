# PPT Summarizer

An AI-powered tool that analyzes PowerPoint presentations and PDF documents, generating comprehensive slide-by-slide summaries and professional PDF reports. Uses OpenAI's GPT-4o vision model to extract insights, explain mathematical equations, and create detailed executive summaries.

## Features

- **Multi-format Support**: Process PPT, PPTX, and PDF files
- **AI-Powered Analysis**: GPT-4o vision model for intelligent summarization
- **Comprehensive Summaries**: 10-15 sentence detailed summaries per slide
- **Mathematical Equations**: Preserves and explains formulas in LaTeX format
- **Executive Summary**: 400-500 word professional overview of entire presentation
- **PDF Reports**: Clean, professional PDF with slide summaries and executive summary
- **REST API**: FastAPI-based API with interactive documentation
- **Gamma Integration**: Generate beautiful Gamma presentation decks
- **Multi-Deck Support**: Automatically handles presentations > 10 slides by splitting and combining
- **Docker Support**: Fully containerized deployment

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url>
cd capstone2
poetry install

# 2. Configure environment
cp .env.example .env
# Edit .env and add your API keys

# 3. Start services
docker-compose up -d

# 4. Access API
curl http://localhost:8000/
# Or visit http://localhost:8000/docs for interactive documentation
```

## Table of Contents

- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Setup Guide](#setup-guide)
  - [1. Python Dependencies](#1-python-dependencies)
  - [2. LibreOffice Installation](#2-libreoffice-installation)
  - [3. Database Setup](#3-database-setup)
  - [4. API Keys Configuration](#4-api-keys-configuration)
- [Running the Project](#running-the-project)
  - [Option 1: Docker (Recommended)](#option-1-docker-recommended)
  - [Option 2: Python Directly](#option-2-python-directly)
- [API Usage](#api-usage)
  - [Endpoints](#endpoints)
  - [Example API Calls](#example-api-calls)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)

## Repository Structure

```
capstone2/
├── api.py                          # API server entry point
├── controller.py                   # FastAPI endpoints and business logic
├── pipeline/                       # Main processing pipelines
│   ├── ppt_summarizer.py          # Slide analysis pipeline
│   └── generate_gamma_presentation.py  # Gamma deck generation
├── tools/                          # Core utilities
│   ├── client.py                  # OpenAI client initialization
│   ├── extract_metadata.py        # File processing and conversion
│   ├── create_file_summary.py     # Slide summarization logic
│   ├── gamma_api.py               # Gamma API integration
│   ├── database.py                # Database connection
│   └── prepare_config.py          # Configuration management
├── orm/                            # SQLAlchemy ORM models
│   ├── files.py                   # File metadata model
│   ├── slide.py                   # Slide data model
│   └── slide_improvement.py       # Improvement suggestions model
├── dto/                            # Pydantic data transfer objects
│   ├── file.py
│   ├── slide.py
│   └── slide_improvement.py
├── database/                       # Database operations
│   ├── database_setup.py          # Schema initialization
│   └── database_operations.py     # CRUD operations
├── llm_instructions/               # LLM prompt templates
│   └── slide_analysis.yaml        # Comprehensive analysis prompts
├── config/                         # Configuration files
├── data/                           # Input files and generated outputs
│   ├── *.pptx                     # Input presentations
│   ├── *.pdf                      # Converted PDFs
│   ├── *_page_*.png               # Extracted slide images
│   └── summary_report_*.pdf       # Generated PDF reports
├── docker-compose.yaml             # Docker orchestration
├── Dockerfile                      # Application container
├── pyproject.toml                  # Python dependencies
├── .env.example                    # Environment variables template
└── .env                            # Your API keys (DO NOT COMMIT)
```

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11 or higher**
- **Poetry** - Python dependency management ([Install Poetry](https://python-poetry.org/docs/#installation))
- **Docker Desktop** - For database and containerized deployment ([Install Docker](https://www.docker.com/products/docker-desktop))
- **LibreOffice** - For PPT to PDF conversion (see setup below)
- **Poppler Utils** - For PDF to image conversion (included in Docker)
- **OpenAI API Key** - Required ([Get API Key](https://platform.openai.com/api-keys))
- **Gamma API Key** - Optional, for Gamma deck generation ([Get API Key](https://gamma.app/))

## Setup Guide

### 1. Python Dependencies

Install Python dependencies using Poetry:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

This installs all required packages including:
- FastAPI, Uvicorn (API server)
- OpenAI (GPT-4o integration)
- SQLAlchemy, AsyncPG (database)
- ReportLab (PDF generation)
- PyMuPDF, pdf2image (file processing)

### 2. LibreOffice Installation

LibreOffice is required to convert PowerPoint files to PDF format.

#### Windows

1. Download LibreOffice from https://www.libreoffice.org/download/download/
2. Run the installer (LibreOffice_X.X.X_Win_x64.msi)
3. Follow installation wizard with default settings
4. Verify installation:
   ```bash
   soffice --version
   ```
5. If command not found, add to PATH:
   - Default location: `C:\Program Files\LibreOffice\program`
   - Add to System Environment Variables → Path
   - Restart terminal

#### macOS

```bash
# Install using Homebrew
brew install --cask libreoffice

# Verify installation
soffice --version
```

#### Linux (Ubuntu/Debian)

```bash
# Install LibreOffice
sudo apt-get update
sudo apt-get install -y libreoffice

# Verify installation
soffice --version
```

#### Docker

If using Docker, LibreOffice is automatically included in the container. No manual installation needed.

### 3. Database Setup

Start PostgreSQL database using Docker:

```bash
# Start database container
docker-compose up -d db

# Wait for database to be ready (about 10 seconds)
docker-compose logs db

# Initialize database schema
poetry run python database/database_setup.py
```

This creates:
- Database: `ppt_database`
- Schema: `ppt_summarizer`
- Tables: `files`, `slide`, `slide_improvement`, `summary`

**Database Connection:**
- Host: `localhost`
- Port: `5434` (external) → `5432` (internal)
- User: `user`
- Password: `password`
- Database: `ppt_database`

### 4. API Keys Configuration

Create and configure your `.env` file:

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Add your API keys to `.env`:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Optional: Gamma API Key (for Gamma deck generation)
GAMMA_API_KEY=sk-gamma-your-gamma-api-key-here

# Optional: API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_LOG_LEVEL=info

# Database URL (default works with docker-compose)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5434/ppt_database
```

**IMPORTANT:**
- No spaces around the `=` sign
- Keep your `.env` file secure and never commit it to version control
- The `.env` file must be in the project root directory

**Verify your configuration:**

```bash
poetry run python test_env.py
```

Expected output:
```
[OK] OPENAI_API_KEY: sk-proj-FH...
[OK] GAMMA_API_KEY: sk-gamma-R...
[OK] OpenAI client initialized successfully
[OK] Gamma API key retrieved successfully
```

## Running the Project

### Option 1: Docker (Recommended)

Run the entire application stack with Docker:

```bash
# Start all services (database + API)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- **API**: http://localhost:8000
- **Database**: localhost:5434
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Option 2: Python Directly

Run the API server without Docker:

```bash
# Start database only
docker-compose up -d db

# Run API server
poetry run python api.py
```

The API will be available at http://localhost:8000

## API Usage

### Endpoints

The API provides the following endpoints:

#### 1. Health Check
```
GET /
```
Returns API status and version.

#### 2. Analyze Presentation (File Path)
```
POST /summarize
Content-Type: application/json

{
  "file_path": "/path/to/presentation.pptx"
}
```
Processes a presentation from file path and generates PDF summary.

#### 3. Upload and Analyze
```
POST /upload-and-summarize
Content-Type: multipart/form-data

file: <presentation-file>
```
Upload a presentation file and get analysis in one call.

#### 4. Download PDF Summary
```
GET /summarize/download/{file_id}
```
Download the generated PDF report for a specific file.

#### 5. Generate Gamma Deck
```
POST /generate-gamma
Content-Type: application/json

{
  "file_id": 1
}
```
Generate a Gamma presentation deck from analyzed slides.

**Note**: Automatically handles presentations > 10 slides by splitting into multiple decks and combining them. See [GAMMA_MULTI_DECK.md](GAMMA_MULTI_DECK.md) for details.

#### 6. Download Combined Gamma Presentation
```
GET /generate-gamma/download/{file_id}
```
Download the combined PPTX file (for presentations with > 10 slides).

### Example API Calls

#### Using cURL

**Health Check:**
```bash
curl http://localhost:8000/
```

**Upload and Analyze:**
```bash
curl -X POST http://localhost:8000/upload-and-summarize \
  -F "file=@data/presentation.pptx"
```

**Response:**
```json
{
  "file_id": 1,
  "pdf_path": "data/summary_report_1_20260529_123045.pdf",
  "total_slides": 15,
  "message": "Successfully analyzed 15 slides. PDF report generated."
}
```

**Download PDF:**
```bash
curl -O http://localhost:8000/summarize/download/1
```

**Generate Gamma Deck:**
```bash
curl -X POST http://localhost:8000/generate-gamma \
  -H "Content-Type: application/json" \
  -d '{"file_id": 1}'
```

**Response (≤10 slides):**
```json
{
  "file_id": 1,
  "gamma_url": "https://gamma.app/public/...",
  "export_url": "https://gamma.app/api/export/...",
  "message": "Successfully generated Gamma presentation with 8 slides."
}
```

**Response (>10 slides):**
```json
{
  "file_id": 2,
  "gamma_url": "https://gamma.app/public/...",
  "export_url": "https://gamma.app/api/export/...",
  "message": "Generated 2 Gamma decks and combined into single presentation",
  "combined_file_path": "data/gamma_combined_2_20260529_123045.pptx",
  "total_chunks": 2
}
```

**Download Combined Presentation (for >10 slides):**
```bash
curl -O http://localhost:8000/generate-gamma/download/2
```

#### Using Python Requests

```python
import requests

# Upload and analyze
with open('presentation.pptx', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload-and-summarize',
        files={'file': f}
    )
    result = response.json()
    print(f"File ID: {result['file_id']}")
    print(f"PDF: {result['pdf_path']}")

# Download PDF
file_id = result['file_id']
pdf_response = requests.get(f'http://localhost:8000/summarize/download/{file_id}')
with open(f'summary_{file_id}.pdf', 'wb') as f:
    f.write(pdf_response.content)
```

#### Using Interactive Documentation

Visit http://localhost:8000/docs for Swagger UI where you can:
- Try all endpoints interactively
- See request/response schemas
- Upload files directly from browser
- View detailed API documentation

## Output Files

All generated files are saved in the `data/` directory:

### Input Files
```
data/
├── presentation.pptx           # Your uploaded presentation
└── CV_accelarator.pptx         # Example presentation
```

### Intermediate Files
```
data/
├── presentation.pdf            # Converted PDF
└── presentation_page_1.png     # Extracted slide images
    presentation_page_2.png
    ...
```

### Output Files
```
data/
└── summary_report_1_20260529_123045.pdf   # Generated PDF report
```

### PDF Report Structure

The generated PDF report contains:

**Page 1: Title Page**
- Report title
- File ID and metadata
- Generation timestamp
- Total number of slides

**Pages 2-N: Slide Summaries (one per page)**
- Slide number header
- 10-15 sentence comprehensive summary
- Mathematical equations properly formatted
- Key insights and explanations

**Page N+1: Executive Summary**
- Professional 400-500 word overview
- All key findings and conclusions
- Important mathematical equations
- Comprehensive presentation insights

### Database Storage

All data is stored in PostgreSQL:

```sql
-- Files table
SELECT * FROM ppt_summarizer.files;
-- Contains: file_id, file_path, file_extension, uploaded_at

-- Slides table
SELECT * FROM ppt_summarizer.slide;
-- Contains: slide_id, file_id, slide_path, slide_transcription,
--           slide_summary, running_summary, created_at

-- Improvements table
SELECT * FROM ppt_summarizer.slide_improvement;
-- Contains: improvement_id, slide_id, scores, improvement_points
```

## Using Python Scripts Directly

You can also run the pipelines directly without the API:

### Analyze a Presentation

```bash
poetry run python pipeline/ppt_summarizer.py
```

Edit `pipeline/ppt_summarizer.py` to change the input file:
```python
test_file = Path("data/your-presentation.pptx")
```

### Generate Gamma Deck

```bash
poetry run python pipeline/generate_gamma_presentation.py <file_id>
```

Replace `<file_id>` with the file ID from the analysis step.

## Troubleshooting

### API Keys Not Loading

**Problem:** `OPENAI_API_KEY not found` error

**Solution:**
1. Verify `.env` file exists in project root
2. Check no spaces around `=` in .env:
   ```bash
   OPENAI_API_KEY=your-key    # Correct
   OPENAI_API_KEY = your-key  # Wrong
   ```
3. Run test: `poetry run python test_env.py`
4. Restart API server

### LibreOffice Not Found

**Problem:** `soffice command not found`

**Solution:**
1. Verify installation: `soffice --version`
2. Add to PATH (Windows):
   - Default: `C:\Program Files\LibreOffice\program`
   - Add to Environment Variables → Path
3. Restart terminal
4. Or use Docker (LibreOffice included)

### Database Connection Failed

**Problem:** Cannot connect to database

**Solution:**
```bash
# Check database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Verify port 5434 is not in use
netstat -an | grep 5434  # Linux/Mac
netstat -an | findstr 5434  # Windows
```

### PDF Generation Fails

**Problem:** PDF generation error

**Solution:**
1. Check `data/` directory exists and is writable
2. Verify all slides were processed (check database)
3. Check for special characters in summaries
4. View detailed error logs: `docker-compose logs api`

### Poppler Not Found (PDF to Image)

**Problem:** `pdf2image` error about poppler

**Solution:**
- **Windows:** Download poppler from https://github.com/oschwartz10612/poppler-windows/releases/
  - Extract and add `bin` folder to PATH
- **macOS:** `brew install poppler`
- **Linux:** `sudo apt-get install poppler-utils`
- **Docker:** Included automatically

### Out of Memory

**Problem:** Large presentations cause memory issues

**Solution:**
1. Process presentations with fewer slides
2. Increase Docker memory limit:
   ```yaml
   # docker-compose.yaml
   services:
     api:
       deploy:
         resources:
           limits:
             memory: 4G
   ```
3. Process slides in batches

## Performance Tips

- **First analysis takes longer** (~30 seconds per slide) due to GPT-4o API calls
- **Subsequent operations are fast** (database queries)
- **Use Docker** for consistent performance and easier deployment
- **Batch processing:** Process multiple presentations overnight
- **Cache results:** Results are stored in database for quick retrieval

## Additional Resources

- **Quick Start Guide:** [QUICK_START.md](QUICK_START.md)
- **Docker Setup:** [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **API Documentation:** http://localhost:8000/docs (when running)
- **Environment Setup:** [ENV_FIX_SUMMARY.md](ENV_FIX_SUMMARY.md)
- **Feature Improvements:** [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)
- **Examples:** [EXAMPLE_OUTPUT.md](EXAMPLE_OUTPUT.md)

## Development

### Run Tests

```bash
# Test environment variables
poetry run python test_env.py

# Test summary improvements
poetry run python test_summary_improvements.py

# Test API
poetry run python test_api.py
```

### Database Management

```bash
# Access database CLI
docker-compose exec db psql -U user -d ppt_database

# Backup database
docker-compose exec db pg_dump -U user ppt_database > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U user -d ppt_database
```

### View Logs

```bash
# All services
docker-compose logs -f

# API only
docker-compose logs -f api

# Database only
docker-compose logs -f db
```

## License

[Add your license here]

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review documentation in the repository
- Open an issue on GitHub

## Acknowledgments

- OpenAI GPT-4o for intelligent analysis
- Gamma for beautiful presentation generation
- FastAPI for excellent API framework
- LibreOffice for document conversion
