# 🚆 AI-Powered Indian Railways Traffic Management System

An **AI-powered railway traffic management and simulation system** designed to assist railway operators in monitoring train movements, predicting operational issues, managing signals and platforms, detecting anomalies, and responding to railway incidents.

The system combines a **React-based railway dashboard**, **FastAPI backend**, and multiple **Machine Learning / Deep Learning modules** to provide real-time AI-assisted railway traffic management.

> **Note:** This project is an academic/research simulation and decision-support system. It is not intended for direct control of real-world railway infrastructure.

---

## 📌 Features

### 🚆 Railway Traffic Simulation

* Real-time train movement simulation
* Train position tracking
* Train speed monitoring
* Train delay tracking
* Train status monitoring
* Platform allocation
* Signal-controlled train movement
* Railway network visualization
* Live railway state monitoring

### 🚦 Intelligent Signal Control

AI-based signal recommendation using a **Deep Q-Network (DQN)**.

Supported signal states:

* 🔴 RED
* 🟡 DOUBLE YELLOW
* 🟡 YELLOW
* 🟢 GREEN

The AI recommends signal states based on the simulated railway traffic situation.

The AI recommendation does **not automatically override the operator's manual control**.

---

### ⏱️ Train Delay Prediction

Uses **XGBoost** to predict train delays based on railway operating conditions.

Model:

```text
XGBoost Regression
```

Reported evaluation:

* MAE: **1.72**
* RMSE: **2.14**
* R²: **0.883**

---

### ⚠️ Train Conflict Prediction

Uses a **Random Forest classifier** to identify possible conflicts between trains.

Model performance:

```text
Accuracy: 96.75%
```

The model evaluates factors such as:

* Train distance
* Train speed
* Time difference
* Relative train movement

---

### 🔍 Railway Anomaly Detection

Uses **Isolation Forest** to detect unusual railway traffic conditions.

The system can identify potential anomalies involving:

* Train speed
* Train distance
* Track occupancy
* Signal state
* Current delay
* Nearby train distance
* Station distance

Model:

```text
Isolation Forest
```

---

### 🔀 Incident-Driven Train Rerouting

AI-assisted rerouting is provided for actual railway incidents.

Supported incident scenarios include:

* Track failure
* Track blockage
* Signal failure
* Maintenance block
* Emergency / obstruction

The system **does not reroute trains simply because of high traffic or congestion**.

Rerouting considers conditions such as:

* Actual incident
* Route availability
* Alternative route availability
* Signal availability
* Conflict risk
* Operational restrictions

Model:

```text
Random Forest
```

---

### 🚉 Network-Level Congestion Prediction

Uses a **Graph Neural Network (GNN)** to analyze congestion across interconnected railway sections.

The railway network is represented as a graph containing:

* 12 railway nodes
* 12 railway connections
* 24 directed graph edges

Congestion classes:

```text
LOW
MEDIUM
HIGH
```

Model:

```text
Graph Convolutional Network (GCN)
```

Reported test accuracy:

```text
99.30%
```

---

### 📅 AI Timetable Optimization

Uses a **Genetic Algorithm** to optimize simulated railway timetable configurations.

The optimizer considers railway scheduling constraints and produces improved timetable arrangements.

---

### 🤖 AI Railway Assistant

The system includes a railway operations assistant that can answer railway-status-related questions using the current simulated railway state.

Example:

```text
What is the current railway status?
```

The assistant provides operational information from the simulator.

---

### 🚨 AI Incident Response & Recommendation

Provides AI-assisted recommendations when an operational issue occurs.

The system considers the current railway state, including:

* Train positions
* Train status
* Signal status
* Controlling signals
* Train delays
* Platform allocation

It produces recommendations intended to assist the operator in responding to incidents.

---

### 🎛️ Manual Override

A dedicated manual override system allows the operator to manually control the simulator.

The operator can:

* Change any signal
* Set signal status manually
* Move trains to platforms
* Override platform allocation
* Control railway operations independently of AI recommendations

Manual control is kept separate from AI decision-support functionality.

---

### 🛡️ Train Movement Safety Rule

A train is allowed to move only when its controlling signal is:

