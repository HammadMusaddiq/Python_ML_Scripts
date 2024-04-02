# Install Yolov8 Fixed Classification

## Step 1 (Create Virtual Environment)

```bash
python3 -m venv yolov8
source yolov8/bin/activate
```

## Step 2 (Install Requirements)

```bash
pip install --upgrade pip
pip install ultralytics==8.0.22
pip install fastapi[all]
```

## Step 3 (Run Server)

```bash
uvicorn app.main:app --reload --port 8087
#python -m uvicorn main:app --reload --host 0.0.0.0 --port 8087
```

## Step 4 (Test Server)

```bash
curl -X POST "http://localhost:8087/predict" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"image_url\":\" \
https://images.unsplash.com/photo-1617670000000-0c0c0c0c0c0c?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80\"}"
```

