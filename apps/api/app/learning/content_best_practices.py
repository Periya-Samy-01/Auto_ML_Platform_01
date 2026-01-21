"""
Best Practices Topic Content
Lesson content for the Best Practices topic
"""

BEST_PRACTICES_CONTENT = {
    "data-quality": {
        "content": """
## What is it?

**"Garbage in, garbage out"** is the fundamental rule of ML. No algorithm, no matter how sophisticated, can produce good results from bad data. Data quality encompasses accuracy, completeness, consistency, and relevance of your dataset.

Spending time on data quality pays dividends throughout the project.

## How it Works

**Dimensions of Data Quality:**
```
Accuracy:
├── Values are correct
├── Labels are accurate
└── No errors in collection

Completeness:
├── Missing values handled
├── All necessary fields present
└── Sufficient sample size

Consistency:
├── Same format throughout
├── No contradictions
├── Standardized units

Relevance:
├── Features relate to target
├── Data is representative
└── Time period is appropriate
```

**Common Data Quality Issues:**
```
├── Incorrect labels (mislabeled examples)
├── Data entry errors (typos, wrong values)
├── Duplicate records
├── Inconsistent formats (dates, categories)
├── Selection bias (non-representative sample)
├── Outliers (real or errors?)
├── Missing values (systematic or random?)
└── Data drift (distribution changes over time)
```

## Example

**E-commerce Churn Prediction:**

```
Data Quality Issues Found:
├── 500 customers with age = -1 (impossible)
├── "California" vs "CA" vs "california" (inconsistent)
├── 10% purchase amounts missing
├── Some customers appear twice
└── Labels from overloaded CSR (noisy)

Before Quality Fix:
├── Model accuracy: 72%
├── False positive rate: 35%
└── Business doesn't trust predictions

Quality Improvements:
├── Fixed ages: Used median imputation
├── Standardized states: Mapped to codes
├── Filled missing purchases: Used customer average
├── Removed duplicates: Kept most recent
├── Re-labeled noisy samples: Expert review

After Quality Fix:
├── Model accuracy: 86%
├── False positive rate: 15%
└── Business adopts predictions

Same model, better data = much better results!
```

## When to Use

**Data Quality Checklist:**
```
Before any modeling:
├── Check for missing values
├── Look for duplicates
├── Verify label accuracy (sample check)
├── Check value distributions (outliers?)
├── Validate data types
├── Confirm data freshness
└── Assess representativeness
```

**Red Flags:**
```
├── Accuracy too good (< 100%, data leakage?)
├── Class distribution very different from production
├── Features available in training but not production
├── Data collected differently across sources
└── Model performance varies dramatically by segment
```

## Key Takeaways

- **Data quality > algorithm choice** for most projects
- Fix data issues **before** trying fancy models
- **Garbage in = garbage out** (always true)
- Check **labels carefully**: Noisy labels hurt more than noisy features
- **Sample check** data manually before and during modeling
- Time spent on data pays off in **model performance**
""",
        "key_points": [
            "Garbage in, garbage out—data quality trumps algorithms",
            "Fix data issues before trying fancy models",
            "Noisy labels hurt more than noisy features",
            "Manually sample-check data during the project",
            "Time spent on data pays off in model performance"
        ]
    },
    
    "start-simple": {
        "content": """
## What is it?

**Start simple** means beginning with straightforward models before adding complexity. A baseline model helps you understand the problem, verify your pipeline, and establish a benchmark. Often, simple models perform surprisingly well—and if they don't, they help you understand why.

Complexity should be earned, not assumed.

## How it Works

**Why Start Simple:**
```
├── Establishes baseline to beat
├── Validates data pipeline works
├── Provides quick feedback
├── Reveals data issues
├── May be good enough!
└── Makes debugging easier
```

**Baseline Models by Task:**
```
Classification:
├── Logistic Regression (linear, interpretable)
├── Random Forest (non-linear, robust)
└── Majority class predictor (sanity check)

Regression:
├── Linear Regression (interpretable)
├── Decision Tree (simple non-linear)
└── Mean predictor (sanity check)

Clustering:
├── K-Means (simple, fast)
└── Hierarchical (no K choice)
```

**Complexity Ladder:**
```
Level 1: Simple baseline (Logistic Regression)
         ↓ If not good enough
Level 2: Better baseline (Random Forest)
         ↓ If not good enough
Level 3: Tuned model (XGBoost with tuning)
         ↓ If not good enough
Level 4: Complex model (Neural Network)
         ↓ If not good enough
Level 5: Ensemble or custom architecture
```

## Example

**Document Classification Project:**

```
Goal: Classify support tickets into categories

Attempt 1: Started with BERT (state-of-art)
├── Training time: 4 hours
├── Deployment complexity: GPU required
├── Accuracy: 89%
└── Hard to debug errors

Step back: Try simple baseline first

Attempt 2: TF-IDF + Logistic Regression
├── Training time: 10 seconds
├── Deployment: Simple, any server
├── Accuracy: 85%
└── Easy to debug and explain

Analysis:
├── Only 4% accuracy difference
├── Simple model is 1000x faster to train
├── Costs $10/month vs $200/month to serve
└── Easy to update with new categories

Decision: Deploy simple model
├── If accuracy becomes critical, revisit
└── Complexity wasn't justified
```

## When to Use

**Always Start Simple When:**
```
├── New problem (don't know what's possible)
├── New dataset (might have issues)
├── Timeline is tight (need quick results)
├── Deployment resources limited
├── Interpretability matters
└── Team is learning the domain
```

**When to Add Complexity:**
```
├── Simple model clearly underfits
├── Business requires higher accuracy
├── Compute resources available
├── Team has expertise
└── Baseline is stable and well-understood
```

**Questions Before Adding Complexity:**
```
1. Is the simple model truly underfitting?
2. Have I tried improving data quality?
3. Is the performance gap worth the cost?
4. Can I maintain the complex model?
5. Does stakeholder really need more accuracy?
```

## Key Takeaways

- **Baseline first**: Logistic Regression, Random Forest
- Simple models reveal **data and pipeline issues**
- Complexity should be **earned**, not assumed
- **Simple is often good enough** for production
- Add complexity only when **clearly justified**
- A working simple model beats a broken complex one
""",
        "key_points": [
            "Always start with a baseline model (Logistic Regression, Random Forest)",
            "Simple models reveal data and pipeline issues",
            "Complexity should be earned, not assumed",
            "Simple models are often good enough for production",
            "Add complexity only when clearly justified"
        ]
    },
    
    "experiment-tracking": {
        "content": """
## What is it?

**Experiment tracking** is the practice of systematically recording your ML experiments: parameters, code versions, results, and artifacts. Without it, you can't reproduce results, compare approaches, or remember what you tried. It's version control for ML experiments.

Essential for any serious ML work.

## How it Works

**What to Track:**
```
For each experiment, log:
├── Hyperparameters (learning rate, depth, etc.)
├── Dataset version (or hash)
├── Code version (git commit)
├── Random seed
├── Training metrics (loss, time)
├── Validation metrics (accuracy, F1, etc.)
├── Test metrics (final evaluation)
├── Model artifacts (saved model)
└── Notes (what you tried, why)
```

**Tracking Tools:**
```
Popular Options:
├── MLflow: Open source, self-hosted or cloud
├── Weights & Biases: Cloud-first, great UI
├── Neptune: Cloud, experiment comparison
├── TensorBoard: TensorFlow native
├── DVC: Data versioning + experiments
└── Simple: Spreadsheet + good folder structure
```

**Basic Folder Structure:**
```
project/
├── data/
│   ├── raw/
│   └── processed/
├── experiments/
│   ├── 2024-01-15_baseline/
│   │   ├── config.json
│   │   ├── model.pkl
│   │   └── metrics.json
│   └── 2024-01-16_tuned_rf/
├── notebooks/
├── src/
└── README.md
```

## Example

**Experiment Tracking in Practice:**

```
Without Tracking (Bad):
├── "I think the good model was from last Tuesday..."
├── "What learning rate did I use?"
├── "Can't reproduce that 95% accuracy"
└── Time wasted re-running experiments

With Tracking (Good):
Experiment: rf_baseline_v2
├── Date: 2024-01-15 14:32
├── Git commit: a1b2c3d
├── Dataset: customers_v3 (hash: xyz789)
├── Parameters:
│   ├── n_estimators: 100
│   ├── max_depth: 10
│   └── min_samples_split: 5
├── Results:
│   ├── CV accuracy: 87.3% ± 1.2%
│   ├── Test accuracy: 86.8%
│   └── Training time: 45s
├── Model saved: models/rf_baseline_v2.pkl
└── Notes: "Stronger than XGBoost on this data"

Three weeks later:
├── "Let me check what worked best..."
├── Filter by test accuracy
├── Exact config to reproduce
└── Can compare all approaches
```

## When to Use

**Benefits of Tracking:**
```
├── Reproducibility: Exact reproduction of any run
├── Comparison: Compare all approaches fairly
├── Collaboration: Team can see what's been tried
├── Debugging: "What changed between good and bad?"
├── Documentation: Automatic experiment history
└── Production: Know exactly what's deployed
```

**Minimum Viable Tracking:**
```
If no tools, at least:
├── Save config.json with each run
├── Use git for code versioning
├── Name experiments with dates
├── Keep a running notes document
└── Save final models with metadata
```

## Key Takeaways

- **Log everything**: Parameters, metrics, code version
- **Use a tool**: MLflow, W&B, or even spreadsheets
- Without tracking, you **waste time repeating work**
- Enables **reproducibility** and **comparison**
- Start tracking from **day one** of any project
- Future you will **thank present you**
""",
        "key_points": [
            "Log everything: parameters, metrics, code version",
            "Use tracking tools: MLflow, Weights & Biases, or spreadsheets",
            "Without tracking, you waste time repeating work",
            "Enables reproducibility and fair comparison",
            "Start tracking from day one of any project"
        ]
    },
    
    "deployment": {
        "content": """
## What is it?

**Model deployment** is getting your trained model into production where it can make real predictions on new data. A model that only works in a Jupyter notebook isn't providing value. Deployment involves considerations around infrastructure, latency, monitoring, and maintenance.

Where ML creates business value.

## How it Works

**Deployment Options:**
```
Batch Inference:
├── Run predictions on batches periodically
├── Results stored in database
├── Good for: Reports, recommendations
├── Latency: Hours to days

Real-time API:
├── Model served via REST/gRPC endpoint
├── Predictions on-demand
├── Good for: User-facing features
├── Latency: Milliseconds to seconds

Edge Deployment:
├── Model runs on device (phone, IoT)
├── No network required
├── Good for: Privacy, offline use
├── Constraints: Model size, compute
```

**Production Considerations:**
```
├── Latency: How fast must predictions be?
├── Throughput: How many predictions per second?
├── Availability: What uptime is required?
├── Cost: Compute, storage, maintenance
├── Security: Data privacy, model access
├── Monitoring: When does model fail?
└── Updates: How to refresh the model?
```

## Example

**E-commerce Recommendation System:**

```
Development:
├── Model: Collaborative filtering + embeddings
├── Training: 2 hours on GPU
├── Offline accuracy: 85% hit rate
└── "Ready for production!"

Production Reality:
├── 10M users, need predictions in <100ms
├── Model too slow for real-time
├── Need to handle traffic spikes (Black Friday)
└── What if model starts recommending wrong things?

Deployment Solution:
├── Pre-compute recommendations for top 100K users
├── Cache popular item recommendations
├── Simple fallback model for edge cases
├── A/B test before full rollout

Monitoring:
├── Track click-through rate
├── Alert if CTR drops >15%
├── Log predictions for debugging
├── Weekly model refresh
```

## When to Use

**Deployment Checklist:**
```
Before deploying:
├── Model tested on realistic test set
├── Latency measured and acceptable
├── Error handling for edge cases
├── Fallback if model fails
├── Monitoring and alerting setup
├── Logging for debugging
├── A/B testing plan
└── Rollback procedure
```

**Deployment Patterns:**

| Pattern | When to Use |
|---------|-------------|
| Batch | Daily reports, not time-sensitive |
| Shadow | Test new model without affecting users |
| Canary | Gradual rollout, monitor closely |
| A/B Test | Compare models on real traffic |
| Blue/Green | Instant switch between versions |

**Model Monitoring:**
```
Watch for:
├── Data drift (input distribution changes)
├── Prediction drift (output distribution changes)
├── Performance degradation (accuracy drops)
├── Latency increases
└── Error rate spikes
```

## Key Takeaways

- A notebook model is **not deployed**
- Consider **latency, throughput, cost** early
- Always have a **fallback** plan
- **Monitor** predictions in production
- **A/B test** before full rollout
- Models **decay**: Plan for retraining
""",
        "key_points": [
            "A notebook model provides no business value until deployed",
            "Consider latency, throughput, and cost early in the project",
            "Always have a fallback plan for model failures",
            "Monitor predictions in production for drift and degradation",
            "A/B test before full rollout and plan for retraining"
        ]
    }
}