```text
YELLOW
DOUBLE YELLOW
GREEN
```

A train cannot move when its controlling signal is:

```text
RED
```

This rule is enforced by the railway simulation logic.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │      React Frontend     │
                    │     Railway Dashboard   │
                    └────────────┬────────────┘
                                 │
                                 │ HTTP / API
                                 ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │   Railway State Engine  │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌───────────┐      ┌───────────┐
        │ Delay AI  │      │ Signal AI  │      │ Conflict AI│
        └───────────┘      └───────────┘      └───────────┘
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌───────────┐      ┌───────────┐
        │ Anomaly AI│      │ Reroute AI │      │Congestion │
        │           │      │            │      │    GNN    │
        └───────────┘      └───────────┘      └───────────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Incident Response AI    │
                    │ Timetable Optimization  │
                    │ Railway AI Assistant    │
                    └─────────────────────────┘
```

---

# 🧠 AI Modules

| Module                 | Technique              | Purpose                            |
| ---------------------- | ---------------------- | ---------------------------------- |
| Delay Prediction       | XGBoost                | Predict train delays               |
| Signal Control         | Deep Q-Network         | Recommend signal states            |
| Conflict Prediction    | Random Forest          | Detect potential train conflicts   |
| Anomaly Detection      | Isolation Forest       | Detect unusual railway conditions  |
| Rerouting              | Random Forest + Rules  | Recommend incident-based rerouting |
| Congestion Prediction  | GNN / GCN              | Predict network congestion         |
| Timetable Optimization | Genetic Algorithm      | Optimize railway schedules         |
| Railway Assistant      | Rule-based AI          | Answer railway-status questions    |
| Incident Response      | Decision-support rules | Recommend responses to incidents   |

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS
* HTML

## Backend

* Python
* FastAPI
* Uvicorn

## Machine Learning

* Scikit-learn
* XGBoost
* PyTorch
* PyTorch Geometric
* Pandas
* NumPy

## AI Techniques

* XGBoost Regression
* Random Forest
* Isolation Forest
* Deep Q-Network
* Graph Convolutional Network
* Genetic Algorithm
* Rule-based decision support

---

# 📁 Project Structure

```text
railway-ai-1/
│
├── backend/
│   │
│   ├── anomaly_ai/
│   │   ├── data/
│   │   ├── model/
│   │   ├── generate_data.py
│   │   ├── train_model.py
│   │   └── anomaly_predictor.py
│   │
│   ├── conflict_ai/
│   │   ├── data/
│   │   ├── model/
│   │   ├── generate_data.py
│   │   ├── train_model.py
│   │   └── conflict_predictor.py
│   │
│   ├── congestion_ai/
│   │   ├── data/
│   │   ├── gnn_model.py
│   │   ├── train_model.py
│   │   └── congestion_predictor.py
│   │
│   ├── incident_response_ai/
│   │   └── incident_response.py
│   │
│   ├── reroute_ai/
│   │   ├── data/
│   │   ├── model/
│   │   ├── generate_data.py
│   │   ├── train_model.py
│   │   └── reroute_predictor.py
│   │
│   ├── railway_assistant/
│   │   └── ...
│   │
│   ├── signal_ai/
│   │   ├── environment.py
│   │   ├── dqn.py
│   │   ├── train_agent.py
│   │   └── signal_predictor.py
│   │
│   ├── timetable_ai/
│   │   └── ...
│   │
│   ├── data/
│   │   └── train_data.csv
│   │
│   ├── model/
│   │   └── delay_model.pkl
│   │
│   ├── railway_state.py
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
```

---

# 💻 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Indian-Railways-Traffic-Management-System.git
```

Move into the project:

```bash
cd AI-Indian-Railways-Traffic-Management-System
```

---

# 🐍 Backend Setup

Go to the backend:

```bash
cd backend
```

Install the required Python packages.

If a `requirements.txt` file is provided:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# ⚛️ Frontend Setup

Open another terminal.

Go to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🚦 Using the System

After starting both backend and frontend:

1. Open the frontend dashboard.
2. Monitor the railway network.
3. View train positions and statuses.
4. Monitor signal states.
5. View platform allocation.
6. View AI recommendations.
7. Use the AI modules for operational analysis.
8. Use Manual Override when manual intervention is required.
9. Start/stop the railway simulation.
10. Monitor incident-response recommendations.

