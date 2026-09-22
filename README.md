# Full-Stack AI Chatbot Application

A robust, containerized full-stack AI Chatbot application built using **FastAPI**, **Streamlit**, and **PostgreSQL**, fully orchestrated with **Docker Compose** and deployed on **AWS EC2**.

---

## Screenshots & Demo

<img width="1787" height="958" alt="Screenshot 2026-09-19 201645" src="https://github.com/user-attachments/assets/214c9afd-2212-4bc7-a6ef-2621164d4931" />

<img width="1757" height="893" alt="Screenshot 2026-09-19 201705" src="https://github.com/user-attachments/assets/73cd0701-8a1e-4301-9b59-8432923610bf" />

## Architecture & Project Structure

```text
AI chatbot/
├── __pycache__/           
├── myenv/                  
├── .env                   
├── .gitignore            
├── app.py                 
├── chatbot.py              
├── database.py             
├── docker-compose.yml    
├── Dockerfile              
├── Dockerfile.frontend     
└── requirements.txt        
```

### Tech Stack
* **Frontend:** Streamlit
* **Backend:** FastAPI, Python
* **Database:** PostgreSQL, SQLAlchemy ORM
* **Containerization:** Docker, Docker Compose
* **Cloud Platform:** AWS EC2 (Ubuntu Linux)

---

## Environment Variables Setup

Root directory me `.env` file banayein aur ye variables define karein:

```env
# Database Credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=chatbot_db
DB_HOST=postgres_db # Use 'localhost' when running without Docker locally
DB_PORT=5432

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Local Development (Using Docker Compose)

### 1. Repository Clone Karein:
```bash
git clone https://github.com/mursleenmohd/AI-Sassy-Chatbot.git
cd ai-chatbot
```

### 2. Environment File Set Karein:
```bash
cp .env.example .env 
```

### 3. Docker Containers Build & Run Karein:
```bash
docker compose up -d --build
```

### 4. Access Applications:
* **Streamlit Frontend:** http://localhost:8501
* **FastAPI Docs:** http://localhost:8000/docs
* **PostgreSQL Database:** localhost:5432

---

## Deployment on AWS EC2

### 1. AWS EC2 Instance Launch:
* **OS:** Ubuntu 22.04 LTS / 24.04 LTS
* **Instance Type:** t2.micro / t3.micro (Free Tier)
* **Security Group Inbound Ports Open:** 22 (SSH), 8000 (FastAPI), 8501 (Streamlit), 80 (HTTP).

### 2. Server Par Setup Commands:
```bash
# System Update & Tools Install
sudo apt update && sudo apt install -y docker.io docker-compose git

# Docker Permission Fix
sudo usermod -aG docker \$USER
newgrp docker

# Clone Repo & Run
git clone https://github.com/mursleenmohd/AI-Sassy-Chatbot.git
cd ai-chatbot
nano .env # Add your production environment variables

# Build and Start Containers
docker compose up -d --build
```

### 3. Live Access:
* **Streamlit UI:** http://65.1.107.198:8501
* **Backend API:** http://65.1.107.198:8000/docs
