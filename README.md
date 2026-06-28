# ☁️ AWS Cost Optimizer — Powered by Groq AI

A full-stack web application that connects to your AWS account, scans your infrastructure, and uses **Groq AI** to deliver actionable cost-saving recommendations.

![Stack](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=flat-square&logo=react)
![Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Stack](https://img.shields.io/badge/AI-Groq-F55036?style=flat-square&logo=groq)
![Stack](https://img.shields.io/badge/Cloud-AWS-FF9900?style=flat-square&logo=amazonaws)

---

## ✨ Features

- 🔗 **AWS Account Connection** — securely connect using Access Key + Secret Key
- 🔍 **Infrastructure Scanner** — scans EC2, EBS, RDS, and S3 resources
- 💰 **Cost Analysis** — fetches real monthly spend via AWS Cost Explorer
- 🤖 **Groq AI Recommendations** — ultra-fast analysis with estimated savings per issue
- 💬 **AI Chat Assistant** — ask anything about your AWS costs in natural language
- 📊 **Animated Dashboard** — live charts, stat cards, and recommendation list
- 🐳 **Docker Support** — run the full stack with one command

---

## 🖥️ Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | React 19, Vite, Recharts          |
| Backend  | FastAPI, Python 3.12, Uvicorn     |
| AI       | Groq API (LLaMA 3)                |
| Cloud    | AWS boto3 (EC2, EBS, RDS, S3, CE) |
| Infra    | Docker, Docker Compose, Terraform |

---

## 📁 Project Structure

```
aws-cost-optimizer/
├── backend/
│   ├── main.py                  # FastAPI app & all routes
│   ├── requirements.txt
│   ├── .env.example
│   └── services/
│       ├── ai_service.py        # Groq AI integration
│       ├── aws_service.py       # AWS boto3 calls
│       └── optimizer.py         # Cost rule engine
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── ConnectPage.jsx  # AWS credentials form
│       │   ├── DashboardPage.jsx# Charts + recommendations
│       │   └── ChatPage.jsx     # AI chat interface
│       ├── components/
│       │   └── Navbar.jsx
│       └── App.css              # Animated dark theme
├── docker-compose.yml
└── infra/
    └── main.tf                  # Terraform config
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key → [console.groq.com/keys](https://console.groq.com/keys)
- AWS IAM user with read-only permissions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/aws-cost-optimizer.git
cd aws-cost-optimizer
```

### 2. Backend setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Groq API key
```

Start backend:
```bash
python -m uvicorn main:app --reload --port 8000
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

---

## 🐳 Docker (run everything at once)

```bash
export GROQ_API_KEY=your_key_here   # Windows: set GROQ_API_KEY=your_key_here
docker-compose up --build
```

Open **http://localhost**

---

## 🔐 AWS IAM Permissions Required

Create a read-only IAM user with this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeRegions",
        "rds:DescribeDBInstances",
        "s3:ListAllMyBuckets",
        "sts:GetCallerIdentity",
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🌐 API Endpoints

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| GET    | /health    | Health check                       |
| POST   | /connect   | Verify AWS credentials             |
| POST   | /scan      | Scan all AWS resources             |
| POST   | /analyze   | Groq AI cost analysis              |
| POST   | /chat      | Multi-turn AI chat                 |

---

## ⚙️ Environment Variables

```env
# backend/.env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 📸 Pages

| Page | Description |
|------|-------------|
| **Connect** | Enter AWS credentials to get started |
| **Dashboard** | View costs, resources, charts, and AI recommendations |
| **AI Chat** | Ask Groq AI anything about your AWS spending |

---

## 🔒 Security Notes

- AWS credentials are **never stored** — used only in memory for the session
- Always use a **read-only IAM policy** — the app never modifies your AWS resources
- Never commit your `.env` file — it is listed in `.gitignore`

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Built With

- [FastAPI](https://fastapi.tiangolo.com/)
- [Groq API](https://console.groq.com/)
- [React](https://react.dev/)
- [Recharts](https://recharts.org/)
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
