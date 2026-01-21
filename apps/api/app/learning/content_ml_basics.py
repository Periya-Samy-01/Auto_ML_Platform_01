"""
ML Basics Topic Content
Lesson content for the ML Basics topic
"""

# Each lesson follows the structure:
# - What is it?
# - How it works
# - Example
# - When to Use
# - Key Takeaways

ML_BASICS_CONTENT = {
    "what-is-ml": {
        "content": """
## What is it?

Machine Learning (ML) is a subset of artificial intelligence that enables computers to learn patterns from data and make decisions without being explicitly programmed. Unlike traditional software where developers write specific rules for every scenario, ML systems discover these rules automatically by analyzing examples.

Think of it this way: instead of telling a computer "if the email contains 'lottery winner', mark it as spam," you show the computer thousands of spam and non-spam emails, and it learns to identify the patterns itself.

## How it Works

The fundamental process of machine learning involves three key steps:

1. **Data Collection**: Gather relevant examples that represent the problem you want to solve
2. **Training**: Feed this data to an algorithm that identifies patterns and relationships
3. **Prediction**: Use the learned patterns to make predictions on new, unseen data

```
TRADITIONAL PROGRAMMING:
Input Data + Rules → Program → Output

MACHINE LEARNING:
Input Data + Expected Output → Algorithm → Learned Rules
```

The algorithm adjusts its internal parameters iteratively, minimizing the difference between its predictions and the actual outcomes until it achieves acceptable accuracy.

## Example

Consider building a house price predictor:

**Traditional Approach**: You would manually define rules like "if bedrooms > 3 AND location = 'downtown' AND age < 10 years, then price = high". This becomes impossibly complex with many factors.

**ML Approach**: You provide the algorithm with thousands of past house sales including features (bedrooms, location, size, age) and their actual prices. The algorithm discovers which features matter most and how they combine to affect price.

[Diagram: Traditional vs ML Approach Comparison]

## When to Use

Machine learning is ideal when:
- **Patterns are complex**: Too many variables for humans to define rules manually
- **Data is abundant**: You have sufficient examples to learn from (typically thousands)
- **Patterns may change**: The underlying rules evolve over time (spam tactics, market trends)
- **Human expertise is scarce**: Difficult to articulate expert knowledge into explicit rules
- **Personalization is needed**: Different users require different predictions

Avoid ML when:
- Simple if-then rules suffice
- You have very little data
- Decisions require full explainability for legal/compliance reasons
- The cost of errors is extremely high and unpredictable

## Key Takeaways

- ML enables computers to **learn from data** rather than following explicit rules
- It excels at finding **complex patterns** humans might miss
- The quality of predictions depends heavily on the **quality and quantity of training data**
- ML is not magic—it requires careful problem definition, data preparation, and evaluation
- Not every problem needs ML; sometimes simple rules work better
""",
        "key_points": [
            "ML learns patterns from data instead of being explicitly programmed",
            "The process involves data collection, training, and prediction",
            "Quality and quantity of data directly impact model performance",
            "ML is best for complex patterns, abundant data, and changing environments",
            "Simple problems may not need ML solutions"
        ]
    },
    
    "types-of-ml": {
        "content": """
## What is it?

Machine learning algorithms are categorized into three main types based on how they learn from data: Supervised Learning, Unsupervised Learning, and Reinforcement Learning. Understanding these categories helps you choose the right approach for your problem.

## How it Works

### Supervised Learning
The algorithm learns from **labeled data**—examples where you know both the input and the correct output. It's like learning with a teacher who provides the answers.

```
Training Data: [Features] → [Known Label]
Example: [House Size, Bedrooms, Location] → [Price: $350,000]

After Training:
New House [2000 sqft, 3 beds, Suburb] → Predicted Price: $325,000
```

**Types**: Classification (predicting categories) and Regression (predicting numbers)

### Unsupervised Learning
The algorithm works with **unlabeled data**—it finds hidden patterns without being told what to look for. It's like exploring data to discover natural groupings.

```
Training Data: [Features only, no labels]
Example: [Customer Age, Spending, Frequency]

Output: Discovered clusters like "Budget Shoppers", "Premium Buyers"
```

**Uses**: Clustering, dimensionality reduction, anomaly detection

### Reinforcement Learning
The algorithm learns through **trial and error**, receiving rewards or penalties for its actions. It's like training a pet with treats.

```
Agent takes Action → Environment provides Reward/Penalty
Agent adjusts Strategy → Repeat until optimal behavior
```

**Uses**: Game playing, robotics, autonomous systems

## Example

**Email Classification (Supervised)**:
- Training data: Thousands of emails labeled as "spam" or "not spam"
- Model learns: Words, patterns, sender characteristics that indicate spam
- Prediction: New email arrives → Model predicts spam/not spam

**Customer Segmentation (Unsupervised)**:
- Data: Customer purchase history (no predefined groups)
- Algorithm discovers: 4 natural customer segments
- Business use: Tailor marketing to each segment

**Game AI (Reinforcement)**:
- Agent: Chess-playing program
- Actions: Possible moves
- Reward: +1 for winning, -1 for losing
- Learning: Discovers winning strategies through millions of games

[Diagram: Three Types of ML with Examples]

## When to Use

| Type | Use When |
|------|----------|
| **Supervised** | You have labeled data and want to predict outcomes |
| **Unsupervised** | You want to discover hidden patterns or groupings |
| **Reinforcement** | The agent must learn optimal behavior through interaction |

**Supervised Learning** is most common in business applications because labeled data is often available from historical records.

## Key Takeaways

- **Supervised**: Learn from labeled examples to predict outcomes (classification/regression)
- **Unsupervised**: Discover hidden patterns in unlabeled data (clustering)
- **Reinforcement**: Learn optimal actions through trial and error with rewards
- Most business ML problems use supervised learning
- The choice depends on your data availability and problem type
""",
        "key_points": [
            "Supervised learning uses labeled data to predict outcomes",
            "Unsupervised learning discovers patterns without labels",
            "Reinforcement learning optimizes through trial and error",
            "Supervised learning is most common in business applications",
            "Choose based on data availability and problem requirements"
        ]
    },
    
    "ml-pipeline": {
        "content": """
## What is it?

The ML Pipeline is the end-to-end process of building a machine learning solution, from understanding the problem to deploying a working model. It's a structured workflow that ensures reproducibility, quality, and maintainability of your ML projects.

Think of it as a recipe: each step builds upon the previous one, and skipping steps leads to poor results.

## How it Works

The pipeline consists of six main stages:

### 1. Problem Definition
- Define what you're trying to predict or discover
- Determine success metrics
- Understand business constraints

### 2. Data Collection & Exploration
- Gather relevant data from various sources
- Explore data distributions and relationships
- Identify data quality issues

```
Data Exploration Checklist:
├── Check data size (rows, columns)
├── Identify data types (numeric, categorical, text)
├── Find missing values
├── Detect outliers
└── Visualize distributions
```

### 3. Data Preprocessing
- Handle missing values (impute or remove)
- Encode categorical variables
- Scale numerical features
- Split into training and test sets

### 4. Model Training
- Select appropriate algorithms
- Train models on training data
- Tune hyperparameters

### 5. Model Evaluation
- Evaluate on held-out test data
- Compare multiple models
- Validate against business requirements

### 6. Deployment & Monitoring
- Deploy model to production
- Monitor performance over time
- Retrain when performance degrades

[Diagram: ML Pipeline Flow Chart]

## Example

**Building a Customer Churn Predictor:**

1. **Define**: Predict which customers will cancel subscription next month
2. **Collect**: Gather customer demographics, usage patterns, support tickets
3. **Preprocess**: Handle missing ages, encode subscription types, scale usage metrics
4. **Train**: Try Logistic Regression, Random Forest, compare results
5. **Evaluate**: Achieve 85% accuracy, 78% recall on churners
6. **Deploy**: Integrate into CRM, flag high-risk customers weekly

```
Typical Time Distribution:
├── Data Collection/Prep: 60-70%
├── Model Training: 10-15%
├── Evaluation: 10-15%
└── Deployment: 10-15%
```

## When to Use

Follow the full pipeline when:
- Building production ML systems
- Working in teams that need reproducibility
- Projects require auditability
- You want maintainable, scalable solutions

You might simplify for:
- Quick prototypes and experiments
- One-time analysis tasks
- Learning and exploration

**Important**: Data collection and preprocessing typically consume 60-80% of project time. Don't underestimate this phase!

## Key Takeaways

- The ML pipeline provides a **structured approach** from problem to deployment
- **Data preparation** is the most time-consuming step (60-80% of effort)
- Each stage builds on the previous—**don't skip steps**
- **Evaluation** must happen on data the model hasn't seen during training
- **Monitoring** deployed models is essential as data patterns change over time
- A well-defined pipeline ensures **reproducibility** and **maintainability**
""",
        "key_points": [
            "The pipeline covers problem definition through deployment",
            "Data preparation consumes 60-80% of project time",
            "Each stage builds on the previous—don't skip steps",
            "Always evaluate on unseen test data",
            "Deployed models require ongoing monitoring",
            "A structured pipeline ensures reproducibility"
        ]
    },
    
    "key-terminology": {
        "content": """
## What is it?

Machine learning has its own vocabulary that can be confusing for beginners. Understanding these key terms is essential for reading documentation, communicating with data scientists, and following ML tutorials.

This lesson covers the most important terminology you'll encounter in any ML project.

## How it Works

### Core Concepts

**Features (X)**: Input variables used to make predictions. Also called attributes, predictors, or independent variables.
```
House Price Prediction Features:
├── Square footage
├── Number of bedrooms
├── Location
└── Year built
```

**Labels/Target (y)**: The outcome you're trying to predict. Also called the dependent variable or response.
```
In house price prediction: Label = Sale Price
In spam detection: Label = Spam/Not Spam
```

**Training Data**: The dataset used to teach the model patterns.

**Test Data**: A separate dataset used to evaluate model performance on unseen examples.

### Model Performance

**Overfitting**: When a model memorizes the training data instead of learning general patterns. It performs great on training data but poorly on new data.

```
Signs of Overfitting:
├── Training accuracy: 99%
├── Test accuracy: 65%
└── Model is too complex for the data
```

**Underfitting**: When a model is too simple to capture the underlying patterns. It performs poorly on both training and test data.

**Generalization**: The model's ability to perform well on new, unseen data—the ultimate goal of ML.

### Training Process

**Hyperparameters**: Settings you choose before training (learning rate, number of trees, etc.). These control how the model learns.

**Parameters**: Values the model learns during training (weights, coefficients). These define the learned patterns.

**Epoch**: One complete pass through the entire training dataset.

**Batch**: A subset of training data processed together before updating model parameters.

[Diagram: Features, Labels, and Train/Test Split Visualization]

## Example

**Spam Email Classifier:**

| Term | Example |
|------|---------|
| Features | Email length, sender domain, word frequencies |
| Label | Spam (1) or Not Spam (0) |
| Training Data | 8,000 labeled emails |
| Test Data | 2,000 labeled emails (held out) |
| Overfitting | Model flags emails from "john@company.com" as spam because John sent spam in training data |
| Generalization | Model correctly identifies new spam patterns it hasn't seen |

## When to Use

These terms appear throughout ML work:

- **Features/Labels**: During data preparation and model selection
- **Train/Test Split**: Essential for honest model evaluation
- **Overfitting/Underfitting**: When diagnosing model problems
- **Hyperparameters**: When tuning model performance

Understanding terminology helps you:
- Read ML documentation and tutorials
- Communicate with technical teams
- Debug model performance issues
- Make informed decisions about model design

## Key Takeaways

- **Features** are inputs; **Labels** are outputs you predict
- **Training data** teaches the model; **Test data** evaluates it
- **Overfitting** = memorizing; **Underfitting** = oversimplifying
- **Generalization** is the goal—performing well on new data
- **Hyperparameters** are set by you; **Parameters** are learned by the model
- Proper **train/test splitting** prevents overly optimistic evaluations
""",
        "key_points": [
            "Features are inputs; Labels are the target outputs",
            "Training data teaches; Test data evaluates honestly",
            "Overfitting means memorizing instead of learning patterns",
            "Underfitting means the model is too simple",
            "Generalization—performing well on new data—is the goal",
            "Hyperparameters are your choices; Parameters are learned"
        ]
    },
    
    "when-to-use-ml": {
        "content": """
## What is it?

Knowing when to use machine learning—and when not to—is one of the most valuable skills in data science. ML is powerful but not always the right solution. This lesson helps you identify problems suited for ML and recognize situations where simpler approaches work better.

## How it Works

### ML is a Good Fit When:

**1. Patterns are Complex**
When relationships between inputs and outputs are too intricate for humans to define manually.

```
Good for ML:
├── Image recognition (millions of pixel relationships)
├── Natural language understanding
├── Fraud detection (hundreds of behavioral signals)
└── Recommendation systems
```

**2. Data is Abundant**
ML algorithms need examples to learn from. More complex problems require more data.

```
Rough Data Guidelines:
├── Simple classification: 1,000+ examples per class
├── Complex patterns: 10,000+ examples
├── Deep learning: 100,000+ examples
└── Computer vision: Millions of images
```

**3. Patterns May Change Over Time**
When underlying rules evolve, ML can adapt by retraining on new data.

**4. Exact Rules are Unknown**
When experts can recognize patterns but can't articulate explicit rules.

### ML is NOT a Good Fit When:

**1. Simple Rules Suffice**
```
Don't use ML for:
├── Age > 18 → Adult
├── Balance < 0 → Overdraft
└── Date > Expiry → Expired
```

**2. Data is Scarce**
With too few examples, ML models can't learn reliable patterns.

**3. Full Explainability is Required**
Some domains require explaining every decision (legal, medical diagnostics).

**4. Deterministic Outcomes are Needed**
When you need 100% predictable behavior, not probabilistic predictions.

[Diagram: Decision Tree for "Should I Use ML?"]

## Example

**Problem: Validate Email Format**
- Rule: Check if string matches `text@text.text` pattern
- Verdict: ❌ Don't use ML—a simple regex works perfectly

**Problem: Detect Fraudulent Transactions**
- Hundreds of signals (amount, location, time, device, history)
- Fraud patterns constantly evolve
- Human rules miss subtle combinations
- Verdict: ✅ Perfect for ML

**Problem: Recommend Movies to Users**
- Millions of users and movies
- Complex taste patterns
- Preferences change over time
- Verdict: ✅ Perfect for ML

**Problem: Calculate Shipping Cost**
- Based on weight, distance, shipping class
- Fixed formula defined by business
- Verdict: ❌ Use the formula directly

## When to Use

| Scenario | Use ML? | Why |
|----------|---------|-----|
| Predict customer churn | ✅ Yes | Complex behavioral patterns |
| Check if number is even | ❌ No | Simple modulo operation |
| Classify product reviews | ✅ Yes | Language understanding is complex |
| Apply tax rate by region | ❌ No | Lookup table suffices |
| Detect manufacturing defects | ✅ Yes | Visual patterns are complex |
| Sort list alphabetically | ❌ No | Standard algorithm exists |

**Rule of Thumb**: If you can write down the exact rules in under an hour, you probably don't need ML.

## Key Takeaways

- ML excels at **complex patterns** that humans can't easily define
- Sufficient **data quantity and quality** is essential
- ML adapts to **changing patterns** through retraining
- **Don't overcomplicate**—simple rules beat ML for simple problems
- Consider **explainability requirements** before choosing ML
- **Cost-benefit analysis**: ML adds complexity; ensure the benefit justifies it
""",
        "key_points": [
            "Use ML for complex patterns, abundant data, and changing rules",
            "Don't use ML when simple rules or formulas suffice",
            "Data quantity and quality directly impact ML success",
            "Consider explainability requirements for your domain",
            "ML adds complexity—ensure benefits justify the cost",
            "If you can write rules in an hour, you probably don't need ML"
        ]
    },
    
    "datasets-quality": {
        "content": """
## What is it?

Data quality is the foundation of successful machine learning. The principle "garbage in, garbage out" applies strongly to ML—no algorithm can compensate for poor data. This lesson covers what makes a good dataset and how to handle common data quality issues.

## How it Works

### Characteristics of Good Data

**1. Sufficient Quantity**
More data generally leads to better models, but quality matters more than raw numbers.

```
Data Quantity Guidelines:
├── Start with: 10x features minimum
├── Classification: 1,000+ per class ideally
├── Rare events: Oversample or use specialized techniques
└── Deep learning: Significantly more data needed
```

**2. Representative Samples**
Training data must represent the real-world scenarios the model will encounter.

```
Problem Example:
├── Training: Photos taken in daylight
├── Production: Model fails on nighttime photos
└── Fix: Include diverse lighting conditions
```

**3. Accurate Labels**
For supervised learning, incorrect labels teach wrong patterns.

**4. Minimal Bias**
Data should not systematically favor certain outcomes inappropriately.

### Common Data Quality Issues

**Missing Values**
```
Handling Strategies:
├── Remove rows (if few missing)
├── Remove columns (if mostly missing)
├── Impute with mean/median (numerical)
├── Impute with mode (categorical)
└── Use "missing" as a category
```

**Outliers**
Extreme values that may be errors or genuine rare cases.

**Duplicates**
Repeated records that can bias the model toward certain examples.

**Inconsistent Formats**
Same information represented differently (USA, United States, US).

[Diagram: Data Quality Dimensions]

## Example

**Customer Churn Dataset Quality Check:**

| Issue | Example | Fix |
|-------|---------|-----|
| Missing | 15% missing phone numbers | Remove column (not predictive anyway) |
| Missing | 2% missing age | Impute with median age |
| Outlier | Customer age = 150 | Cap at 100 or investigate |
| Duplicate | Same customer ID twice | Keep most recent record |
| Format | Dates: "01/15/24", "2024-01-15" | Standardize to ISO format |
| Imbalance | 95% non-churners, 5% churners | Use class weights or oversampling |

```
Data Quality Checklist:
├── Check for missing values per column
├── Verify data types are correct
├── Look for outliers (use statistics + visualization)
├── Remove or flag duplicates
├── Standardize categorical values
├── Check class balance for classification
└── Validate data ranges make sense
```

## When to Use

Data quality assessment should happen:
- **Before modeling**: Never skip the exploration phase
- **When performance drops**: Data drift may have occurred
- **When acquiring new data**: Validate before integrating
- **Periodically in production**: Data sources can change

**Time Investment**: Expect to spend 60-80% of your project time on data preparation. This is normal and essential.

**Automation**: Build data validation pipelines that check quality automatically for production systems.

## Key Takeaways

- **"Garbage in, garbage out"**—data quality limits model quality
- Good data is **sufficient, representative, accurate, and unbiased**
- **Missing values** can be handled through removal or imputation
- **Outliers** need investigation—they may be errors or genuine
- **Class imbalance** requires special handling techniques
- **60-80% of ML work** is data preparation—embrace it
- Build **automated validation** for production data pipelines
""",
        "key_points": [
            "Data quality directly limits model quality",
            "Good data is sufficient, representative, accurate, and unbiased",
            "Handle missing values through removal or imputation",
            "Investigate outliers before removing them",
            "Class imbalance needs special techniques",
            "Expect 60-80% of time on data preparation"
        ]
    },
    
    "first-model": {
        "content": """
## What is it?

Building your first model is the moment where theory becomes practice. This lesson walks through the conceptual steps of creating a machine learning model from start to finish, using a simple example to illustrate each phase.

## How it Works

Let's build a model to predict whether a customer will purchase a product based on their browsing behavior.

### Step 1: Define the Problem
```
Goal: Predict purchase probability (Yes/No)
Type: Binary Classification (Supervised Learning)
Success Metric: Accuracy and Recall
```

### Step 2: Prepare the Data
```
Dataset: 10,000 customer sessions
Features:
├── Time on site (minutes)
├── Pages viewed
├── Items added to cart
├── Previous purchases (count)
└── Device type (mobile/desktop)

Label: Purchased (1) or Not (0)
```

### Step 3: Split the Data
```
Total: 10,000 records
├── Training set: 8,000 (80%)
└── Test set: 2,000 (20%)

IMPORTANT: Never evaluate on training data!
```

### Step 4: Choose an Algorithm
For a first model, start simple:
```
Good Starting Algorithms:
├── Logistic Regression (classification)
├── Decision Tree (interpretable)
└── Random Forest (often works well)

Avoid for first attempt:
├── Neural Networks (complex)
└── Ensemble methods (complex)
```

### Step 5: Train the Model
```
Pseudocode:
model = LogisticRegression()
model.fit(X_train, y_train)

What happens:
├── Algorithm sees training examples
├── Finds patterns in features vs labels
└── Adjusts internal weights/parameters
```

### Step 6: Evaluate Performance
```
predictions = model.predict(X_test)

Compare predictions to actual labels:
├── Accuracy: 85% correct overall
├── Precision: 80% of predicted purchases were real
├── Recall: 75% of actual purchases were caught
```

[Diagram: Model Training and Evaluation Flow]

## Example

**Complete First Model Walkthrough:**

```
STEP 1: Load and explore data
├── Check shape: 10,000 rows, 6 columns
├── Check for missing values: 2% in "previous_purchases"
└── Handle missing: Fill with 0 (assume new customer)

STEP 2: Prepare features
├── Numerical: time_on_site, pages_viewed, cart_items, previous_purchases
├── Categorical: device_type → convert to 0 (mobile) / 1 (desktop)
└── Scale numerical features to similar ranges

STEP 3: Split data
├── Shuffle randomly first
├── 80% training, 20% test
└── Keep class balance similar in both sets

STEP 4: Train model
├── Choose: Logistic Regression (simple, interpretable)
├── Train on 8,000 examples
└── Training time: ~1 second

STEP 5: Evaluate
├── Predict on 2,000 test examples
├── Compare to actual labels
└── Accuracy: 85%, Recall: 75%

STEP 6: Iterate
├── Try Random Forest → Accuracy: 88%
├── Tune hyperparameters → Accuracy: 89%
└── Select best model for deployment
```

## When to Use

This workflow applies to most supervised learning projects:
- **Classification**: Spam detection, churn prediction, image classification
- **Regression**: Price prediction, demand forecasting, score prediction

**Best Practices for First Models:**
- Start with a **simple baseline** model
- Get the full pipeline working before optimizing
- Use **cross-validation** for more robust evaluation
- **Iterate**: Simple model → Evaluate → Improve → Repeat

## Key Takeaways

- Start with a **clear problem definition** and success metrics
- **Split data** into training and test sets before any modeling
- Choose a **simple algorithm** first to establish a baseline
- **Evaluate on test data** that the model hasn't seen during training
- **Iterate**: Build simple, evaluate, improve, repeat
- Getting the full **pipeline working** matters more than initial accuracy
- Your first model is a **starting point**, not the final solution
""",
        "key_points": [
            "Start with clear problem definition and success metrics",
            "Always split data before modeling",
            "Begin with simple algorithms to establish baselines",
            "Evaluate only on unseen test data",
            "Iterate: simple model → evaluate → improve → repeat",
            "A working pipeline matters more than initial accuracy"
        ]
    }
}
