# 🚀 Job Finder AI Agent 🚀

A powerful, intelligent job matching and recommendation system that automatically fetches jobs from multiple sources, parses resumes, and provides personalized job recommendations with advanced scoring algorithms.

This project combines rule-based matching with semantic similarity using BERT to deliver highly accurate job-candidate compatibility scores. Perfect for job seekers, recruiters, and HR professionals looking to streamline the job matching process.

---

## ✨ Features

### 🔍 **Multi-Source Job Ingestion**
- **Remotive.io Integration**: Fetches remote jobs with real-time API integration
- **Adzuna Integration**: Comprehensive job database with global coverage
- **Concurrent Processing**: Simultaneous job fetching from multiple sources
- **Automatic Deduplication**: Smart duplicate detection and removal
- **Configurable Limits**: Control job volume per source and query

### 📄 **Universal Resume Parser**
- **PDF Processing**: Extracts structured data from PDF resumes using `pdfplumber`
- **Universal Format Support**: Works with any resume format and structure
- **Comprehensive Extraction**: 
  - Personal information (name, contact details, LinkedIn)
  - Skills and technologies
  - Work experience with duration calculation
  - Education and certifications
  - Projects with technologies used
  - Professional summary
- **Robust Error Handling**: Graceful fallbacks for missing or malformed data

### 🧠 **Advanced Matching & Scoring**
- **Hybrid Scoring System**: Combines rule-based logic with semantic similarity
- **Semantic Analysis**: Uses Sentence-BERT for deep semantic understanding
- **Rule-Based Matching**: Skills, experience, education, location, and title alignment
- **Intelligent Weighting**: Balanced scoring across multiple factors
- **Real-time Scoring**: Instant compatibility scores for all jobs

### 💾 **Smart Data Management**
- **JSON Storage**: Persistent job and resume data storage
- **Metadata Tracking**: Comprehensive logging of fetch times, sources, and statistics
- **Backup System**: Automatic backup creation before updates
- **Storage Analytics**: Detailed statistics and performance metrics

### 🔧 **Modular Architecture**
- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **Provider Abstraction**: Easy to add new job sources
- **Pipeline Architecture**: Clean separation of concerns
- **Extensible Design**: Simple to extend with new features

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Job Sources   │    │  Resume Input   │    │   FastAPI App   │
│                 │    │                 │    │                 │
│ • Remotive.io   │    │ • PDF Upload    │    │ • REST API      │
│ • Adzuna        │    │ • Universal     │    │ • WebSocket     │
│ • Extensible    │    │ • Parser        │    │ • Documentation │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Processing Engine                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Job Ingestion│  │Resume Parser│  │   Scoring   │            │
│  │   Pipeline   │  │   Engine    │  │   System    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                │                │                    │
│         ▼                ▼                ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Normalization│  │Text Extraction│  │Rule-Based  │            │
│  │ & Deduplication│  │& Structuring │  │  Scoring   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                │                │                    │
│         ▼                ▼                ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Storage    │  │   Storage    │  │Semantic     │            │
│  │   Engine     │  │   Engine     │  │  Scoring    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Jobs JSON  │  │ Resume JSON │  │  Metadata   │            │
│  │   Storage    │  │   Storage   │  │   Storage   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Job Ingestion**: Multiple sources → Normalization → Deduplication → Storage
2. **Resume Processing**: PDF Upload → Text Extraction → Structured Data → Storage  
3. **Matching Engine**: Jobs + Resume → Rule-based Scoring → Semantic Analysis → Combined Score
4. **Results**: Ranked job recommendations with compatibility scores

---

## 🛠️ Technology Stack

| Category | Technology / Service | Purpose |
|----------|---------------------|---------|
| **Backend Framework** | FastAPI | Modern, fast web API with automatic documentation |
| **Job Sources** | Remotive.io, Adzuna | Multi-source job data ingestion |
| **Resume Processing** | pdfplumber | PDF text extraction and parsing |
| **Semantic Analysis** | Sentence-BERT | Deep semantic similarity computation |
| **Data Storage** | JSON Files | Persistent, structured data storage |
| **HTTP Client** | aiohttp | Asynchronous API requests |
| **Data Validation** | Pydantic | Type-safe data models and validation |
| **Environment Management** | python-dotenv | Secure configuration management |
| **NLP Processing** | spaCy | Named entity recognition and text processing |

---

## 📁 Project Structure

