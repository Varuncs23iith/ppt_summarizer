# PPT Summarizer

An AI-powered tool for analyzing and summarizing PowerPoint presentations and PDF documents. The system extracts slides from presentations, processes them through GPT-4o's vision model, and generates detailed summaries stored in a PostgreSQL database.

## Features

- **Multi-format Support**: Process PPT, PPTX, and PDF files
- **Automated Conversion**: Converts PowerPoint files to PDF, then to high-quality images
- **AI-Powered Analysis**: Uses OpenAI GPT-4o vision model for intelligent slide summarization
- **Detailed Extraction**:
  - Text transcription from slides
  - Image descriptions
  - Table extraction (converted to Markdown)
  - Mathematical formula transcription (LaTeX format)
- **Persistent Storage**: Stores all summaries and metadata in PostgreSQL
- **Async Architecture**: Fully asynchronous database operations for better performance

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**
- **Poetry** - Python dependency management tool
- **Docker & Docker Compose** - For PostgreSQL database
- **LibreOffice** - Required for PPT to PDF conversion
- **Poppler Utils** - Required for PDF to image conversion
- **OpenAI API Key** - Get one from OpenAI Platform

## Installation

### 1. Clone the Repository

Clone this repository to your local machine.

### 2. Install Python Dependencies

```bash
poetry install
```

This will install all required dependencies listed in pyproject.toml.

### 3. Set Up PostgreSQL Database

Start the PostgreSQL container using Docker Compose:

```bash
docker-compose up -d
```

This creates a PostgreSQL database with the following configuration:
- Database Name: ppt_database
- User: user
- Password: password
- Port: 5434 (host) to 5432 (container)

### 4. Initialize Database Schema

Run the database setup script to create the schema and tables:

```bash
poetry run python database/database_setup.py
```

This creates schema ppt_summarizer with tables: files, slide, summary

### 5. Configure Environment Variables

Create a .env file in the project root with your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Basic Usage

Run the main pipeline to process a PowerPoint presentation:

```bash
poetry run python pipeline/ppt_summarizer.py
```

By default, this processes data/CV_accelarator.pptx

## Dependencies

### Core Dependencies

- python (^3.11) - Programming language
- openai (^2.29.0) - OpenAI API client for GPT-4o
- pydantic (^2.12.5) - Data validation using Python type hints
- python-pptx (^1.0.2) - PowerPoint file processing
- pymupdf (^1.27.2.2) - PDF manipulation
- pdf2image (^1.17.0) - Convert PDF pages to images
- pillow (^12.1.1) - Image processing library
- sqlalchemy (^2.0.48) - SQL toolkit and ORM
- asyncpg (^0.31.0) - Async PostgreSQL driver
- psycopg2-binary (^2.9.11) - PostgreSQL adapter
- pyyaml (^6.0.3) - YAML parser for configuration
- jinja2 (^3.1.6) - Template engine
- python-box (^7.4.1) - Dict with attribute access

### System Dependencies

- LibreOffice: Used for converting PPT/PPTX files to PDF format
- Poppler: Required by pdf2image for PDF rendering

## Project Structure

```
capstone2/
├── pipeline/              # Main orchestration logic
├── tools/                 # Core processing utilities
├── orm/                   # SQLAlchemy ORM models
├── dto/                   # Pydantic data transfer objects
├── database/              # Database operations
├── llm_instructions/      # LLM prompt templates
├── config/                # Configuration files
├── data/                  # Input files and generated images
└── docker-compose.yaml    # PostgreSQL container setup
```

## How It Works

1. Input Processing: The system accepts PPT, PPTX, or PDF files
2. Conversion Pipeline:
   - PPT/PPTX files are converted to PDF using LibreOffice
   - PDF files are split into individual page images (PNG format, 200 DPI)
3. AI Analysis: Each slide image is:
   - Base64 encoded
   - Sent to GPT-4o vision model with specialized prompts
   - Analyzed for text, images, tables, and formulas
4. Data Storage:
   - File metadata stored in files table
   - Individual slide summaries stored in slide table
   - Aggregated summaries in summary table

## Database Schema

### ppt_summarizer.files
- file_id (PK): Auto-incrementing ID
- file_path: Path to the processed file
- file_extension: File extension (pdf, ppt, pptx)
- uploaded_at: Timestamp of file processing

### ppt_summarizer.slide
- slide_id (PK): Auto-incrementing ID
- file_id (FK): References files table
- slide_path: Path to the slide image
- slide_summary: AI-generated summary
- running_summary: Cumulative summary
- created_at: Timestamp

### ppt_summarizer.summary
- summary_id (PK): Auto-incrementing ID
- file_id (FK): References files table
- summary_text: Final aggregated summary
- created_at: Timestamp

## Configuration

### Database Connection

Default connection settings (defined in tools/database.py):
```
postgresql+asyncpg://user:password@localhost:5434/ppt_database
```

### LLM Prompts

Prompts are stored in YAML format in llm_instructions/. The system follows these rules:
- Summarize text content accurately
- Describe images in detail
- Preserve all numbers without manipulation
- Convert tables to Markdown format
- Transcribe mathematical formulas using LaTeX syntax

## Troubleshooting

### LibreOffice Not Found
Ensure LibreOffice is installed and soffice command is in your PATH

### Database Connection Failed
- Check if Docker container is running: docker-compose ps
- Verify port 5434 is not in use
- Restart container: docker-compose restart

### PDF to Image Conversion Error
Install poppler-utils (see Prerequisites section)

### OpenAI API Errors
- Verify your API key in .env file
- Check your OpenAI account balance and rate limits
- Ensure you have access to GPT-4o model

## Development

### Running with Poetry

Execute any Python script in the Poetry environment:
```bash
poetry run python <script_name>.py
```

### Database Management

Stop the database:
```bash
docker-compose down
```

Remove database volume (clean slate):
```bash
docker-compose down -v
```

View database logs:
```bash
docker-compose logs db
```
