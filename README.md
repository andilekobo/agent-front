# CareerOps 🤖

CareerOps is an AI-powered career assistant that helps users search for jobs and get career guidance.

It combines a React frontend, FastAPI backend, Gemini, RAG with ChromaDB, and the Adzuna Job Search API.

## 🚀 What CareerOps Can Do

- Search for jobs based on role and location
- Extract job search information from natural language
- Retrieve relevant career knowledge using RAG
- Search live job listings through Adzuna
- Show job details such as:
  - Job title
  - Company
  - Location
  - Salary
  - Employment type
  - Matched skills
  - Application URL
- Generate natural-language career responses using Gemini

## 🧠 Architecture

```text
User
  ↓
React + Vite Frontend
  ↓
FastAPI Backend
  ↓
CareerOps Agent
  ├── RAG Retrieval
  │     ↓
  │   ChromaDB
  │
  ├── Gemini
  │     ↓
  │   Role + Location Extraction
  │
  └── Adzuna Job Search
        ↓
     Live Jobs
  ↓
Gemini Response
  ↓
Frontend