```
job-finder-ai-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # Pydantic data models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── jobs.py             # API routes
│   ├── services/
│   │   ├── __init__.py
│   │   └── job_service.py      # Business logic
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py               # Database configuration
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── remotive_client.py  # Remotive.io API client
│   │   └── adzuna_client.py    # Adzuna API client
│   ├── pipelines/
│   │   ├── __init__.py
│   │   └── job_ingestor.py     # Job ingestion pipeline
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── job_storage.py      # Job data persistence
│   │   ├── resume_parser.py    # Resume parsing engine
│   │   └── match_scoring.py    # Rule-based scoring
│   └── scoring/
│       ├── __init__.py
│       └── semantic_matcher.py # Semantic similarity scoring
├── scripts/
│   ├── fetch_and_store_jobs.py # Job ingestion script
│   └── test_semantic_match.py  # Semantic matching tests
├── data/
│   ├── fetched_jobs.json       # Stored job data
│   └── parsed_resume.json      # Parsed resume data
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- API keys for job sources (optional for testing)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd job-finder-ai-agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Job Source API Keys (Optional - system works without them)
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_API_KEY=your_adzuna_api_key

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

### 5. Start the Application

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run job ingestion script
python scripts/fetch_and_store_jobs.py "python developer, data scientist" 10
```

---

## 🚀 Usage

### Job Ingestion

```bash
# Fetch jobs for multiple titles
python scripts/fetch_and_store_jobs.py "python developer, data scientist, ai engineer" 20

# Parameters:
# - Job titles (comma-separated)
# - Limit per source (default: 10)
```

### Resume Parsing

```bash
# Parse a resume PDF
python app/utils/resume_parser.py path/to/resume.pdf
```

### Semantic Similarity Testing

```bash
# Test semantic matching
python scripts/test_semantic_match.py
```

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get jobs
curl http://localhost:8000/jobs/

# Search jobs (to be implemented)
curl http://localhost:8000/jobs/search
```

---

## 🔍 Job Matching Algorithm

### Scoring Components

1. **Skills Match (35%)**: Direct and mapped skill alignment
2. **Experience Level (25%)**: Job level vs. candidate experience
3. **Education Match (15%)**: Degree requirements alignment
4. **Location Match (10%)**: Geographic compatibility
5. **Title Match (10%)**: Job title relevance
6. **Salary Expectations (5%)**: Basic salary compatibility

### Semantic Analysis

- **Sentence-BERT Integration**: Deep semantic understanding using `all-MiniLM-L6-v2`
- **Fallback System**: Keyword-based similarity when BERT unavailable
- **Text Extraction**: Intelligent extraction of relevant content from resumes and jobs
- **Cosine Similarity**: Mathematical similarity computation

### Final Score Calculation

The system combines rule-based scoring with semantic similarity using weighted algorithms to produce a final compatibility score (0-100%).

---

## 📊 Data Models

### Job Model
```python
class Job(BaseModel):
    id: str
    title: str
    company_name: str
    location: str
    description: str
    salary_range: Optional[str]
    required_skills: List[str]
    source_platform: Literal["remotive", "adzuna", "other"]
    posted_date: datetime
    url: str
    match_score: Optional[float]  # Added by scoring system
```

### Resume Model
```python
class ResumeData:
    full_name: str
    email: str
    phone: str
    linkedin: str
    location: str
    skills: List[str]
    experience: List[Dict]
    education: List[Dict]
    certifications: List[Dict]
    projects: List[Dict]
    summary: str
    years_of_experience: int
    current_position: str
```

---

## 🔧 Configuration

### Job Sources

- **Remotive.io**: Remote job platform with comprehensive API
- **Adzuna**: Global job search engine with rich metadata
- **Extensible**: Easy to add new sources via provider pattern

### Storage Options

- **JSON Files**: Simple, portable data storage
- **Metadata Tracking**: Comprehensive logging and statistics
- **Backup System**: Automatic backup creation

### Scoring Weights

Configurable weights for different scoring factors to customize matching behavior.

---

## 🗺️ Roadmap

### Planned Features

- **Database Integration**: PostgreSQL/MongoDB for production use
- **User Authentication**: Multi-user support with profiles
- **Email Notifications**: Job alerts and recommendations
- **Cover Letter Generation**: AI-powered cover letter creation
- **Interview Preparation**: Personalized interview guidance
- **Analytics Dashboard**: Job search insights and trends
- **Mobile App**: React Native mobile application
- **API Rate Limiting**: Production-ready API management

### Advanced Features

- **Machine Learning**: Predictive job matching using historical data
- **Salary Analysis**: Market rate analysis and negotiation insights
- **Company Research**: Automated company background research
- **Skill Gap Analysis**: Personalized skill development recommendations

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Remotive.io** for providing excellent remote job data
- **Adzuna** for comprehensive job search API
- **Sentence-BERT** for semantic similarity capabilities
- **FastAPI** for the excellent web framework
- **pdfplumber** for robust PDF processing

---

## 📞 Support

For support, email support@jobfinder-ai.com or create an issue in the repository.

---

**Built with ❤️ for the job search community**