---

# 🔌 Important API Endpoints

### Railway State

```text
GET /railway-state
```

Returns the current railway simulation state.

### Dashboard State

```text
GET /dashboard-live
```

Returns live dashboard information.

### Delay Prediction

```text
GET /ai-delay-live/{train_id}
```

### Signal AI

```text
GET /ai-signal-live/{train_id}
```

### Conflict AI

```text
GET /ai-conflict-live/{train_id}
```

### Anomaly AI

```text
GET /ai-anomaly-live/{train_id}
```

### Rerouting AI

```text
GET /ai-reroute-live/{train_id}
```

### Congestion AI

```text
GET /ai-congestion-live
```

### Railway Assistant

```text
POST /ai-assistant
```

### Incident Response

```text
POST /ai-incident-response
```

### Manual Signal Control

```text
POST /manual/signal
```

### Manual Platform Control

```text
POST /manual/platform
```

### Train Movement

```text
POST /train/move
```

### Simulation Control

```text
POST /simulation/start
POST /simulation/stop
POST /simulation/tick
```

---

# 📊 AI Model Results

The models were trained and tested on datasets generated for the railway simulation environment.

### Delay Prediction

```text
MAE  = 1.72
RMSE = 2.14
R²   = 0.883
```

### Conflict Prediction

```text
Accuracy = 96.75%
```

### Congestion Prediction

```text
Test Accuracy = 99.30%
```

### Anomaly Detection

```text
Dataset Size = 10,000
Anomalies    = 500
Anomaly Rate = 5%
```

### Rerouting

```text
Dataset Size = 15,000
Accuracy     = 98.37%
```

These results are based on the project's simulated/generated datasets and should not be interpreted as real-world railway operational performance.

---

# 🔐 Safety & Operational Philosophy

The system follows several important principles:

### AI is decision support

AI modules provide recommendations and predictions rather than directly controlling real railway infrastructure.

### Manual control is available

Operators can manually override signals and platform allocations within the simulator.

### Red signal prevents movement

The simulation prevents train movement when the controlling signal is RED.

### Rerouting requires an actual issue

The system does not treat congestion alone as a reason to reroute a train.

Rerouting is associated with incidents such as:

```text
Track Failure
Track Blockage
Signal Failure
Maintenance Block
Emergency / Obstruction
```

---

# 📚 Dataset Note

The machine-learning datasets used in this project are generated/simulated for the development and evaluation of the railway traffic management simulator.

They do not represent actual Indian Railways operational datasets.

Therefore, model accuracy values should be interpreted within the context of this simulation.

---

# 🎯 Project Objectives

The main objectives of the project are:

* Develop an AI-assisted railway traffic management system.
* Simulate railway traffic operations.
* Predict train delays.
* Detect potential train conflicts.
* Detect abnormal railway conditions.
* Predict railway network congestion.
* Recommend signals using reinforcement learning.
* Recommend rerouting during railway incidents.
* Optimize railway timetables.
* Provide incident-response recommendations.
* Provide a railway operations assistant.
* Provide manual operator control.
* Visualize railway operations through a real-time dashboard.

---

# 🚀 Future Improvements

Possible future development includes:

* Real railway infrastructure data integration
* Real-time GPS/railway positioning
* Advanced transformer-based railway forecasting
* Multi-agent reinforcement learning
* More detailed railway signaling simulation
* Automatic incident classification
* Explainable AI recommendations
* Historical traffic analytics
* Railway network map integration
* Role-based operator accounts
* Database-backed railway state
* Cloud deployment
* Advanced monitoring and logging

---

# 👨‍💻 Project

**AI-Powered Indian Railways Traffic Management System**

An AI-driven railway traffic simulation and decision-support platform combining machine learning, deep learning, graph neural networks, optimization algorithms, and a real-time railway operations dashboard.

---

## ⚠️ Disclaimer

This project is intended for **educational, research, demonstration, and simulation purposes**.

It is not certified or intended for direct use in controlling real-world railway signaling, train movement, railway infrastructure, or safety-critical railway operations.
