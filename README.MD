# 🎥 Video Enhancement Server (FastAPI + Real-ESRGAN)

This project is a FastAPI server that accepts uploaded videos, enhances them with [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) (AI upscaling), and provides endpoints to manage processed files.

---

## 📦 Requirements

- Python **3.10** (>= 3.7 works, but 3.10 is recommended)  
- `git`  
- `ffmpeg` (for extracting/encoding video frames)  
- macOS or Linux (tested on macOS, should also work on Linux)  

---

## ⚙️ Installation

python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux

pip install --upgrade pip

pip install -r requirements.txt

brew install ffmpeg or sudo apt update && sudo apt install ffmpeg -y

## Pull Real-ESRGAN

git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN

pip install basicsr

pip install facexlib
pip install gfpgan
pip install -r requirements.txt
python setup.py develop

### info - https://github.com/xinntao/Real-ESRGAN

## Running

python main.py
