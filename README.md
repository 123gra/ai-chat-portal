# ai-chat-portal
# AI Chat Portal (Django + React + GPT)

This project allows users to create and manage chat conversations with an AI model.  
All conversations are stored in PostgreSQL, can be viewed later, and can be ended with automatically generated summaries.

---

## Features

- Start new chat sessions
- Store complete conversation history in PostgreSQL
- Resume previous chats
- End chat and generate auto-summary
- Clean and modern chat UI
- Backend powered by Django REST Framework
- Frontend built in React + Tailwind
- Works **locally** and in **GitHub Codespaces**

---

## Architecture Diagram
User (Browser)
|
v
Frontend (React + Tailwind)
|
v
Backend API (Django REST Framework)
|
v
PostgreSQL (Conversation + Messages)
|
v
OpenAI API (Text generation + Summaries)
## Tech Stack

| Layer       | Technology |
|------------|------------|
| Frontend   | React (Vite) + Tailwind CSS |
| Backend    | Django + Django REST Framework |
| AI Model   | OpenAI GPT |
| Database   | PostgreSQL |
| Deployment | Local & GitHub Codespaces |

---

##  Screenshots
/screenshots folder for screenshots

## Folder Structure
ai-chat-portal/
│
├─ README.md
├─ requirements.txt
│
├─ backend/
│ ├─ manage.py
│ ├─ chat/
│ ├─ users/
│ └─ ...
│
├─ frontend/
│ ├─ src/
│ └─ ...
│
├─ sample_conversations/
│ ├─ sample_data.json
│ └─ sample_data.sql
│
└─ screenshots/
├─ ui-home.png
├─ ui-chat.png
└─ ui-history.png


---

## Requirements

A **requirements.txt** is included in the root with all backend dependencies.

##  Sample Data

Located in `sample_conversations/`

##  Setup Instructions (Local)

### 1. Clone Repo
git clone https://github.com/123gra/ai-chat-portal.git
cd ai-chat-portal

### 2. Setup Backend
cd backend
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
### 3. Setup Frontend
cd ../frontend
npm install
npm run dev
##  Run in GitHub Codespaces

1. Open Codespace
2. Run backend:  
cd backend
python manage.py runserver 0.0.0.0:8000
3. Run frontend:
cd frontend
npm run dev -- --host
4. Go to **Ports Tab → Set both ports to Public**
5. Refresh UI to avoid CORS issues
##  API Documentation

OpenAPI / Swagger UI- mentioned in backend/chat_api/urls.py
Codespace: https://obscure-space-giggle-vjwxwwq9vvvhjqj-8000.app.github.dev/api/docs/
Local :http://127.0.0.1:8000/api/docs

