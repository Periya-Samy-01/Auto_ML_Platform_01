"""
Classification Topic Content
Lesson content for the Classification topic
"""

# Each lesson follows the structure:
# - What is it?
# - How it works
# - Example
# - When to Use
# - Key Takeaways

CLASSIFICATION_CONTENT = {
    "what-is-classification": {
        "content": """
## What is it?

Classification is a type of supervised machine learning where the goal is to predict which **category** or **class** a data point belongs to. Unlike regression which predicts continuous numbers, classification predicts discrete labels.

Think of it as teaching a computer to sort things into buckets: Is this email spam or not? Is this transaction fraudulent? What species is this flower?

## How it Works

Classification algorithms learn a **decision boundary** that separates different classes in the feature space.

```
Training Process:
1. Input: Features (X) + Known Labels (y)
2. Algorithm finds patterns that distinguish classes
3. Creates decision boundary between classes
4. Output: Model that can predict class of new data

Prediction Process:
1. New data point comes in
2. Model evaluates which side of boundary it falls
3. Assigns class label
4. Optionally provides probability scores
```

The algorithm learns from examples where you already know the correct answer, then applies that knowledge to classify new, unseen examples.

## Example

**Email Spam Classification:**

| Feature | Spam Email | Normal Email |
|---------|------------|--------------|
| Contains "FREE!!!" | Often | Rarely |
| Unknown sender | Usually | Sometimes |
| Has attachments | Sometimes | Sometimes |
| Urgent language | Often | Rarely |

```
Input Features:
├── Word frequencies
├── Sender reputation
├── Link count
├── Writing style
└── Time of sending

Output Classes:
├── Spam (1)
└── Not Spam (0)
```

The classifier learns that emails with "FREE!!!" from unknown senders are likely spam, while emails from colleagues are likely legitimate.

[Diagram: Decision Boundary Separating Two Classes]

## When to Use

Classification is appropriate when:
- **Output is categorical**: You're predicting a discrete label, not a number
- **Categories are known**: You have predefined classes to classify into
- **Labeled data exists**: You have training examples with correct labels
- **Patterns exist**: Features contain information that distinguishes classes

**Common Applications:**
- Medical diagnosis (disease/no disease)
- Customer churn prediction
- Image recognition
- Sentiment analysis
- Credit scoring
- Fraud detection

## Key Takeaways

- Classification predicts **discrete categories**, not continuous values
- Requires **labeled training data** with known class assignments
- Algorithms learn **decision boundaries** to separate classes
- Output can be a class label or probability scores for each class
- Works best when features contain **discriminative information**
- Evaluation uses metrics like accuracy, precision, recall, and F1 score
""",
        "key_points": [
            "Classification predicts discrete categories, not numbers",
            "Requires labeled training data with known classes",
            "Algorithms learn decision boundaries between classes",
            "Can output class labels or probability scores",
            "Common in spam detection, medical diagnosis, fraud detection"
        ]
    },
    
    "binary-vs-multiclass": {
        "content": """
## What is it?

Classification problems are categorized by the number of classes they predict. **Binary classification** has exactly two classes (yes/no, spam/not-spam), while **multi-class classification** has three or more classes (cat/dog/bird, low/medium/high risk).

Understanding this distinction helps you choose the right algorithms and evaluation metrics.

## How it Works

### Binary Classification
Two mutually exclusive classes. The model outputs a probability for one class; the other is simply 1 minus that probability.

```
Binary Examples:
├── Spam detection: Spam vs Not Spam
├── Medical test: Positive vs Negative
├── Churn prediction: Will Leave vs Will Stay
└── Fraud detection: Fraudulent vs Legitimate

Output: Single probability (0 to 1)
├── P(Spam) = 0.85 → Classify as Spam
├── P(Spam) = 0.15 → Classify as Not Spam
└── Threshold typically 0.5 (adjustable)
```

### Multi-class Classification
Three or more mutually exclusive classes. The model outputs probabilities for all classes that sum to 1.

```
Multi-class Examples:
├── Image recognition: Cat / Dog / Bird / Fish
├── Sentiment: Positive / Neutral / Negative
├── Digit recognition: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
└── Priority levels: Low / Medium / High / Critical

Output: Probability distribution
├── P(Cat) = 0.70
├── P(Dog) = 0.25
├── P(Bird) = 0.04
└── P(Fish) = 0.01
→ Classify as Cat
```

### Multi-label Classification
A related but different problem where each sample can belong to **multiple classes simultaneously**.

```
Multi-label Example:
├── Movie genres: Action AND Comedy AND Romance
├── Article tags: Technology AND Business AND AI
└── Each label is independent (not mutually exclusive)
```

## Example

**Customer Support Ticket Classification:**

**Binary Version:**
- Urgent vs Not Urgent

**Multi-class Version:**
- Billing Issue
- Technical Problem
- Feature Request
- Account Access
- General Inquiry

```
Ticket Text: "I can't log into my account and need access urgently"

Binary Output: Urgent (0.92)

Multi-class Output:
├── Account Access: 0.78 ← Winner
├── Technical Problem: 0.15
├── Billing Issue: 0.04
├── Feature Request: 0.02
└── General Inquiry: 0.01
```

## When to Use

| Type | Use When |
|------|----------|
| **Binary** | Only two possible outcomes exist |
| **Multi-class** | 3+ mutually exclusive categories |
| **Multi-label** | Items can belong to multiple categories |

**Algorithm Considerations:**
- Some algorithms naturally handle multi-class (Decision Trees, Random Forest)
- Others need adaptation (Logistic Regression uses One-vs-Rest or One-vs-One)
- Binary problems are generally easier to solve

## Key Takeaways

- **Binary**: Two classes, single probability output
- **Multi-class**: 3+ mutually exclusive classes, probability distribution
- **Multi-label**: Multiple classes can be true simultaneously
- Most algorithms handle binary natively; multi-class may need strategies
- Binary classification metrics extend to multi-class with averaging
- Choose based on your problem's natural structure
""",
        "key_points": [
            "Binary classification: exactly two mutually exclusive classes",
            "Multi-class: three or more mutually exclusive classes",
            "Multi-label: items can belong to multiple classes at once",
            "Binary outputs single probability; multi-class outputs distribution",
            "Some algorithms need adaptation for multi-class problems"
        ]
    },
    
    "logistic-regression": {
        "content": """
## What is it?

Despite its name, **Logistic Regression** is a classification algorithm, not a regression algorithm. It predicts the probability that an instance belongs to a particular class using a logistic (sigmoid) function to map predictions to probabilities between 0 and 1.

It's one of the simplest and most interpretable classification algorithms, making it a great starting point for many problems.

## How it Works

Logistic Regression combines features linearly, then applies the **sigmoid function** to convert the output to a probability.

```
Step 1: Linear Combination
z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b

Step 2: Apply Sigmoid Function
P(y=1) = 1 / (1 + e^(-z))

Step 3: Classification
If P(y=1) > threshold (usually 0.5):
    Predict class 1
Else:
    Predict class 0
```

The sigmoid function has an S-shape that naturally maps any value to the range (0, 1):
- Large positive z → probability near 1
- Large negative z → probability near 0
- z = 0 → probability = 0.5

**Training**: The algorithm finds weights (w) and bias (b) that minimize prediction errors using gradient descent.

[Diagram: Sigmoid Function S-Curve]

## Example

**Loan Default Prediction:**

```
Features:
├── Income: $50,000
├── Debt-to-income ratio: 0.35
├── Credit score: 680
├── Years employed: 3

Learned Weights:
├── Income: -0.00002 (higher income = lower risk)
├── Debt ratio: +2.5 (higher debt = higher risk)
├── Credit score: -0.01 (higher score = lower risk)
├── Years employed: -0.3 (more experience = lower risk)

Calculation:
z = (-0.00002 × 50000) + (2.5 × 0.35) + (-0.01 × 680) + (-0.3 × 3) + bias
z = -1.0 + 0.875 - 6.8 - 0.9 + 8.0 = 0.175

P(Default) = 1 / (1 + e^(-0.175)) = 0.54

Prediction: Slight risk of default (54%)
```

## When to Use

**Good for:**
- Binary classification problems
- When you need probability outputs
- When interpretability is important (coefficients show feature importance)
- Linearly separable or nearly linearly separable data
- As a baseline model before trying complex algorithms

**Limitations:**
- Assumes linear decision boundary
- Struggles with complex, non-linear patterns
- Sensitive to outliers
- Features should be somewhat independent

**Best Practices:**
```
Preprocessing Checklist:
├── Scale features (StandardScaler recommended)
├── Handle missing values
├── Encode categorical variables
├── Consider polynomial features for non-linearity
└── Check for multicollinearity
```

## Key Takeaways

- Logistic Regression is for **classification**, not regression
- Uses **sigmoid function** to output probabilities (0 to 1)
- **Highly interpretable**: coefficients show feature influence
- Assumes **linear decision boundary**
- Great **baseline model** for binary classification
- Fast to train and predict, works well with many features
""",
        "key_points": [
            "Classification algorithm despite its name",
            "Uses sigmoid function to output probabilities 0-1",
            "Highly interpretable—coefficients indicate feature importance",
            "Assumes linear decision boundary between classes",
            "Fast, simple, and excellent as a baseline model"
        ]
    },
    
    "decision-trees": {
        "content": """
## What is it?

A **Decision Tree** is a flowchart-like structure where each internal node represents a test on a feature, each branch represents the outcome of that test, and each leaf node represents a class prediction. It recursively splits the data based on feature values to separate classes.

Decision Trees are intuitive because they mimic human decision-making processes.

## How it Works

The algorithm builds the tree by finding the best feature and threshold to split data at each node.

```
Building a Decision Tree:
1. Start with all data at root
2. Find best feature/threshold to split
3. Split data into child nodes
4. Repeat recursively until:
   ├── Node is pure (single class)
   ├── Max depth reached
   └── Min samples per node reached
5. Assign majority class to leaf nodes
```

**Splitting Criteria:**
- **Gini Impurity**: Measures probability of misclassification
- **Entropy/Information Gain**: Measures disorder reduction
- Lower impurity after split = better split

```
Example Split Decision:
├── Option A: Split on "Age > 30"
│   ├── Gini impurity: 0.35
│   └── Creates mixed groups
└── Option B: Split on "Income > 50k"
    ├── Gini impurity: 0.15
    └── Creates purer groups
→ Choose Option B (lower impurity)
```

[Diagram: Decision Tree Structure with Nodes and Leaves]

## Example

**Customer Churn Prediction Tree:**

```
                    [All Customers]
                          │
              Contract Type = Monthly?
                    /           \\
                 Yes             No
                  │               │
           [High Churn]    Tenure < 12 months?
              (65%)            /         \\
                            Yes           No
                             │             │
                      [Medium]         [Low Churn]
                        (40%)            (10%)

Prediction Path for New Customer:
├── Contract: Monthly? → Yes
└── Predict: High Churn Risk (65%)
```

**Reading the Tree:**
- Start at root
- Follow branches based on feature values
- Reach leaf node for prediction
- Each path is a human-readable rule

## When to Use

**Advantages:**
- **Highly interpretable**: Can visualize and explain decisions
- **No feature scaling needed**: Works with raw values
- **Handles mixed data types**: Numerical and categorical
- **Captures non-linear relationships**: Through multiple splits
- **Fast prediction**: Just follow the tree path

**Disadvantages:**
- **Prone to overfitting**: Can memorize training data
- **Unstable**: Small data changes can create different trees
- **Biased toward features with many levels**
- **Struggles with smooth boundaries**

**Best Practices:**
```
Preventing Overfitting:
├── Set max_depth (e.g., 5-10)
├── Set min_samples_split (e.g., 10-20)
├── Set min_samples_leaf (e.g., 5-10)
├── Use pruning techniques
└── Consider ensemble methods (Random Forest)
```

## Key Takeaways

- Decision Trees split data using **if-then rules**
- **Highly interpretable**: Each path is a readable decision rule
- **No preprocessing needed**: Works with raw features
- **Prone to overfitting**: Use depth limits and pruning
- Foundation for powerful ensembles like **Random Forest**
- Great for understanding feature importance and relationships
""",
        "key_points": [
            "Flowchart-like structure with if-then decision rules",
            "Highly interpretable—can visualize and explain decisions",
            "No feature scaling required",
            "Prone to overfitting—use depth limits and min samples",
            "Foundation for ensemble methods like Random Forest"
        ]
    },
    
    "random-forest": {
        "content": """
## What is it?

**Random Forest** is an ensemble learning method that builds multiple decision trees and combines their predictions. By averaging many trees trained on random subsets of data and features, it reduces overfitting and improves accuracy compared to a single decision tree.

Think of it as "wisdom of the crowd" for machine learning—many diverse trees vote together for better predictions.

## How it Works

Random Forest introduces randomness at two levels:

```
Building Random Forest:
1. Create N trees (e.g., 100)
2. For each tree:
   ├── Bootstrap sample: Random subset of rows (with replacement)
   └── Random features: Use random subset of features at each split
3. Train each tree independently
4. For prediction:
   ├── Each tree votes for a class
   └── Final prediction: Majority vote (or average probabilities)
```

**Key Randomization:**
- **Bagging (Bootstrap Aggregating)**: Each tree sees ~63% of original data
- **Feature Randomness**: Each split considers only √(n_features) features
- Creates diverse, uncorrelated trees

```
Example: 5 Trees Voting
├── Tree 1: Churn
├── Tree 2: No Churn
├── Tree 3: Churn
├── Tree 4: Churn
├── Tree 5: No Churn
└── Final Vote: Churn (3 vs 2)
```

[Diagram: Multiple Trees Contributing to Final Prediction]

## Example

**Fraud Detection with Random Forest:**

```
Individual Trees (simplified):
├── Tree 1: "High transaction + New device = Fraud"
├── Tree 2: "Foreign location + Large amount = Fraud"
├── Tree 3: "Night time + Multiple attempts = Fraud"
└── Each tree has different focus

New Transaction Evaluation:
├── Amount: $2,500 (high)
├── Device: Known
├── Location: Foreign
├── Time: 2 AM
├── Attempts: 3

Tree Predictions:
├── Tree 1: Not Fraud (device is known)
├── Tree 2: Fraud (foreign + large)
├── Tree 3: Fraud (night + multiple attempts)
├── Tree 4: Fraud
├── Tree 5: Not Fraud
└── ... 95 more trees vote ...

Final: 72 Fraud, 28 Not Fraud → Predict Fraud
Probability: 0.72
```

## When to Use

**Advantages:**
- **Excellent accuracy**: Often wins in competitions
- **Robust to overfitting**: Averaging reduces variance
- **Handles high-dimensional data**: Feature randomness helps
- **Built-in feature importance**: From split contributions
- **Parallelizable**: Trees train independently
- **Works out of the box**: Little tuning needed

**Disadvantages:**
- **Less interpretable**: Can't visualize 100+ trees
- **Slower prediction**: Must query all trees
- **Memory intensive**: Stores many trees
- **Not great for streaming data**: Batch training

**Key Hyperparameters:**
```
Tuning Random Forest:
├── n_estimators: Number of trees (100-500 typical)
├── max_depth: Depth limit per tree
├── min_samples_split: Minimum samples to split
├── max_features: Features considered per split
│   ├── 'sqrt': √(n_features) - classification default
│   └── 'log2': log₂(n_features)
└── bootstrap: Whether to use bootstrap sampling
```

## Key Takeaways

- Ensemble of many decision trees with **randomization**
- Combines **bagging** (random rows) + **random features**
- **More accurate** and **less overfitting** than single trees
- Provides **feature importance rankings** automatically
- Excellent default choice—works well with minimal tuning
- Trade-off: **Less interpretable** than single decision tree
""",
        "key_points": [
            "Ensemble of many decision trees with randomization",
            "Uses bagging (random rows) and random feature selection",
            "More accurate and robust than single decision trees",
            "Provides built-in feature importance rankings",
            "Excellent default choice with minimal tuning needed"
        ]
    },
    
    "svm": {
        "content": """
## What is it?

**Support Vector Machine (SVM)** is a powerful classification algorithm that finds the optimal hyperplane to separate classes with the maximum margin. It focuses on the data points closest to the decision boundary (called "support vectors") to define the separation.

SVM excels in high-dimensional spaces and is effective even when the number of features exceeds the number of samples.

## How it Works

SVM finds the hyperplane that maximizes the margin between classes.

```
Key Concepts:
├── Hyperplane: Decision boundary (line in 2D, plane in 3D)
├── Margin: Distance between hyperplane and nearest points
├── Support Vectors: Points closest to the hyperplane
└── Goal: Maximize margin for best generalization

Optimization:
├── Find hyperplane that separates classes
├── Maximize distance to nearest points
└── Only support vectors matter for the boundary
```

**Kernel Trick:**
When data isn't linearly separable, SVM uses kernels to transform data into higher dimensions where it becomes separable.

```
Common Kernels:
├── Linear: For linearly separable data
├── RBF (Gaussian): Maps to infinite dimensions, most versatile
├── Polynomial: Creates polynomial decision boundary
└── Sigmoid: Similar to neural network activation

Example: XOR Problem (not linearly separable in 2D)
├── Original space: Impossible to draw separating line
├── After kernel transformation: Data becomes separable
└── SVM finds boundary in transformed space
```

[Diagram: Maximum Margin Hyperplane with Support Vectors]

## Example

**Image Classification (Handwritten Digits):**

```
Feature Space:
├── Each pixel is a feature (784 features for 28x28 image)
├── High-dimensional space
├── Classes: Digits 0-9

SVM Approach:
├── Use RBF kernel for non-linear boundaries
├── One-vs-One strategy for multi-class
├── Find support vectors for each digit pair

Result:
├── Digit "7" vs "1" boundary defined by ~50 support vectors
├── Digit "8" vs "0" boundary defined by ~80 support vectors
└── Final prediction: Combine all pairwise decisions
```

**Hyperparameter Impact:**
```
C (Regularization):
├── High C: Stricter margin, may overfit
└── Low C: Wider margin, more tolerance for misclassification

Gamma (RBF kernel):
├── High gamma: Each point has small influence (complex boundary)
└── Low gamma: Points have broad influence (smooth boundary)
```

## When to Use

**Advantages:**
- **Effective in high dimensions**: Works when features > samples
- **Memory efficient**: Only stores support vectors
- **Versatile kernels**: Handles non-linear boundaries
- **Robust to overfitting** in high-dimensional space

**Disadvantages:**
- **Slow on large datasets**: Training is O(n² to n³)
- **Sensitive to feature scaling**: Must normalize data
- **No probability outputs**: By default (can enable with Platt scaling)
- **Difficult to interpret**: Especially with non-linear kernels

**Best Practices:**
```
Using SVM Effectively:
├── Always scale features (StandardScaler)
├── Start with RBF kernel
├── Grid search C and gamma
├── Use cross-validation
└── Consider linear kernel for text classification
```

## Key Takeaways

- SVM finds the **maximum margin hyperplane** between classes
- **Support vectors** are the critical training points near the boundary
- **Kernel trick** enables non-linear decision boundaries
- **Excellent for high-dimensional data** (text, images)
- **Requires feature scaling** for good performance
- Can be slow on large datasets—consider for < 100k samples
""",
        "key_points": [
            "Finds maximum margin hyperplane to separate classes",
            "Support vectors are points closest to the decision boundary",
            "Kernel trick enables non-linear classification",
            "Excellent for high-dimensional data (features > samples)",
            "Requires feature scaling and can be slow on large datasets"
        ]
    },
    
    "knn": {
        "content": """
## What is it?

**K-Nearest Neighbors (KNN)** is a simple, intuitive algorithm that classifies a new data point based on the majority class among its K nearest neighbors. It's called a "lazy learner" because it doesn't build an explicit model during training—it just stores the training data and does all the work at prediction time.

The core idea: "You are the company you keep."

## How it Works

```
KNN Classification Process:
1. Store all training data (no explicit training phase)
2. For new data point:
   ├── Calculate distance to ALL training points
   ├── Find K nearest neighbors
   ├── Count class votes among neighbors
   └── Predict majority class

Distance Metrics:
├── Euclidean: √(Σ(x₁-x₂)²) - most common
├── Manhattan: Σ|x₁-x₂| - for grid-like data
├── Minkowski: Generalized distance
└── Cosine: For text/high-dimensional data
```

**Choosing K:**
```
K Value Effects:
├── K = 1: Very sensitive to noise, may overfit
├── K = 3-5: Good starting point
├── K = large: Smoother boundary, may underfit
└── Always use odd K for binary classification (avoid ties)

Rule of thumb: K ≈ √n (where n = training size)
```

[Diagram: KNN with Different K Values]

## Example

**Movie Recommendation by Genre:**

```
Training Data (simplified 2D):
├── Action movies: top-right cluster
├── Comedies: bottom-left cluster
└── Dramas: center area

New Movie Features:
├── Action scenes: 7/10
├── Humor level: 3/10

K=3 Nearest Neighbors:
├── Neighbor 1: Action (distance: 1.2)
├── Neighbor 2: Action (distance: 1.5)
├── Neighbor 3: Drama (distance: 2.0)

Voting: Action = 2, Drama = 1
Prediction: Action movie

K=5 Result might be different:
├── Additional neighbors might be Drama
└── Could change the prediction
```

**Distance Calculation:**
```
Point A: [Action=7, Humor=3]
Point B: [Action=8, Humor=2]

Euclidean Distance:
√((7-8)² + (3-2)²) = √(1 + 1) = 1.41
```

## When to Use

**Advantages:**
- **Simple and intuitive**: Easy to understand and implement
- **No training phase**: Just store data
- **Naturally handles multi-class**: No adaptation needed
- **Non-parametric**: No assumptions about data distribution
- **Adapts to new data**: Just add to training set

**Disadvantages:**
- **Slow prediction**: Must compute distance to all points
- **Memory intensive**: Stores entire training set
- **Curse of dimensionality**: Distances become meaningless in high dimensions
- **Sensitive to irrelevant features**: All features contribute equally
- **Sensitive to scale**: Must normalize features

**Best Practices:**
```
KNN Optimization:
├── Always scale features (StandardScaler)
├── Use cross-validation to find optimal K
├── Consider dimensionality reduction first
├── Use KD-Tree or Ball-Tree for faster queries
└── Remove irrelevant features
```

## Key Takeaways

- **Instance-based learning**: No explicit model, stores all data
- Classifies based on **majority vote of K nearest neighbors**
- **Simple but effective** for many problems
- **Slow at prediction time**: O(n) for each prediction
- **Must scale features**: Different scales distort distances
- Works best with **low dimensions** and **clean data**
""",
        "key_points": [
            "Classifies based on majority vote of K nearest neighbors",
            "Lazy learner—no training, all work done at prediction",
            "Simple and intuitive but slow for large datasets",
            "Sensitive to feature scaling and irrelevant features",
            "Works best with low-dimensional, clean data"
        ]
    },
    
    "naive-bayes": {
        "content": """
## What is it?

**Naive Bayes** is a probabilistic classifier based on Bayes' theorem with a "naive" assumption that all features are independent of each other. Despite this simplifying assumption rarely being true, Naive Bayes works surprisingly well in practice, especially for text classification.

It calculates the probability of each class given the features and predicts the class with the highest probability.

## How it Works

**Bayes' Theorem:**
```
P(Class | Features) = P(Features | Class) × P(Class)
                      ─────────────────────────────────
                              P(Features)

Where:
├── P(Class | Features): Probability of class given features (what we want)
├── P(Features | Class): Likelihood of features given class
├── P(Class): Prior probability of class
└── P(Features): Probability of features (constant, can ignore for comparison)
```

**The "Naive" Assumption:**
```
P(Feature₁, Feature₂, ... | Class) = P(F₁|C) × P(F₂|C) × ...

Assume features are independent:
├── Simplifies calculation dramatically
├── Often not true in reality
└── But still works well in practice!
```

**Variants:**
```
Naive Bayes Types:
├── Gaussian: For continuous features (assumes normal distribution)
├── Multinomial: For count data (word frequencies in text)
├── Bernoulli: For binary features (word presence/absence)
└── Complement: For imbalanced datasets
```

## Example

**Spam Classification:**

```
Training Data Statistics:
├── P(Spam) = 0.30 (30% of emails are spam)
├── P(Not Spam) = 0.70

Word Probabilities:
├── P("free" | Spam) = 0.80
├── P("free" | Not Spam) = 0.05
├── P("meeting" | Spam) = 0.10
├── P("meeting" | Not Spam) = 0.40

New Email: "free meeting tomorrow"

Calculate P(Spam | email):
P(Spam) × P("free"|Spam) × P("meeting"|Spam)
= 0.30 × 0.80 × 0.10 = 0.024

Calculate P(Not Spam | email):
P(Not Spam) × P("free"|Not Spam) × P("meeting"|Not Spam)
= 0.70 × 0.05 × 0.40 = 0.014

Normalize:
├── P(Spam) = 0.024 / (0.024 + 0.014) = 0.63
└── P(Not Spam) = 0.014 / (0.024 + 0.014) = 0.37

Prediction: Spam (63% probability)
```

## When to Use

**Advantages:**
- **Extremely fast**: Both training and prediction
- **Works well with small data**: Good for limited samples
- **Handles high dimensions**: Great for text with many features
- **Works with missing data**: Can ignore missing features
- **Provides probability scores**: Natural probabilistic output

**Disadvantages:**
- **Independence assumption**: Features often correlated
- **Data scarcity problem**: Zero probability if feature unseen
- **Not great for complex relationships**: Linear decision boundaries

**Best Practices:**
```
Naive Bayes Tips:
├── Use Laplace smoothing to handle unseen features
├── Choose variant based on data type:
│   ├── Text data → Multinomial
│   ├── Binary features → Bernoulli
│   └── Continuous features → Gaussian
├── Works as excellent baseline
└── Consider for real-time classification (speed)
```

## Key Takeaways

- Based on **Bayes' theorem** with independence assumption
- **Extremely fast** and efficient
- **Excellent for text classification** (spam, sentiment)
- Works well with **small datasets** and **high dimensions**
- Independence assumption is "naive" but often works
- Great **baseline model** for classification problems
""",
        "key_points": [
            "Probabilistic classifier based on Bayes' theorem",
            "Assumes feature independence (naive assumption)",
            "Extremely fast for training and prediction",
            "Excellent for text classification and high-dimensional data",
            "Great baseline model despite simplifying assumption"
        ]
    },
    
    "imbalanced-data": {
        "content": """
## What is it?

**Imbalanced data** occurs when classes in your dataset have significantly different numbers of samples. For example, fraud detection where 99% of transactions are legitimate and only 1% are fraudulent. Standard classifiers often perform poorly because they tend to predict the majority class.

This is one of the most common challenges in real-world classification problems.

## How it Works

**The Problem:**
```
Imbalanced Dataset Example:
├── Class A (Majority): 9,500 samples (95%)
└── Class B (Minority): 500 samples (5%)

Naive Classifier Behavior:
├── Predicts Class A for everything
├── Achieves 95% accuracy!
├── But 0% recall on Class B
└── Completely useless for detecting Class B
```

**Solutions:**

### 1. Resampling Techniques
```
Oversampling (increase minority):
├── Random: Duplicate minority samples
├── SMOTE: Create synthetic samples by interpolation
└── ADASYN: Focus on hard-to-learn samples

Undersampling (reduce majority):
├── Random: Remove majority samples
├── Tomek Links: Remove borderline majority samples
└── NearMiss: Keep majority samples near boundary

Combined:
└── SMOTE + Tomek Links: Oversample then clean
```

### 2. Algorithm Modifications
```
Class Weights:
├── Penalize misclassifying minority class more heavily
├── weight = n_samples / (n_classes × n_samples_per_class)
└── Most algorithms support class_weight='balanced'

Threshold Adjustment:
├── Default threshold: 0.5
├── Lower threshold for minority class
└── Use precision-recall curve to choose
```

### 3. Evaluation Metrics
```
Avoid Accuracy! Use:
├── Precision: Of predicted positives, how many correct?
├── Recall: Of actual positives, how many detected?
├── F1 Score: Harmonic mean of precision and recall
├── AUC-ROC: Performance across all thresholds
└── Confusion Matrix: Visual understanding
```

[Diagram: SMOTE Creating Synthetic Samples]

## Example

**Credit Card Fraud Detection:**

```
Original Data:
├── Legitimate: 99,000 (99%)
├── Fraudulent: 1,000 (1%)
└── Ratio: 99:1

Strategy 1: Class Weights
├── Fraud weight: 99
├── Legitimate weight: 1
└── Misclassifying fraud costs 99x more

Strategy 2: SMOTE
├── Generate synthetic fraud samples
├── New fraud count: 50,000
├── New ratio: ~2:1
└── Train on balanced data

Results Comparison:
                    Precision  Recall  F1
├── No handling       0.95      0.20   0.33
├── Class weights     0.85      0.75   0.80
└── SMOTE             0.82      0.80   0.81
```

## When to Use

| Technique | Use When |
|-----------|----------|
| **Class Weights** | Simple, good first try |
| **SMOTE** | Need more minority samples, have enough data |
| **Undersampling** | Have lots of majority samples |
| **Threshold Tuning** | Need to control precision/recall tradeoff |

**Decision Guide:**
```
Imbalance Handling Flowchart:
├── Imbalance < 1:10 → Class weights usually sufficient
├── Imbalance 1:10 to 1:100 → Try SMOTE or combined
├── Imbalance > 1:100 → Consider anomaly detection
└── Always evaluate with appropriate metrics!
```

## Key Takeaways

- **Imbalanced data** causes classifiers to favor majority class
- **Accuracy is misleading**: Use precision, recall, F1, AUC
- **Resampling**: Oversample minority or undersample majority
- **SMOTE**: Creates synthetic samples for minority class
- **Class weights**: Penalize majority class misclassifications
- Always **evaluate on original distribution**, not resampled data
""",
        "key_points": [
            "Imbalanced data causes classifiers to favor majority class",
            "Accuracy is misleading—use F1, precision, recall, AUC",
            "SMOTE creates synthetic minority samples",
            "Class weights penalize majority class errors",
            "Always evaluate on original distribution, not resampled data"
        ]
    },
    
    "choosing-algorithm": {
        "content": """
## What is it?

Choosing the right classification algorithm is crucial for building effective models. Different algorithms have different strengths, and the best choice depends on your data characteristics, problem requirements, and constraints like interpretability and speed.

This guide helps you make informed algorithm choices.

## How it Works

**Decision Framework:**

```
Algorithm Selection Factors:
├── Data Size: How many samples and features?
├── Data Type: Numerical, categorical, mixed?
├── Linearity: Are classes linearly separable?
├── Interpretability: Do you need to explain decisions?
├── Speed: Training and prediction time constraints?
└── Accuracy vs. Simplicity: Trade-offs acceptable?
```

**Algorithm Comparison:**

| Algorithm | Best For | Interpretable | Speed | Handles Non-linear |
|-----------|----------|---------------|-------|-------------------|
| Logistic Regression | Linear problems, baseline | ✓ | Fast | ✗ |
| Decision Tree | Explainable rules | ✓ | Fast | ✓ |
| Random Forest | General purpose | ✗ | Medium | ✓ |
| SVM | High dimensions | ✗ | Slow | ✓ (with kernel) |
| KNN | Small datasets | ✓ | Slow pred | ✓ |
| Naive Bayes | Text, probabilistic | ✓ | Very Fast | ✗ |

**Selection Guide:**
```
Start Here:
├── Need interpretability?
│   ├── Yes → Logistic Regression or Decision Tree
│   └── No → Continue
├── Text classification?
│   ├── Yes → Naive Bayes or SVM (linear)
│   └── No → Continue
├── Large dataset (>100k)?
│   ├── Yes → Random Forest, Logistic Regression
│   └── No → Continue
├── High dimensions (features > samples)?
│   ├── Yes → SVM with RBF kernel
│   └── No → Continue
└── Default choice → Random Forest
```

## Example

**Choosing Algorithm for Customer Churn:**

```
Problem Analysis:
├── Samples: 50,000 customers
├── Features: 25 (mix of numerical and categorical)
├── Classes: Binary (Churn / No Churn)
├── Requirement: Need to explain why customers churn
└── Constraint: Weekly batch predictions (speed not critical)

Candidate Evaluation:
├── Logistic Regression
│   ├── ✓ Interpretable coefficients
│   ├── ✓ Fast
│   └── ? May miss non-linear patterns
├── Decision Tree
│   ├── ✓ Very interpretable rules
│   ├── ✓ Handles mixed features
│   └── ✗ May overfit
├── Random Forest
│   ├── ✓ High accuracy
│   ├── ✓ Feature importance
│   └── ✗ Less interpretable
└── Recommendation: Decision Tree (with depth limit) for explainability
    OR Random Forest + SHAP for accuracy with explanations
```

## When to Use

**Quick Reference:**

```
Problem Type → Algorithm
├── Baseline model → Logistic Regression
├── Need explanations → Decision Tree
├── Best accuracy (general) → Random Forest, XGBoost
├── Text classification → Naive Bayes, Linear SVM
├── High-dimensional, small data → SVM
├── Real-time, many features → Naive Bayes
└── Similar items clustering → KNN
```

**Practical Approach:**
```
Recommended Workflow:
1. Start with Logistic Regression (baseline)
2. Try Random Forest (usually better)
3. If RF works, try XGBoost/LightGBM
4. Compare with cross-validation
5. Choose based on:
   ├── Performance metrics
   ├── Interpretability needs
   ├── Deployment constraints
   └── Maintenance complexity
```

## Key Takeaways

- **No single best algorithm**: Depends on your specific problem
- **Start simple**: Logistic Regression as baseline
- **Random Forest**: Excellent default for most problems
- Consider **interpretability** requirements early
- **Data size matters**: Some algorithms don't scale
- Always **compare multiple algorithms** with cross-validation
- **Business constraints** (speed, explainability) often decide
""",
        "key_points": [
            "No single best algorithm—depends on your problem",
            "Start simple with Logistic Regression as baseline",
            "Random Forest is excellent default for most problems",
            "Consider interpretability requirements early",
            "Always compare multiple algorithms with cross-validation"
        ]
    },
    
    "practice-iris": {
        "content": """
## What is it?

The **Iris dataset** is one of the most famous datasets in machine learning, often used for learning classification. It contains measurements from 150 iris flowers from three species (Setosa, Versicolor, Virginica), with four features each. It's small, clean, and perfect for practicing classification techniques.

This lesson walks through a complete classification workflow.

## How it Works

**Dataset Overview:**
```
Iris Dataset:
├── Samples: 150 flowers (50 per species)
├── Features: 4 numerical measurements
│   ├── Sepal length (cm)
│   ├── Sepal width (cm)
│   ├── Petal length (cm)
│   └── Petal width (cm)
├── Classes: 3 species
│   ├── Setosa (easily separable)
│   ├── Versicolor (some overlap with Virginica)
│   └── Virginica (some overlap with Versicolor)
└── Balanced: 50 samples per class
```

**Complete Workflow:**
```
Step 1: Load and Explore Data
├── Check shape: 150 rows × 4 features
├── Check for missing values: None
├── Visualize class distribution: Balanced
└── Explore feature distributions: All reasonable

Step 2: Split Data
├── Training set: 120 samples (80%)
├── Test set: 30 samples (20%)
└── Stratify: Maintain class proportions

Step 3: Preprocess (if needed)
├── Scale features: StandardScaler
└── Iris doesn't need much preprocessing

Step 4: Train Models
├── Logistic Regression
├── Decision Tree
├── Random Forest
├── KNN (K=5)
└── SVM (RBF kernel)

Step 5: Evaluate
├── Accuracy
├── Confusion Matrix
└── Classification Report (per-class metrics)
```

## Example

**Step-by-Step Classification:**

```
# Pseudocode Workflow

# Step 1: Load Data
data = load_iris_dataset()
X = data.features  # Shape: (150, 4)
y = data.labels    # Shape: (150,)

# Step 2: Split
X_train, X_test, y_train, y_test = train_test_split(X, y, 
    test_size=0.2, 
    stratify=y,
    random_state=42)

# Step 3: Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Step 4: Train Multiple Models
models = {
    'Logistic Regression': LogisticRegression(),
    'Decision Tree': DecisionTree(max_depth=3),
    'Random Forest': RandomForest(n_trees=100),
    'KNN': KNeighbors(k=5),
    'SVM': SVM(kernel='rbf')
}

results = {}
for name, model in models:
    model.fit(X_train_scaled, y_train)
    predictions = model.predict(X_test_scaled)
    accuracy = calculate_accuracy(y_test, predictions)
    results[name] = accuracy

# Step 5: Compare Results
print(results)
# Logistic Regression: 0.967
# Decision Tree: 0.933
# Random Forest: 0.967
# KNN: 0.967
# SVM: 0.967
```

**Confusion Matrix Analysis:**
```
Actual vs Predicted (Best Model):
              Setosa  Versicolor  Virginica
Setosa          10         0          0
Versicolor       0         9          1
Virginica        0         0         10

Interpretation:
├── Setosa: Perfect classification
├── Versicolor: 1 misclassified as Virginica
└── Virginica: Perfect classification
└── Overall: 29/30 correct = 96.7%
```

## When to Use

**This Dataset is Good For:**
- Learning classification workflow
- Comparing algorithm performance
- Understanding evaluation metrics
- Practicing data preprocessing
- Quick experiments and prototyping

**Practice Extensions:**
```
Try These Exercises:
├── Feature Selection: Use only 2 features, visualize decision boundary
├── Cross-Validation: 5-fold CV for more robust evaluation
├── Hyperparameter Tuning: Grid search for each algorithm
├── Feature Engineering: Create petal_ratio = length/width
└── Ensemble: Combine predictions from multiple models
```

## Key Takeaways

- **Complete workflow**: Load → Split → Preprocess → Train → Evaluate
- **Multiple algorithms** often achieve similar results on clean data
- **Stratified splitting** maintains class proportions
- **Confusion matrix** shows where mistakes happen
- Simple datasets like Iris are great for **learning and experimentation**
- Real-world data requires more preprocessing and tuning
""",
        "key_points": [
            "Iris is a classic dataset perfect for learning classification",
            "Complete workflow: Load → Split → Preprocess → Train → Evaluate",
            "Multiple algorithms often perform similarly on clean data",
            "Use stratified splitting to maintain class proportions",
            "Confusion matrix reveals where misclassifications occur"
        ]
    }
}
