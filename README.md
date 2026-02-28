# Drop4Life: An Integrated Blood Donation and Emergency Alert System

![Drop4Life Logo](https://img.shields.io/badge/Drop4Life-Primary_Red-D32F2F?style=for-the-badge&logo=flask&logoColor=white)

**Drop4Life** is a smart, technology-driven blood donation platform designed to connect blood donors, recipients, and blood banks through a centralized digital system. It was developed as a B.Tech CSE Mini Project.

---

## 📚 Project Overview

Blood donation is a critical healthcare service, yet many regions face shortages due to poor coordination, a lack of real-time information, and delayed communication during emergencies.

This platform solves these problems by enabling users to:
* **Locate nearby blood banks** using an interactive, real-time map.
* **View real-time blood availability** and inventory at local hospitals.
* **Receive emergency alerts** when critical blood shortages happen in their area.
* **Earn rewards & social points** for frequent donations to gamify and encourage regular contributions.

---

## 🛠️ Zero-Cost Architecture & Tech Stack

A major constraint and goal of this project was to implement a **100% Zero-Cost Architecture** that required **NO credit cards** and **NO paid cloud services**. 

To achieve a premium, functional web application without incurring costs, we carefully selected free and open-source alternatives to standard enterprise tools:

### 1. Backend & Framework
* **Python & Flask:** Chosen over heavy frameworks like Django because Flask is lightweight, incredibly fast for routing, easy to set up on local machines for college demonstrations, and completely free.
* **Jinja2:** Built-in template engine for rendering dynamic HTML server-side.

### 2. Database Alternatives
* *Enterprise Standard:* AWS RDS, Google Cloud SQL (Requires Credit Card & Monthly Fees)
* **Our Solution: SQLite & SQLAlchemy** 
    * We used `SQLite` because it is a serverless database that stores all structured data locally in a single file (`drop4life.db`). 
    * It requires zero installation protocols, making the project highly portable when moving between laptops for university presentations.
    * We used `Flask-SQLAlchemy` as our ORM to interact with the database using Python objects securely.

### 3. Real-Time Maps & Location
* *Enterprise Standard:* Google Maps Platform API (Requires strict API Key monitoring and Credit Card).
* **Our Solution: Leaflet.js + OpenStreetMap**
    * We integrated `Leaflet.js`, an open-source JavaScript library for mobile-friendly interactive maps.
    * We paired this with completely free map tiles from `OpenStreetMap`, allowing us to plot hospital coordinates (e.g., in Hyderabad) dynamically without requesting any API credentials or worrying about rate limits during testing.

### 4. Emergency Alert System
* *Enterprise Standard:* Twilio SMS API / SendGrid (Paid services per message).
* **Our Solution: Python `smtplib` & Terminal Mocking**
    * For the scope of the demo, emergency broadcast alerts instantly trigger rich terminal logs.
    * The architecture is fully scaffolded using Python's built-in `smtplib`, allowing it to connect directly to a standard free Gmail account to send out emergency broadcast emails to all registered donors instantly.

### 5. Frontend UI/UX
* **Vanilla HTML/CSS/JS + Bootstrap 5:** To avoid complex build tools and npm configurations, we leveraged Bootstrap via CDN.
* **Premium CSS (Glassmorphism):** We built a custom `style.css` file utilizing modern CSS properties like `backdrop-filter` to create "Glassmorphism" (frosted glass) navigation bars and cards.
* **Typography:** Integrated Google Fonts (`Poppins`) to ensure the platform feels like a modern SaaS application.

---

## ⚙️ Features

* **Multi-Role Authentication:** Uses `Flask-Login` and `Flask-Bcrypt` to securely hash passwords and manage sessions for two separate user roles: **Donors** and **Hospitals**.
* **Donor Dashboard:** Tracks eligibility (calculating time since last donation), manages personal details, and displays a history of earned social points.
* **Hospital Dashboard:** Allows authorized medical personnel to update live blood inventory (A+, B-, O+, etc.) and post Emergency Alerts straight to the system.
* **Interactive Discovery:** The `/find_blood` page allows users to filter by blood group and see hospitals plotted instantly on the map.

---

## 🚀 Live Demo & Deployment
We have linked this project to **Vercel** for a live, serverless demonstration. 
👉 **Check out the live website:** [https://drop4-life.vercel.app/](https://drop4-life.vercel.app/)

---

## 💻 How to Run Locally

If you are a reviewer or a student setting this up for a local presentation:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Divvelasriram/Drop4Life.git
   cd Drop4Life
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize & Run the Application:**
   Because SQLite is used, the application will automatically create the local database file inside `/instance/` when you run it for the first time.
   ```bash
   python app.py
   ```

5. **View the App:**
   Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🎓 Academic Information

**B.Tech CSE(A) (2023–2027) - Batch 8 Mini Project**

Submitted to: Chaitanya (Deemed to be University)  
Under the guidance of: **Mrs. Taskeen Nasim**

**Developed By:**
* Nelluri Udaya Sri (23CSE1009)
* Sankineni Sujith Rao (23CSE1029)
* Ankit Jana (23CSE1036)
* Divvela Om Venkata Naga Sai Sri Ram (23CSE1039)
* Wangmayum Irshad (23CSE1061)
