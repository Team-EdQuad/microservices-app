# 📁 EdQuad – Backend (FastAPI Microservices)

This is the **backend system** of the EdQuad Education Information Management & Decision Support System. It includes multiple FastAPI-based services connected through an API Gateway and powered by MongoDB.

> 💡 Supports student predictions, behaviour analysis, explainability, and full academic & non-academic tracking.

---

## 🧱 Services Overview

* `api-gateway` – Central router (port `8000`)
* `user-management` – Auth & user roles (`8001`)
* `academic` – Subjects, exams, assignments (`8002`)
* `non-academic` – Sports, clubs (`8003`)
* `attendance` – Attendance data (`8004`)
* `behavioural` – Behaviour recognition (`8005`)
* `dashboard` – ML, predictions, stats (`8006`)
* `calendar` – current and upcoming events (`8007`)

---

## 🔧 Manual Setup for Services (Example)

Repeat for each service below:

```bash
cd services/<service-name>

python -m venv venv
Set-ExecutionPolicy RemoteSigned -Scope Process
./venv/Scripts/Activate.ps1

pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port <port>
```

> Ensure all services run on ports 8001 to 8007. API Gateway should run on port 8000.

---

## 🐳 Docker Setup (Backend)

```bash
cd microservices-app/infrastructure

docker compose down
docker container prune -f
docker image prune -a -f

cd ..
git pull origin main

cd infrastructure
docker compose build --no-cache
docker compose up -d
```

---

## 👥 Sample Users

| Role    | Email                                                                   | Password    |
| ------- | ----------------------------------------------------------------------- | ----------- |
| Admin   | [admin@example.com](mailto:admin@example.com)                           | admin123    |
| Teacher | [amal@gmail.com](mailto:amal@gmail.com)                                 | amal123     |
| Student | [danielle.johnson82@example.com](mailto:danielle.johnson82@example.com) | danielle214 |

> 🔐 No signup. Admin creates all users.

---

## 💡 Tech Stack

* **Frontend**: ReactJS, MUI, JWT Auth
* **Backend**: FastAPI, MongoDB
* **AI/ML**: XGBoost, Scikit-learn, SHAP, Gemini LLM
* **Architecture**: Microservices + Docker

---

## 🔗 Frontend Repository

👉 [`EdQuad-Frontend`](https://github.com/Team-EdQuad//EdQuad-Frontend)

---

## ✅ System Summary

EdQuad is a modern, AI-powered education management platform offering:

* Advanced student analytics & insights
* Non-academic & behavioral monitoring
* Admin-first control and no public sign-up
* Modular, microservices-based backend

Together, the frontend and backend repos power a complete decision support system for schools and institutions.
