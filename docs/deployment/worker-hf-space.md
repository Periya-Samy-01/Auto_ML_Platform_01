# ML Worker Deployment (Hugging Face Space)

## Why HF Space?

Render's free tier has a **60-second request timeout**, but ML model training often takes longer. Hugging Face Spaces:
- Allow longer execution times (5+ minutes)
- Provide 2GB RAM and 2 CPU cores (free tier)
- Offer optional GPU access (paid)
- Auto-rebuild when code changes

## Prerequisites

- Hugging Face account (free)
- Files from `hf-space/` directory in your project

## Step-by-Step Deployment

### 1. Create New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Configure:
   - **Space name**: `automl-worker`
   - **SDK**: Gradio
   - **Hardware**: CPU Basic (free)
   - **Visibility**: Public (required for free tier)

### 2. Upload Files

Upload these files from your `hf-space/` directory:

#### `app.py`
The main Gradio application containing:
- Workflow execution logic
- Model training (sklearn algorithms)
- Metric computation
- Plot generation

#### `requirements.txt`
```txt
gradio==4.31.0
huggingface_hub==0.23.0
numpy
pandas
scikit-learn
matplotlib
```

#### `README.md`
```markdown
---
title: AutoML Worker
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.31.0
python_version: "3.11"
app_file: app.py
pinned: false
---

ML execution worker for AutoML Platform.
```

### 3. Wait for Build

HF Space will:
1. Detect the Gradio SDK
2. Install dependencies from `requirements.txt`
3. Start the Gradio app

Build typically takes 2-5 minutes.

### 4. Get Space URL

Once running, your Space URL is:
```
https://[username]-[space-name].hf.space
```

Example: `https://john-automl-worker.hf.space`

### 5. Configure Backend

Add the Space URL to your Render backend environment:
```env
HF_SPACE_URL=https://username-automl-worker.hf.space
```

## API Integration

The backend communicates with HF Space using Gradio 4.x API:

### Request Flow

```
Backend                          HF Space
   │                                │
   │ POST /call/predict             │
   │   {"data": [workflow_json]}    │
   │───────────────────────────────>│
   │                                │
   │ {"event_id": "abc123"}         │
   │<───────────────────────────────│
   │                                │
   │ GET /call/predict/abc123       │
   │───────────────────────────────>│
   │                                │
   │ SSE: data: ["results_json"]    │
   │<───────────────────────────────│
```

## Updating the Worker

### Option 1: Manual Upload

1. Edit files in HF Space web interface
2. Space auto-rebuilds on save

### Option 2: Git Sync

1. Clone your HF Space:
   ```bash
   git clone https://huggingface.co/spaces/username/automl-worker
   ```
2. Copy files from `hf-space/` directory
3. Push changes:
   ```bash
   git add -A && git commit -m "Update worker" && git push
   ```

## Supported Algorithms

The worker supports these sklearn algorithms:

| Algorithm | Classification | Regression |
|-----------|---------------|------------|
| Logistic Regression | ✅ | - |
| Random Forest | ✅ | ✅ |
| Gradient Boosting | ✅ | ✅ |
| SVM | ✅ | ✅ |
| XGBoost | ✅ | ✅ |
| K-Means | Clustering | - |

## Troubleshooting

### Space Won't Start

- Check `README.md` has correct YAML frontmatter
- Verify `sdk_version` matches `gradio` in `requirements.txt`
- Check build logs for import errors

### Training Times Out

- HF Space has ~5-minute limit per request
- Use smaller datasets for testing
- Consider paid tier for longer training

### Results Not Returned

- Check Space logs for execution errors
- Verify workflow JSON format matches expected schema
- Ensure all required node configs are present

## Monitoring

View Space logs at:
```
https://huggingface.co/spaces/username/automl-worker/logs
```
