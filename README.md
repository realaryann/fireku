# FireKu

** Locally hosted, lightweight Flask application for Roku and FireTV for a LAN **

---

## 📝 About

FireKu bundles virtual remotes for Roku and FireTV into a single application. It offers automatic device
discovery on a LAN using the SSDP, part of the UPnP family of UDP protocols using port 1900. 

The backend service is split into two:
1) Roku: It utilizes the Roku REST API/ECP to POST required button commands to the device ip and port
2) FireTV: It utilizes the Android Debug Bridge to spin subprocesses to send button values to the FireTV ip.
---

## ✨ Features
- Feature 1 – Brief explanation
- Feature 2 – Brief explanation
- Feature 3 – Brief explanation

---

## 💻 Installation


```bash
# Clone the repository
git clone https://github.com/username/project.git

# Navigate into the project folder
cd project

# Install dependencies
# Example for Python projects
pip install -r requirements.txt
