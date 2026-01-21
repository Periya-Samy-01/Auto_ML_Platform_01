"""
Learning Content Data
Static topic and lesson definitions
Content is organized in separate files per topic for maintainability
"""

from typing import List, Dict, Any, Optional

# Import topic-specific content
from .content_ml_basics import ML_BASICS_CONTENT
from .content_classification import CLASSIFICATION_CONTENT
from .content_regression import REGRESSION_CONTENT
from .content_clustering import CLUSTERING_CONTENT
from .content_feature_engineering import FEATURE_ENGINEERING_CONTENT
from .content_model_evaluation import MODEL_EVALUATION_CONTENT
from .content_neural_networks import NEURAL_NETWORKS_CONTENT
from .content_best_practices import BEST_PRACTICES_CONTENT

# Topic definitions matching the frontend cards
TOPICS: Dict[str, Dict[str, Any]] = {
    "ml-basics": {
        "id": "ml-basics",
        "title": "ML Basics",
        "description": "Introduction to machine learning concepts and terminology",
        "icon": "BookOpen",
        "color": "text-blue-400",
        "bg_color": "bg-blue-500/10",
        "difficulty": "BEGINNER",
        "estimated_minutes": 40,
        "lessons": [
            {"id": "what-is-ml", "title": "What is Machine Learning?", "description": "Definition and how it differs from traditional programming", "order": 1, "estimated_minutes": 5},
            {"id": "types-of-ml", "title": "Types of ML", "description": "Supervised, Unsupervised, Reinforcement learning", "order": 2, "estimated_minutes": 5},
            {"id": "ml-pipeline", "title": "The ML Pipeline", "description": "Data → Preprocess → Train → Evaluate → Deploy", "order": 3, "estimated_minutes": 5},
            {"id": "key-terminology", "title": "Key Terminology", "description": "Features, labels, training/test sets, overfitting", "order": 4, "estimated_minutes": 5},
            {"id": "when-to-use-ml", "title": "When to Use ML", "description": "Problem types suitable for ML solutions", "order": 5, "estimated_minutes": 5},
            {"id": "datasets-quality", "title": "Datasets & Data Quality", "description": "Data requirements, handling missing values", "order": 6, "estimated_minutes": 5},
            {"id": "first-model", "title": "Your First Model", "description": "Conceptual walkthrough of building a model", "order": 7, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What is the main difference between supervised and unsupervised learning?",
                "options": [
                    {"id": "a", "text": "Supervised learning uses labeled data, unsupervised does not"},
                    {"id": "b", "text": "Supervised learning is faster"},
                    {"id": "c", "text": "Unsupervised learning requires more data"},
                    {"id": "d", "text": "There is no difference"}
                ],
                "correct_option_id": "a"
            },
            {
                "id": "q2",
                "question": "What is overfitting?",
                "options": [
                    {"id": "a", "text": "When a model is too simple"},
                    {"id": "b", "text": "When a model memorizes training data but fails on new data"},
                    {"id": "c", "text": "When training takes too long"},
                    {"id": "d", "text": "When the dataset is too large"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q3",
                "question": "What is a 'feature' in machine learning?",
                "options": [
                    {"id": "a", "text": "The output prediction"},
                    {"id": "b", "text": "An input variable used to make predictions"},
                    {"id": "c", "text": "The model algorithm"},
                    {"id": "d", "text": "The training time"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "Why do we split data into training and test sets?",
                "options": [
                    {"id": "a", "text": "To make training faster"},
                    {"id": "b", "text": "To reduce storage requirements"},
                    {"id": "c", "text": "To evaluate model performance on unseen data"},
                    {"id": "d", "text": "It's not necessary"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q5",
                "question": "Which is NOT a type of machine learning?",
                "options": [
                    {"id": "a", "text": "Supervised Learning"},
                    {"id": "b", "text": "Reinforcement Learning"},
                    {"id": "c", "text": "Unsupervised Learning"},
                    {"id": "d", "text": "Deterministic Learning"}
                ],
                "correct_option_id": "d"
            }
        ]
    },
    "classification": {
        "id": "classification",
        "title": "Classification",
        "description": "Learn to predict categories and classes from data",
        "icon": "Target",
        "color": "text-green-400",
        "bg_color": "bg-green-500/10",
        "difficulty": "BEGINNER",
        "estimated_minutes": 60,
        "lessons": [
            {"id": "what-is-classification", "title": "What is Classification?", "description": "Predicting discrete categories", "order": 1, "estimated_minutes": 5},
            {"id": "binary-vs-multiclass", "title": "Binary vs Multi-class", "description": "Two-class vs multiple-class problems", "order": 2, "estimated_minutes": 5},
            {"id": "logistic-regression", "title": "Logistic Regression", "description": "Linear approach to classification", "order": 3, "estimated_minutes": 5},
            {"id": "decision-trees", "title": "Decision Trees", "description": "Tree-based splitting decisions", "order": 4, "estimated_minutes": 5},
            {"id": "random-forest", "title": "Random Forest", "description": "Ensemble of decision trees", "order": 5, "estimated_minutes": 5},
            {"id": "svm", "title": "Support Vector Machines", "description": "Hyperplane-based separation", "order": 6, "estimated_minutes": 5},
            {"id": "knn", "title": "K-Nearest Neighbors", "description": "Distance-based classification", "order": 7, "estimated_minutes": 5},
            {"id": "naive-bayes", "title": "Naive Bayes", "description": "Probability-based approach", "order": 8, "estimated_minutes": 5},
            {"id": "imbalanced-data", "title": "Handling Imbalanced Data", "description": "SMOTE, class weights, resampling", "order": 9, "estimated_minutes": 5},
            {"id": "choosing-algorithm", "title": "Choosing the Right Algorithm", "description": "When to use which classifier", "order": 10, "estimated_minutes": 5},
            {"id": "practice-iris", "title": "Practice with Iris Dataset", "description": "Hands-on example", "order": 11, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What is the main difference between classification and regression?",
                "options": [
                    {"id": "a", "text": "Classification predicts categories, regression predicts continuous values"},
                    {"id": "b", "text": "Classification is faster than regression"},
                    {"id": "c", "text": "Regression requires more data"},
                    {"id": "d", "text": "There is no difference"}
                ],
                "correct_option_id": "a"
            },
            {
                "id": "q2",
                "question": "Which algorithm uses the 'majority vote' of nearest neighbors?",
                "options": [
                    {"id": "a", "text": "Logistic Regression"},
                    {"id": "b", "text": "Support Vector Machine"},
                    {"id": "c", "text": "K-Nearest Neighbors"},
                    {"id": "d", "text": "Naive Bayes"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q3",
                "question": "What is Random Forest?",
                "options": [
                    {"id": "a", "text": "A single decision tree with many branches"},
                    {"id": "b", "text": "An ensemble of multiple decision trees with randomization"},
                    {"id": "c", "text": "A type of SVM kernel"},
                    {"id": "d", "text": "A distance metric"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "Which technique creates synthetic samples for minority class?",
                "options": [
                    {"id": "a", "text": "Undersampling"},
                    {"id": "b", "text": "Cross-validation"},
                    {"id": "c", "text": "SMOTE"},
                    {"id": "d", "text": "Grid search"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q5",
                "question": "Why is accuracy misleading for imbalanced datasets?",
                "options": [
                    {"id": "a", "text": "It takes too long to calculate"},
                    {"id": "b", "text": "A model can achieve high accuracy by always predicting the majority class"},
                    {"id": "c", "text": "It only works for binary classification"},
                    {"id": "d", "text": "It requires normalized data"}
                ],
                "correct_option_id": "b"
            }
        ]
    },
    "regression": {
        "id": "regression",
        "title": "Regression",
        "description": "Predict continuous values and understand relationships",
        "icon": "TrendingUp",
        "color": "text-purple-400",
        "bg_color": "bg-purple-500/10",
        "difficulty": "BEGINNER",
        "estimated_minutes": 50,
        "lessons": [
            {"id": "what-is-regression", "title": "What is Regression?", "description": "Predicting continuous values", "order": 1, "estimated_minutes": 5},
            {"id": "linear-regression", "title": "Linear Regression", "description": "The foundational algorithm", "order": 2, "estimated_minutes": 5},
            {"id": "polynomial-regression", "title": "Polynomial Regression", "description": "Capturing non-linear relationships", "order": 3, "estimated_minutes": 5},
            {"id": "ridge-lasso", "title": "Ridge & Lasso", "description": "Regularization techniques", "order": 4, "estimated_minutes": 5},
            {"id": "decision-tree-regression", "title": "Decision Tree Regression", "description": "Tree-based approach", "order": 5, "estimated_minutes": 5},
            {"id": "random-forest-regression", "title": "Random Forest Regression", "description": "Ensemble method", "order": 6, "estimated_minutes": 5},
            {"id": "gradient-boosting", "title": "Gradient Boosting", "description": "XGBoost, LightGBM concepts", "order": 7, "estimated_minutes": 5},
            {"id": "feature-importance", "title": "Feature Importance", "description": "Understanding what drives predictions", "order": 8, "estimated_minutes": 5},
            {"id": "practice-housing", "title": "Practice with Housing Dataset", "description": "Hands-on example", "order": 9, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What type of values does regression predict?",
                "options": [
                    {"id": "a", "text": "Discrete categories"},
                    {"id": "b", "text": "Continuous numerical values"},
                    {"id": "c", "text": "Binary yes/no"},
                    {"id": "d", "text": "Text labels"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q2",
                "question": "What is the purpose of regularization in Ridge and Lasso?",
                "options": [
                    {"id": "a", "text": "To make training faster"},
                    {"id": "b", "text": "To prevent overfitting by penalizing large weights"},
                    {"id": "c", "text": "To increase model complexity"},
                    {"id": "d", "text": "To remove outliers"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q3",
                "question": "Which regularization method can set coefficients exactly to zero?",
                "options": [
                    {"id": "a", "text": "Ridge (L2)"},
                    {"id": "b", "text": "Lasso (L1)"},
                    {"id": "c", "text": "Both Ridge and Lasso"},
                    {"id": "d", "text": "Neither"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "How does Gradient Boosting build its ensemble?",
                "options": [
                    {"id": "a", "text": "Trains trees in parallel on random subsets"},
                    {"id": "b", "text": "Trains trees sequentially, each correcting previous errors"},
                    {"id": "c", "text": "Uses a single deep tree"},
                    {"id": "d", "text": "Averages predictions from independent models"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q5",
                "question": "Which metric measures the proportion of variance explained by the model?",
                "options": [
                    {"id": "a", "text": "MSE (Mean Squared Error)"},
                    {"id": "b", "text": "MAE (Mean Absolute Error)"},
                    {"id": "c", "text": "R² (R-squared)"},
                    {"id": "d", "text": "RMSE (Root Mean Squared Error)"}
                ],
                "correct_option_id": "c"
            }
        ]
    },
    "clustering": {
        "id": "clustering",
        "title": "Clustering",
        "description": "Group similar data points without labeled examples",
        "icon": "Layers",
        "color": "text-orange-400",
        "bg_color": "bg-orange-500/10",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "lessons": [
            {"id": "what-is-clustering", "title": "What is Clustering?", "description": "Unsupervised grouping", "order": 1, "estimated_minutes": 5},
            {"id": "k-means", "title": "K-Means", "description": "Centroid-based clustering", "order": 2, "estimated_minutes": 5},
            {"id": "hierarchical", "title": "Hierarchical Clustering", "description": "Dendrogram approach", "order": 3, "estimated_minutes": 5},
            {"id": "dbscan", "title": "DBSCAN", "description": "Density-based clustering", "order": 4, "estimated_minutes": 5},
            {"id": "choosing-k", "title": "Choosing K", "description": "Elbow method, silhouette score", "order": 5, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What makes clustering 'unsupervised'?",
                "options": [
                    {"id": "a", "text": "It runs without human oversight"},
                    {"id": "b", "text": "It learns from data without labeled examples"},
                    {"id": "c", "text": "It doesn't require a computer"},
                    {"id": "d", "text": "It uses random initialization"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q2",
                "question": "What does the 'K' in K-Means represent?",
                "options": [
                    {"id": "a", "text": "The number of features"},
                    {"id": "b", "text": "The number of iterations"},
                    {"id": "c", "text": "The number of clusters"},
                    {"id": "d", "text": "The number of samples"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q3",
                "question": "Which algorithm can find clusters of arbitrary shape and detect outliers?",
                "options": [
                    {"id": "a", "text": "K-Means"},
                    {"id": "b", "text": "Hierarchical Clustering"},
                    {"id": "c", "text": "DBSCAN"},
                    {"id": "d", "text": "Linear Regression"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q4",
                "question": "What is the Elbow Method used for?",
                "options": [
                    {"id": "a", "text": "Choosing the optimal number of clusters (K)"},
                    {"id": "b", "text": "Selecting features"},
                    {"id": "c", "text": "Removing outliers"},
                    {"id": "d", "text": "Calculating distances"}
                ],
                "correct_option_id": "a"
            },
            {
                "id": "q5",
                "question": "What does a high silhouette score indicate?",
                "options": [
                    {"id": "a", "text": "Points are poorly clustered"},
                    {"id": "b", "text": "Points are well-matched to their clusters"},
                    {"id": "c", "text": "Too many clusters"},
                    {"id": "d", "text": "Too few clusters"}
                ],
                "correct_option_id": "b"
            }
        ]
    },
    "feature-engineering": {
        "id": "feature-engineering",
        "title": "Feature Engineering",
        "description": "Transform raw data into features for better models",
        "icon": "Wrench",
        "color": "text-cyan-400",
        "bg_color": "bg-cyan-500/10",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 35,
        "lessons": [
            {"id": "what-is-feature-engineering", "title": "What is Feature Engineering?", "description": "Why features matter", "order": 1, "estimated_minutes": 5},
            {"id": "missing-data", "title": "Handling Missing Data", "description": "Imputation strategies", "order": 2, "estimated_minutes": 5},
            {"id": "encoding-categorical", "title": "Encoding Categorical Variables", "description": "One-hot, label, target encoding", "order": 3, "estimated_minutes": 5},
            {"id": "scaling", "title": "Scaling & Normalization", "description": "StandardScaler, MinMaxScaler", "order": 4, "estimated_minutes": 5},
            {"id": "feature-selection", "title": "Feature Selection", "description": "Removing irrelevant features", "order": 5, "estimated_minutes": 5},
            {"id": "feature-creation", "title": "Feature Creation", "description": "Polynomial, interaction features", "order": 6, "estimated_minutes": 5},
            {"id": "dimensionality-reduction", "title": "Dimensionality Reduction", "description": "PCA basics", "order": 7, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "Why is feature engineering often more important than algorithm choice?",
                "options": [
                    {"id": "a", "text": "It's faster to do"},
                    {"id": "b", "text": "Good features help any algorithm find patterns more easily"},
                    {"id": "c", "text": "It requires less domain knowledge"},
                    {"id": "d", "text": "It's always automated"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q2",
                "question": "What is the risk of using mean imputation for missing values?",
                "options": [
                    {"id": "a", "text": "It's too slow"},
                    {"id": "b", "text": "It can reduce variance and distort relationships"},
                    {"id": "c", "text": "It adds too many features"},
                    {"id": "d", "text": "It only works for categorical data"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q3",
                "question": "Which encoding creates the most new columns?",
                "options": [
                    {"id": "a", "text": "Label Encoding"},
                    {"id": "b", "text": "One-Hot Encoding"},
                    {"id": "c", "text": "Target Encoding"},
                    {"id": "d", "text": "Ordinal Encoding"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "When fitting a scaler, what data should you use?",
                "options": [
                    {"id": "a", "text": "Test data only"},
                    {"id": "b", "text": "Training data only"},
                    {"id": "c", "text": "Both training and test data"},
                    {"id": "d", "text": "Validation data only"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q5",
                "question": "What does PCA optimize for when reducing dimensions?",
                "options": [
                    {"id": "a", "text": "Minimizing computation time"},
                    {"id": "b", "text": "Maximizing preserved variance"},
                    {"id": "c", "text": "Maximizing the number of features"},
                    {"id": "d", "text": "Minimizing feature correlations"}
                ],
                "correct_option_id": "b"
            }
        ]
    },
    "model-evaluation": {
        "id": "model-evaluation",
        "title": "Model Evaluation",
        "description": "Metrics and techniques to assess model performance",
        "icon": "BarChart3",
        "color": "text-pink-400",
        "bg_color": "bg-pink-500/10",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 30,
        "lessons": [
            {"id": "why-evaluation", "title": "Why Evaluation Matters", "description": "Avoiding overfitting", "order": 1, "estimated_minutes": 5},
            {"id": "train-test-split", "title": "Train/Test/Validation Split", "description": "Data partitioning strategies", "order": 2, "estimated_minutes": 5},
            {"id": "classification-metrics", "title": "Classification Metrics", "description": "Accuracy, Precision, Recall, F1, AUC-ROC", "order": 3, "estimated_minutes": 5},
            {"id": "regression-metrics", "title": "Regression Metrics", "description": "MSE, RMSE, MAE, R²", "order": 4, "estimated_minutes": 5},
            {"id": "confusion-matrix", "title": "Confusion Matrix", "description": "Reading and interpreting", "order": 5, "estimated_minutes": 5},
            {"id": "cross-validation", "title": "Cross-Validation", "description": "K-fold, stratified sampling", "order": 6, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "Why might a model with 99% training accuracy perform poorly in production?",
                "options": [
                    {"id": "a", "text": "The training data was too clean"},
                    {"id": "b", "text": "The model overfit to training data and doesn't generalize"},
                    {"id": "c", "text": "99% is not high enough"},
                    {"id": "d", "text": "The test set was too small"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q2",
                "question": "Which metric is most appropriate when false negatives are very costly (e.g., missing a disease)?",
                "options": [
                    {"id": "a", "text": "Precision"},
                    {"id": "b", "text": "Accuracy"},
                    {"id": "c", "text": "Recall"},
                    {"id": "d", "text": "Specificity"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q3",
                "question": "What does R² = 0.85 mean in regression?",
                "options": [
                    {"id": "a", "text": "85% of predictions are correct"},
                    {"id": "b", "text": "The model explains 85% of the variance in the target"},
                    {"id": "c", "text": "The average error is 15%"},
                    {"id": "d", "text": "85% of features are used"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "In a confusion matrix, what do the diagonal elements represent?",
                "options": [
                    {"id": "a", "text": "Incorrect predictions"},
                    {"id": "b", "text": "Correct predictions"},
                    {"id": "c", "text": "False positives"},
                    {"id": "d", "text": "False negatives"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q5",
                "question": "What is the main benefit of K-fold cross-validation?",
                "options": [
                    {"id": "a", "text": "It's faster than a single split"},
                    {"id": "b", "text": "It gives a more reliable performance estimate"},
                    {"id": "c", "text": "It increases the training data"},
                    {"id": "d", "text": "It eliminates the need for a test set"}
                ],
                "correct_option_id": "b"
            }
        ]
    },
    "neural-networks": {
        "id": "neural-networks",
        "title": "Neural Networks",
        "description": "Introduction to deep learning fundamentals",
        "icon": "Brain",
        "color": "text-red-400",
        "bg_color": "bg-red-500/10",
        "difficulty": "ADVANCED",
        "estimated_minutes": 70,
        "lessons": [
            {"id": "what-are-neural-networks", "title": "What are Neural Networks?", "description": "Biological inspiration", "order": 1, "estimated_minutes": 5},
            {"id": "perceptrons", "title": "Perceptrons", "description": "Single-layer networks", "order": 2, "estimated_minutes": 5},
            {"id": "mlp", "title": "Multi-Layer Perceptrons", "description": "Hidden layers", "order": 3, "estimated_minutes": 5},
            {"id": "activation-functions", "title": "Activation Functions", "description": "ReLU, Sigmoid, Tanh", "order": 4, "estimated_minutes": 5},
            {"id": "forward-propagation", "title": "Forward Propagation", "description": "How data flows", "order": 5, "estimated_minutes": 5},
            {"id": "loss-functions", "title": "Loss Functions", "description": "Measuring error", "order": 6, "estimated_minutes": 5},
            {"id": "backpropagation", "title": "Backpropagation", "description": "Learning from errors", "order": 7, "estimated_minutes": 5},
            {"id": "gradient-descent", "title": "Gradient Descent", "description": "Optimization basics", "order": 8, "estimated_minutes": 5},
            {"id": "learning-rate", "title": "Learning Rate", "description": "Tuning convergence", "order": 9, "estimated_minutes": 5},
            {"id": "overfitting-nn", "title": "Overfitting in Neural Networks", "description": "Dropout, regularization", "order": 10, "estimated_minutes": 5},
            {"id": "batch-normalization", "title": "Batch Normalization", "description": "Stabilizing training", "order": 11, "estimated_minutes": 5},
            {"id": "hyperparameter-tuning", "title": "Hyperparameter Tuning", "description": "Architecture choices", "order": 12, "estimated_minutes": 5},
            {"id": "when-to-use-nn", "title": "When to Use Neural Networks", "description": "Use cases and limitations", "order": 13, "estimated_minutes": 5},
            {"id": "frameworks", "title": "Deep Learning Frameworks", "description": "TensorFlow, PyTorch overview", "order": 14, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What is the main limitation of a single perceptron?",
                "options": [
                    {"id": "a", "text": "It's too slow"},
                    {"id": "b", "text": "It can only solve linearly separable problems"},
                    {"id": "c", "text": "It requires too much memory"},
                    {"id": "d", "text": "It can't use activation functions"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q2",
                "question": "What is the most commonly used activation function for hidden layers?",
                "options": [
                    {"id": "a", "text": "Sigmoid"},
                    {"id": "b", "text": "Tanh"},
                    {"id": "c", "text": "ReLU"},
                    {"id": "d", "text": "Softmax"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q3",
                "question": "What does backpropagation calculate?",
                "options": [
                    {"id": "a", "text": "The forward pass predictions"},
                    {"id": "b", "text": "The gradients of the loss with respect to weights"},
                    {"id": "c", "text": "The batch size"},
                    {"id": "d", "text": "The number of epochs"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "What is dropout used for?",
                "options": [
                    {"id": "a", "text": "Making training faster"},
                    {"id": "b", "text": "Reducing memory usage"},
                    {"id": "c", "text": "Preventing overfitting"},
                    {"id": "d", "text": "Increasing model capacity"}
                ],
                "correct_option_id": "c"
            },
            {
                "id": "q5",
                "question": "When might tree-based methods outperform neural networks?",
                "options": [
                    {"id": "a", "text": "Image classification"},
                    {"id": "b", "text": "Natural language processing"},
                    {"id": "c", "text": "Structured tabular data with meaningful features"},
                    {"id": "d", "text": "Speech recognition"}
                ],
                "correct_option_id": "c"
            }
        ]
    },
    "best-practices": {
        "id": "best-practices",
        "title": "Best Practices",
        "description": "Tips and tricks for successful ML projects",
        "icon": "Lightbulb",
        "color": "text-yellow-400",
        "bg_color": "bg-yellow-500/10",
        "difficulty": "BEGINNER",
        "estimated_minutes": 20,
        "lessons": [
            {"id": "data-quality", "title": "Data Quality First", "description": "Garbage in, garbage out", "order": 1, "estimated_minutes": 5},
            {"id": "start-simple", "title": "Start Simple", "description": "Baseline models before complexity", "order": 2, "estimated_minutes": 5},
            {"id": "experiment-tracking", "title": "Experiment Tracking", "description": "Logging experiments", "order": 3, "estimated_minutes": 5},
            {"id": "deployment", "title": "Model Deployment Considerations", "description": "Production readiness", "order": 4, "estimated_minutes": 5},
        ],
        "quiz": [
            {
                "id": "q1",
                "question": "What does 'Garbage in, garbage out' mean in ML?",
                "options": [
                    {"id": "a", "text": "Models should be thrown away after use"},
                    {"id": "b", "text": "Bad data quality leads to bad model performance"},
                    {"id": "c", "text": "Complex models are wasteful"},
                    {"id": "d", "text": "You should delete failed experiments"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q2",
                "question": "Why should you start with a simple model?",
                "options": [
                    {"id": "a", "text": "Simple models are always more accurate"},
                    {"id": "b", "text": "To establish a baseline and verify your pipeline"},
                    {"id": "c", "text": "Complex models don't work"},
                    {"id": "d", "text": "Simple models are the only option"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q3",
                "question": "What should you track in ML experiments?",
                "options": [
                    {"id": "a", "text": "Only the final accuracy"},
                    {"id": "b", "text": "Parameters, metrics, code version, and artifacts"},
                    {"id": "c", "text": "Just the model file"},
                    {"id": "d", "text": "Nothing, it's not important"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q4",
                "question": "Why is model monitoring important in production?",
                "options": [
                    {"id": "a", "text": "To slow down the model"},
                    {"id": "b", "text": "To detect data drift and performance degradation"},
                    {"id": "c", "text": "To increase costs"},
                    {"id": "d", "text": "It's not important"}
                ],
                "correct_option_id": "b"
            },
            {
                "id": "q5",
                "question": "What is A/B testing used for in model deployment?",
                "options": [
                    {"id": "a", "text": "Training the model faster"},
                    {"id": "b", "text": "Comparing model versions on real traffic before full rollout"},
                    {"id": "c", "text": "Reducing model size"},
                    {"id": "d", "text": "Data preprocessing"}
                ],
                "correct_option_id": "b"
            }
        ]
    },
}


def get_all_topics() -> List[Dict[str, Any]]:
    """Get all topic definitions"""
    return list(TOPICS.values())


def get_topic_by_id(topic_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific topic by ID"""
    return TOPICS.get(topic_id)


def get_lesson_by_id(topic_id: str, lesson_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific lesson from a topic with full content"""
    topic = TOPICS.get(topic_id)
    if not topic:
        return None
    
    for lesson in topic.get("lessons", []):
        if lesson["id"] == lesson_id:
            # Create a copy with content merged in
            result = lesson.copy()
            
            # Get content from topic-specific content modules
            content_data = get_lesson_content(topic_id, lesson_id)
            if content_data:
                result["content"] = content_data.get("content")
                result["key_points"] = content_data.get("key_points")
            
            return result
    return None


def get_lesson_content(topic_id: str, lesson_id: str) -> Optional[Dict[str, Any]]:
    """Get lesson content from topic-specific content modules"""
    content_map = {
        "ml-basics": ML_BASICS_CONTENT,
        "classification": CLASSIFICATION_CONTENT,
        "regression": REGRESSION_CONTENT,
        "clustering": CLUSTERING_CONTENT,
        "feature-engineering": FEATURE_ENGINEERING_CONTENT,
        "model-evaluation": MODEL_EVALUATION_CONTENT,
        "neural-networks": NEURAL_NETWORKS_CONTENT,
        "best-practices": BEST_PRACTICES_CONTENT,
    }
    
    topic_content = content_map.get(topic_id)
    if topic_content:
        return topic_content.get(lesson_id)
    return None
