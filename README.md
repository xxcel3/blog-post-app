# 📝 Flask Blog & Social App

A full-featured social blogging platform built with **Flask** and **MongoDB**, allowing users to post content, chat under posts, interact through likes, and take quizzes. It includes secure authentication, multimedia support, rate limiting, and a leaderboard — all containerized using Docker Compose.

---

## 📦 Features

- 🔐 **User Authentication** (bcrypt, auth tokens via cookies)  
- 📝 **Post Creation** with image/video upload support  
- 💬 **Chat under each post**, tied by post ID in MongoDB  
- 👍 **Like/Unlike System** with per-user like tracking  
- ⏱️ **Timed Quiz** with dynamic leaderboard  
- 📉 **IP-Based Rate Limiting**  
- 🧾 **Security Headers** (`X-Content-Type-Options: nosniff`)  
- 🗃️ **MongoDB** for users, posts, chats, and quiz state  
- 🐳 **Docker Compose** for easy setup and deployment  

---

## 🧰 Tech Stack

- **Backend**: Python + Flask  
- **Database**: MongoDB  
- **Frontend**: HTML, CSS, JavaScript  
- **Deployment**: Docker, Docker Compose  

---

## 🚀 How to Run Locally

### 🔧 1. Requirements

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

### ▶️ 2. Run the App

In the root project directory:

```bash
docker-compose up --build
```

This will:

- Start the Flask app on port `8080`
- Start MongoDB (via Docker) on `mongo:27017`

---

### 🌐 3. Open in Browser

Visit:

```
http://localhost:8080/
```

You can now:
- Register / Log in
- Create and browse posts
- Chat under posts
- Like/unlike content
- Take a quiz and view the leaderboard

---

## 🔒 Security Notes

- Passwords are hashed with **bcrypt**
- Auth tokens are stored securely via **HttpOnly** cookies
- Rate limiting is enforced **per IP address**
- Security headers included: `X-Content-Type-Options: nosniff`

---
