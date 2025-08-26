# RIC - Reflective Instruction Coach

## Overview

RIC (Reflective Instruction Coach) is an educational technology application that analyzes classroom teaching audio recordings to provide intelligent feedback to educators. The system uses advanced AI technologies including speech transcription, prosodic analysis, and GPT-4 powered educational feedback to help teachers improve their instructional delivery, clarity, and teaching techniques.

The application focuses on Spanish-language classroom analysis, providing comprehensive insights into teaching effectiveness through automated audio processing and AI-generated recommendations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Client-Side Framework**: Vanilla JavaScript with modern ES6+ features and Web Audio API
- **Styling**: Custom CSS with Bootstrap components and Feather icons
- **File Upload**: Drag-and-drop interface supporting multiple audio formats (MP3, WAV, M4A, OGG, FLAC)
- **Audio Recording**: Real-time microphone recording with Web Audio API, live timer, and playback preview
- **Real-time Updates**: Auto-refresh mechanism for processing status updates

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **File Processing**: Secure file upload handling with size limits (100MB max)
- **Audio Processing Pipeline**: Multi-stage analysis including transcription and prosodic analysis
- **AI Integration**: OpenAI GPT-4o for educational feedback generation
- **Database**: SQLite for development with PostgreSQL compatibility
- **Session Management**: Flask sessions with configurable secret keys

### Core Components

#### Audio Processing Module (`audio_processor.py`)
- **Transcription**: OpenAI Whisper API integration optimized for Spanish language
- **Prosodic Analysis**: Parselmouth (Praat) and librosa for speech pattern analysis
- **Educational Metrics**: Specialized calculations for filler word detection and speech quality

#### RIC AI Agent (`ric_agent.py`)
- **Model**: GPT-4o (latest OpenAI model as of May 2024)
- **Feedback Generation**: Structured JSON responses for educational recommendations
- **Educational Focus**: Specialized prompts for classroom instruction analysis

#### Data Models (`models.py`)
- **AudioAnalysis**: Primary entity storing upload metadata, transcription results, prosodic data, and AI feedback
- **JSON Storage**: Flexible schema using JSON columns for complex analysis data
- **Status Tracking**: Complete workflow state management (uploaded → processing → completed/error)

### Database Design
- **Primary Table**: AudioAnalysis with columns for file metadata, analysis results, and status tracking
- **JSON Fields**: Structured storage for transcription data, prosodic metrics, and AI feedback
- **Timestamp Tracking**: Upload and analysis completion timestamps
- **Error Handling**: Error message storage for failed analyses

### Processing Workflow
1. **File Upload**: Secure file handling with format validation
2. **Database Record Creation**: Initial record with 'uploaded' status
3. **Transcription Processing**: Whisper API call with Spanish optimization
4. **Prosodic Analysis**: Speech pattern analysis using Praat algorithms
5. **AI Feedback Generation**: GPT-4o analysis of educational effectiveness
6. **Status Updates**: Progressive status tracking throughout pipeline

## External Dependencies

### AI and Machine Learning Services
- **OpenAI API**: Whisper for transcription, GPT-4o for educational feedback
- **Parselmouth**: Python interface to Praat for prosodic analysis
- **librosa**: Audio signal processing and feature extraction

### Web Framework and Database
- **Flask**: Web application framework with SQLAlchemy ORM
- **SQLite**: Development database (PostgreSQL compatible)
- **Werkzeug**: WSGI utilities and secure filename handling

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Feather Icons**: Icon library for UI components
- **Chart.js**: Data visualization for analysis results

### Audio Processing Libraries
- **Praat**: Phonetic analysis software (via Parselmouth)
- **NumPy**: Numerical computing for audio signal processing

### Environment Configuration
- **Environment Variables**: OpenAI API key, database URL, session secrets
- **File Storage**: Local filesystem with configurable upload directory
- **Proxy Support**: ProxyFix middleware for deployment environments