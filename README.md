# 🚀 FastAPI CI/CD Lab

[![FastAPI CI/CD](https://github.com/Livesh28/fastapi-cicd-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Livesh28/fastapi-cicd-lab/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-containerized-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tested with Pytest](https://img.shields.io/badge/tested_with-pytest-0A9EDC.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Container Registry](https://img.shields.io/badge/GHCR-ghcr.io%2Flivesh28%2Ffastapi--cicd--lab-lightgrey?logo=github)](https://github.com/Livesh28/fastapi-cicd-lab/pkgs/container/fastapi-cicd-lab)
[![Deployment Target](https://img.shields.io/badge/Deploy-AWS%20EC2-FF9900.svg?logo=amazonec2&logoColor=white)](https://aws.amazon.com/ec2/)

A robust, enterprise-grade Continuous Integration and Continuous Deployment (CI/CD) pipeline for a **FastAPI** web service. This lab demonstrates automated testing, linting, containerization with **Docker**, artifact publication to **GitHub Container Registry (GHCR)**, and automated zero-downtime deployment to an **AWS EC2** instance with post-deployment health verification.

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
  - [CI/CD Pipeline Flow](#cicd-pipeline-flow)
  - [Pipeline Jobs Summary](#pipeline-jobs-summary)
- [Repository Structure](#-repository-structure)
- [API Endpoints](#-api-endpoints)
- [Local Development Setup](#-local-development-setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Quality Checks & Tests](#running-quality-checks--tests)
  - [Running the Local Server](#running-the-local-server)
- [Docker Containerization](#-docker-containerization)
  - [Build and Run Locally](#build-and-run-locally)
  - [Verify Local Container](#verify-local-container)
- [GitHub Actions CI/CD Pipeline Deep Dive](#-github-actions-cicd-pipeline-deep-dive)
  - [1. Test Job](#1-test-job)
  - [2. Lint Job](#2-lint-job)
  - [3. Build & Push Job](#3-build--push-job)
  - [4. Deploy Job](#4-deploy-job)
- [AWS EC2 Deployment Setup](#-aws-ec2-deployment-setup)
  - [1. EC2 Instance Configuration](#1-ec2-instance-configuration)
  - [2. Docker Installation on EC2](#2-docker-installation-on-ec2)
  - [3. GitHub Repository Secrets](#3-github-repository-secrets)
- [Rollback & Versioning Strategy](#-rollback--versioning-strategy)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [Future Enhancements & Production Roadmap](#-future-enhancements--production-roadmap)
- [License](#-license)

---

## 🏗 Overview & Architecture

This project exemplifies the DevOps lifecycle by converting code committed to the `main` branch into a validated, containerized service running on an AWS EC2 instance without manual intervention.

### CI/CD Pipeline Flow

```mermaid
flowchart TD
    A([Git Commit & Push to 'main']) --> B[GitHub Actions Triggered]
    
    subgraph CI ["Continuous Integration (Parallel Jobs)"]
        B --> C[Job: Test<br/>python -m pytest]
        B --> D[Job: Lint<br/>ruff check .]
    end

    C & D --> E[Job: Build & Push<br/>Docker Buildx]
    
    subgraph Registry ["Artifact Packaging"]
        E --> F["GHCR (GitHub Container Registry)<br/>ghcr.io/livesh28/fastapi-cicd-lab:latest<br/>ghcr.io/livesh28/fastapi-cicd-lab:<commit-sha>"]
    end

    subgraph CD ["Continuous Deployment (AWS EC2)"]
        F --> G["Job: Deploy (SSH to EC2 via appleboy/ssh-action)"]
        G --> H["1. Login to GHCR with GITHUB_TOKEN"]
        H --> I["2. Pull Exact Commit Image by SHA"]
        I --> J["3. Stop & Remove Old 'fastapi-lab' Container"]
        J --> K["4. Start New Container (--restart unless-stopped)"]
        K --> L["5. Automated Health Check (curl http://localhost:8000/health)"]
    end

    L --> M([Deployment Succeeded & Service Live 🎉])
```

### Pipeline Jobs Summary

| Job | Trigger / Dependency | Purpose | Key Tools |
| :--- | :--- | :--- | :--- |
| **`test`** | Push to `main` | Runs unit & integration test suite | `pytest`, `fastapi.testclient`, `httpx` |
| **`lint`** | Push to `main` | Validates code style, PEP 8 rules, and import order | `ruff` (configured via `pyproject.toml`) |
| **`build`** | Needs: `[test, lint]` | Builds multi-platform Docker container and publishes artifacts | `docker/build-push-action@v6`, `ghcr.io` |
| **`deploy`** | Needs: `build` | Deploys container to remote EC2 server and verifies health | `appleboy/ssh-action@v1.2.2`, `docker`, `curl` |

---

## 📁 Repository Structure

```text
fastapi-cicd-lab/
├── .github/
│   └── workflows/
│       └── ci.yml             # Complete 4-stage GitHub Actions CI/CD pipeline
├── app/
│   ├── __init__.py            # Python package declaration
│   └── main.py                # FastAPI application & endpoint definitions
├── tests/
│   ├── __init__.py            # Tests package initialization
│   └── test_main.py           # Automated test cases for root and health routes
├── Dockerfile                 # Minimal, reproducible production container definition
├── pyproject.toml             # Ruff linter and code formatter configurations
├── requirements.txt           # Pinned production and development dependencies
├── .gitignore                 # Excluded directories (.venv, cache, credentials)
└── README.md                  # Comprehensive project documentation
```

### Key Files at a Glance

- **`app/main.py`**: Initializes the FastAPI instance with clean route handlers (`/` and `/health`).
- **`tests/test_main.py`**: Uses FastAPI's `TestClient` to assert response status codes and expected JSON payloads.
- **`Dockerfile`**: Based on `python:3.12-slim` to minimize image size and attack surface, exposing port 8000 and starting `uvicorn`.
- **`pyproject.toml`**: Configures `ruff` with line length 88, enforcing `E` (Pycodestyle errors), `F` (Pyflakes), and `I` (isort imports).
- **`.github/workflows/ci.yml`**: Declarative workflow orchestrating continuous testing, linting, packaging, and EC2 remote execution.

---

## 🌐 API Endpoints

The microservice exposes the following RESTful endpoints:

| Method | Endpoint | Description | Expected Status | Sample Response |
| :--- | :--- | :--- | :---: | :--- |
| **`GET`** | `/` | Root greeting & version confirmation | `200 OK` | `{"message": "Hello CI/CD v2"}` |
| **`GET`** | `/health` | Application health check endpoint for monitoring & probes | `200 OK` | `{"status": "healthy"}` |
| **`GET`** | `/docs` | Interactive Swagger API documentation UI | `200 OK` | HTML / OpenAPI Schema |
| **`GET`** | `/redoc` | Alternative ReDoc API documentation UI | `200 OK` | HTML / ReDoc UI |

### Sample cURL Requests

```bash
# Test root endpoint
curl -X GET http://localhost:8000/
# Output: {"message":"Hello CI/CD v2"}

# Test health check endpoint
curl -f -X GET http://localhost:8000/health
# Output: {"status":"healthy"}
```

---

## 💻 Local Development Setup

Follow these instructions to run the application, linter, and tests on your local workstation.

### Prerequisites

- **Python**: Version `3.12+`
- **Git**: Version `2.x+`
- **Docker** *(optional, for container testing)*: Docker Desktop or Docker Engine

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Livesh28/fastapi-cicd-lab.git
   cd fastapi-cicd-lab
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

4. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Running Quality Checks & Tests

Before pushing changes to GitHub, always verify that your code conforms to lint standards and passes all tests:

- **Run Ruff Linter:**
  ```bash
  ruff check .
  ```
  *(To automatically fix safe issues: `ruff check --fix .`)*

- **Run Pytest Suite:**
  ```bash
  python -m pytest -v
  ```

> [!NOTE]
> Always execute pytest using `python -m pytest` so Python automatically appends the current working directory to `sys.path`, allowing modules under `app/` to be resolved cleanly.

### Running the Local Server

Start the Uvicorn development server with hot-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser and navigate to:
- **API Root**: [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🐳 Docker Containerization

The project includes an optimized `Dockerfile` leveraging `python:3.12-slim` to create lightweight, reproducible container images.

### Dockerfile Breakdown

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run Locally

1. **Build the Docker image:**
   ```bash
   docker build -t fastapi-cicd-lab:local .
   ```

2. **Run the container in detached mode:**
   ```bash
   docker run -d \
     --name fastapi-app \
     -p 8000:8000 \
     fastapi-cicd-lab:local
   ```

### Verify Local Container

- **Check container status:**
  ```bash
  docker ps -f name=fastapi-app
  ```

- **Query health check endpoint:**
  ```bash
  curl -i http://localhost:8000/health
  ```

- **Inspect container logs:**
  ```bash
  docker logs -f fastapi-app
  ```

- **Stop and remove container:**
  ```bash
  docker stop fastapi-app && docker rm fastapi-app
  ```

---

## ⚙️ GitHub Actions CI/CD Pipeline Deep Dive

The pipeline is defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) and automatically runs on every `push` to the `main` branch.

### 1. Test Job (`test`)
- Runs on `ubuntu-latest` with Python 3.12.
- Installs dependencies from `requirements.txt`.
- Runs `python -m pytest` across all test files in `tests/`.
- If any test fails, subsequent jobs (`build`, `deploy`) are immediately aborted.

### 2. Lint Job (`lint`)
- Runs on `ubuntu-latest` with Python 3.12 in parallel with the `test` job.
- Runs `ruff check .` to guarantee PEP 8 compliance, clean imports, and absence of syntax errors.

### 3. Build & Push Job (`build`)
- **Prerequisites**: Dependent on both `test` and `lint` completing successfully (`needs: [test, lint]`).
- Authenticates against **GitHub Container Registry (GHCR)** using `docker/login-action@v3` with `${{ secrets.GITHUB_TOKEN }}`.
- Builds the container using `docker/build-push-action@v6`.
- Tags the image with two tags:
  1. `ghcr.io/livesh28/fastapi-cicd-lab:latest`: For immediate references.
  2. `ghcr.io/livesh28/fastapi-cicd-lab:${{ github.sha }}`: **Immutable commit SHA tag** enabling audit trails and instant rollbacks.
- Pushes both tags to GHCR.

### 4. Deploy Job (`deploy`)
- **Prerequisites**: Dependent on `build` completing successfully (`needs: build`).
- Connects securely to the AWS EC2 virtual machine over SSH using `appleboy/ssh-action@v1.2.2`.
- Executes the remote deployment script:
  1. Authenticates Docker on the EC2 host with GHCR using the temporary repository token.
  2. Pulls the **exact immutable image** tagged with `${{ github.sha }}` to eliminate caching discrepancies:
     ```bash
     sudo docker pull ghcr.io/${{ github.repository }}:${{ github.sha }}
     ```
  3. Gracefully stops and cleans up the prior container instance (`fastapi-lab`).
  4. Starts a new container instance running with:
     - Detached mode (`-d`)
     - Automatic restart policy (`--restart unless-stopped`)
     - Port mapping (`-p 8000:8000`)
  5. Performs an in-place health check using `curl -f http://localhost:8000/health`. If the health check fails, the workflow marks the deployment as failed.

---

## ☁️ AWS EC2 Deployment Setup

To deploy this project to your own AWS EC2 instance, follow this setup guide:

### 1. EC2 Instance Configuration

1. **Launch an EC2 Instance:**
   - **AMI**: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS (64-bit x86_64)
   - **Instance Type**: `t2.micro` or `t3.micro` (AWS Free Tier eligible)
   - **Key Pair**: Create or use an existing RSA `.pem` key pair (e.g. `fastapi-key.pem`).

2. **Configure Security Group Inbound Rules:**
   | Type | Protocol | Port Range | Source | Purpose |
   | :--- | :--- | :--- | :--- | :--- |
   | **SSH** | TCP | `22` | `0.0.0.0/0` (or your IP / GitHub runner CIDRs) | SSH remote execution |
   | **Custom TCP** | TCP | `8000` | `0.0.0.0/0` | FastAPI direct HTTP traffic |
   | **HTTP** | TCP | `80` | `0.0.0.0/0` | Optional: Reverse Proxy (Nginx) |

### 2. Docker Installation on EC2

SSH into your EC2 instance:
```bash
ssh -i /path/to/fastapi-key.pem ubuntu@<YOUR_EC2_PUBLIC_IP>
```

Install and start Docker:
```bash
# Update system packages
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Docker Engine
sudo apt-get install -y docker.io curl

# Start and enable Docker service
sudo systemctl enable --now docker

# Add the ubuntu user to the docker group (allows running docker without sudo)
sudo usermod -aG docker ubuntu

# Verify Docker installation
docker --version
```

*(Log out and log back in for group membership changes to take effect).*

### 3. GitHub Repository Secrets

In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions** and add the following repository secrets:

| Secret Name | Description | Example / Format |
| :--- | :--- | :--- |
| **`EC2_HOST`** | Public IP address or Public DNS of your EC2 instance | `54.210.12.34` or `ec2-54-210-12-34.compute-1.amazonaws.com` |
| **`EC2_USER`** | SSH username for the instance | `ubuntu` (for Ubuntu AMIs) or `ec2-user` (for Amazon Linux) |
| **`EC2_SSH_KEY`** | Raw contents of the private SSH key (`.pem`) | `-----BEGIN RSA PRIVATE KEY----- ... -----END RSA PRIVATE KEY-----` |

> [!IMPORTANT]
> **GHCR Package Permissions**: Ensure that GitHub Actions has permission to write packages. In your repository, go to **Settings** > **Actions** > **General** > **Workflow permissions** and select **Read and write permissions**. The workflow also explicitly requests `packages: write` in `ci.yml`.

---

## 🔄 Rollback & Versioning Strategy

Because every build pushes an image tagged with the exact git commit SHA (`${{ github.sha }}`), rollback to any previous version is instantaneous and predictable:

```bash
# SSH into EC2
ssh -i <key.pem> ubuntu@<EC2_HOST>

# Pull and run any previous working commit
sudo docker stop fastapi-lab || true
sudo docker rm fastapi-lab || true
sudo docker run -d \
  --name fastapi-lab \
  --restart unless-stopped \
  -p 8000:8000 \
  ghcr.io/livesh28/fastapi-cicd-lab:<PREVIOUS_COMMIT_SHA>

# Verify rollback
curl -f http://localhost:8000/health
```

---

## 🛠 Troubleshooting & FAQs

### Q1: `ModuleNotFoundError: No module named 'app'` when running pytest locally
**Cause**: When running `pytest` directly, Python does not automatically prepend the root directory to `sys.path`.  
**Solution**: Always invoke pytest as a module:
```bash
python -m pytest
```
Or set `PYTHONPATH`:
```bash
PYTHONPATH=. pytest
```

---

### Q2: GitHub Actions fails with `ssh: handshake failed: ssh: unable to authenticate`
**Checklist**:
1. Check that `EC2_SSH_KEY` in GitHub Secrets includes the entire `.pem` file content, including `-----BEGIN OPENSSH PRIVATE KEY-----` (or `BEGIN RSA PRIVATE KEY`) and `-----END ...-----` tags.
2. Confirm `EC2_USER` is `ubuntu` (not `root` or `ec2-user`).
3. Ensure the corresponding public key is present in `~/.ssh/authorized_keys` on the EC2 instance with `600` file permissions.

---

### Q3: `docker login ghcr.io: denied: requested access to the resource is denied`
**Cause**: The `GITHUB_TOKEN` needs permissions to write packages to GitHub Container Registry.  
**Solution**:
1. Confirm `permissions: packages: write` is present in `ci.yml`.
2. Under GitHub repo settings > Actions > General > Workflow permissions, enable **Read and write permissions**.
3. If the package was previously created under personal account settings, check the package visibility and access policies under your GitHub profile packages.

---

### Q4: Port 8000 already allocated on EC2
**Cause**: A stray container or another application is occupying port 8000.  
**Solution**:
```bash
# Find and stop the process using port 8000
sudo lsof -i :8000
# Or inspect running Docker containers
sudo docker ps
sudo docker stop <container-id>
```

---

## 🚀 Future Enhancements & Production Roadmap

- [ ] **Nginx Reverse Proxy & SSL**: Configure Nginx as a reverse proxy with Let's Encrypt SSL/TLS certificates via Certbot on port 443.
- [ ] **Blue-Green Deployments**: Implement zero-downtime rolling container swaps using Docker Compose or Nginx upstream weighting.
- [ ] **Multi-Environment Pipelines**: Add `staging` and `production` branch flows with manual approval gates.
- [ ] **Infrastructure as Code (IaC)**: Automate EC2 provisioning, security groups, and networking using **Terraform** or **AWS CloudFormation**.
- [ ] **Container Scanning**: Integrate security vulnerability scanning into CI using **Trivy** or **Snyk**.
- [ ] **Monitoring & Observability**: Add Prometheus metrics endpoint (`/metrics`) and Grafana dashboard integration.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to use, modify, and distribute it for educational or commercial purposes.
