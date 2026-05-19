# Project: Text to SQL (FuseMachines Week 3)

## Overview
This project is a Text-to-SQL system that converts natural language questions into executable SQL queries and returns final answers from a database.

---

## Workflow Pipeline

User Question  
↓  
### Step 1: Query Decomposition (Current Task)
Break the user question into structured sub-questions or logical components.

↓  
### Step 2: SQL Generation
Convert each decomposed part into valid SQL queries.

↓  
### Step 3: SQL Execution (PostgreSQL)
Run the generated SQL queries on the PostgreSQL database and fetch results.

↓  
### Step 4: Error Handling + Retry (Agentic Component)
Detect SQL errors, fix them using LLM reasoning, and retry execution automatically.

↓  
## Final Answer
Return the final consolidated answer to the user.

---

## Key Features
- Natural language to SQL conversion
- Multi-step query decomposition
- PostgreSQL integration
- Self-correcting agent loop (retry on errors)
- Modular pipeline design

---

## Tech Stack
- Python
- OpenAI API / LLM (or Gemini optional)
- PostgreSQL
- LangChain (optional for agent design)

---

## Goal
To build an **agentic Text-to-SQL system** that can:
- Understand complex questions
- Break them into logical steps
- Generate correct SQL
- Automatically fix errors and retry execution
