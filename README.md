# AI SQL Agent with Streamlit 🤖📊

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)

An intelligent SQL agent that allows you to query a PostgreSQL database using natural language. Built with LangChain, Google Gemini, and Streamlit.

![Demo](demo.gif)

## 🚀 Overview

This project provides a user-friendly interface to interact with relational databases using plain English. It leverages the power of Large Language Models (LLMs) to translate natural language questions into valid SQL queries, executes them against a PostgreSQL database, and presents the results clearly.

## 🏗️ Project Structure

```text
.
├── database/           # Database files (ignored by git)
├── scripts/            # Utility scripts
│   └── setup_db.sh     # Automates database initialization
├── src/                # Application source code
│   └── app.py          # Streamlit application
├── docker-compose.yml  # Docker services configuration
├── requirements.txt    # Python dependencies
└── .gitignore          # Git ignore rules
```

## Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.8+](https://www.python.org/downloads/)
- [Docker & Docker Compose](https://www.docker.com/get-started)
- [Git](https://git-scm.com/downloads)

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-sql-streamlit
```

### 2. Set Up the Python Environment

It is recommended to use a virtual environment to manage dependencies:

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Install Dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file and add your `GOOGLE_API_KEY`. You can also customize the database credentials if needed.

### 4. Launch the Database

The database is powered by PostgreSQL running in Docker. The system is designed to automatically download the necessary initialization data if it's missing.

```bash
docker-compose up -d
```

*Note: The first time you run this, it will download the database schema and data automatically.*

### 5. Run the Application

Once the database is up and running, start the Streamlit interface:

```bash
streamlit run src/app.py
```

The application will be available at `http://localhost:8501`.

## ✨ Features

- **Natural Language to SQL**: Ask questions about your data in plain English.
- **SQL Preview**: See the generated SQL query before the results.
- **Context-Aware**: Remembers previous questions in the conversation.
- **Automated Data Retrieval**: Downloads and sets up the Chinook dataset automatically.
- **Interactive UI**: Clean and simple interface built with Streamlit.
- **Database Management**: Includes pgAdmin for manual exploration.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM Orchestration**: [LangChain](https://www.langchain.com/)
- **LLM**: [Google Gemini](https://ai.google.dev/)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose


## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🛠️ Development

To maintain code quality, this project uses `black`, `isort`, and `flake8`. Configuration for these tools is located in `pyproject.toml`.

### Install Development Dependencies:
```bash
pip install -r requirements-dev.txt
```

### Run Formatters and Linters:

- **Format code**:
  ```bash
  black .
  ```
- **Sort imports**:
  ```bash
  isort .
  ```
- **Lint code**:
  ```bash
  flake8 .
  ```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
