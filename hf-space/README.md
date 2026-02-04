---
title: AutoML Worker
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.31.0
app_file: app.py
python_version: "3.11"
pinned: false
---

# AutoML Worker

ML execution service for the AutoML Platform. Receives workflow JSON, trains models, and returns results.

## Features

- Supports multiple ML algorithms (Random Forest, SVM, XGBoost, etc.)
- Loads sklearn sample datasets (iris, breast_cancer, diabetes, etc.)
- Computes classification and regression metrics
- Generates visualization plots (confusion matrix, feature importance, etc.)

## API Usage

Send a POST request to `/api/predict` with workflow JSON:

```json
{
  "data": ["{\"nodes\": [...], \"edges\": [...]}"]
}
```

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Then visit `http://localhost:7860`
