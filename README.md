# FireKu

**Locally hosted, lightweight Flask application for Roku and FireTV remotes under a LAN**

---

## 📝 About

FireKu bundles virtual remotes for Roku and FireTV into a single application. It offers automatic device
discovery on a LAN using the SSDP, part of the UPnP family of UDP protocols using port 1900. 

The backend service is split into two:
1) Roku: It utilizes the Roku REST API/ECP to POST required button commands to the device ip and port
2) FireTV: It utilizes the Android Debug Bridge to spin subprocesses to send button values to the FireTV ip.
---

## ✨ Features
- **Automatic Device Discovery** – FireKu utilizes UDP packets to discover FireTVs and Rokus on a private network and shows a dropdown list to select between your desired device
- **Remote Landing page** – FireKu has dedicated landing pages for FireTV and Roku with their own respective styles 
- **Fast, efficient communication** - FireKu uses the official ECP/Roku REST API to communicate with your device efficiently.

---

## 💻 Installation and Usage

## Windows, MacOS, Linux (1)

```bash
# Clone the repository
git clone git@github.com:realaryann/fireku.git

# Navigate into the project folder
cd fireku

# [OPTIONAL] Create a venv
python -m venv venv

# [OPTIONAL] utilize venv
.venv\src\Activate # Windows

source .venv/bin/activate # Mac, Linux

# Install dependencies
pip install -r requirements.txt

# Run Flask application
python main.py

# Navigate to application
localhost:5001
```

## Linux (2) - Dockerfile based

```bash

# Clone the repository
git clone git@github.com:realaryann/fireku.git

# Navigate into the project folder
cd fireku

# Create a docker image
docker build -t yourusername/fireku .

# Run docker image with networkhost
docker run --network host -p 8888:5001 -d --name fireku yourusername/fireku

# Navigate to port 8888 on localhost
localhost:8888

# Stop docker container 
docker stop fireku

# Prune if necessary
docker container prune
```
