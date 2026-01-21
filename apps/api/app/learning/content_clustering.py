"""
Clustering Topic Content
Lesson content for the Clustering topic
"""

# Each lesson follows the structure:
# - What is it?
# - How it works
# - Example
# - When to Use
# - Key Takeaways

CLUSTERING_CONTENT = {
    "what-is-clustering": {
        "content": """
## What is it?

**Clustering** is an unsupervised machine learning technique that groups similar data points together without using labeled examples. Unlike classification where you provide correct answers during training, clustering discovers natural groupings in the data on its own.

Think of it as organizing a drawer of mixed items into groups—you don't have labels telling you what goes where, but similar items naturally belong together.

## How it Works

Clustering algorithms find patterns and structure in unlabeled data.

```
Key Concepts:
├── No Labels: Training data has features only, no target
├── Similarity: Points in same cluster are similar
├── Dissimilarity: Points in different clusters are different
└── Goal: Minimize within-cluster variance

Process:
1. Input: Features only (no labels)
2. Algorithm finds natural groupings
3. Each point assigned to a cluster
4. Output: Cluster labels (0, 1, 2, ...)
```

**Types of Clustering:**
```
├── Partition-based: K-Means, K-Medoids
│   └── Divides data into K non-overlapping clusters
├── Hierarchical: Agglomerative, Divisive
│   └── Creates tree of clusters (dendrogram)
├── Density-based: DBSCAN, OPTICS
│   └── Groups dense regions, handles noise
└── Model-based: Gaussian Mixture Models
    └── Assumes data from mixture of distributions
```

## Example

**Customer Segmentation:**

```
Customer Data (no labels):
├── Customer 1: Age=25, Income=$30K, Purchases=10
├── Customer 2: Age=28, Income=$35K, Purchases=12
├── Customer 3: Age=55, Income=$120K, Purchases=5
├── Customer 4: Age=60, Income=$150K, Purchases=3
└── Customer 5: Age=35, Income=$60K, Purchases=20

After Clustering (K=3):
├── Cluster 0: "Young Budget Shoppers"
│   └── Customers 1, 2 (young, moderate income, frequent purchases)
├── Cluster 1: "Affluent Seniors"
│   └── Customers 3, 4 (older, high income, fewer purchases)
└── Cluster 2: "Active Middle-aged"
    └── Customer 5 (mid-age, moderate income, heavy shopper)

Business Actions:
├── Cluster 0: Discount promotions, volume deals
├── Cluster 1: Premium products, quality focus
└── Cluster 2: Loyalty programs, personalized recommendations
```

[Diagram: Scatter Plot with Colored Clusters]

## When to Use

**Good Applications:**
- **Customer segmentation**: Group customers by behavior
- **Anomaly detection**: Identify outliers as separate clusters
- **Image compression**: Group similar colors
- **Document organization**: Topic discovery
- **Exploratory data analysis**: Find hidden patterns

**Not Appropriate When:**
- You have labeled data (use classification instead)
- Clear categories already defined
- Need for predictive modeling on new data
- Interpretable rules required

**Clustering vs Classification:**
```
Clustering (Unsupervised):
├── No labels provided
├── Discovers structure
└── Groups are discovered

Classification (Supervised):
├── Labels provided
├── Learns from examples
└── Categories are predefined
```

## Key Takeaways

- Clustering is **unsupervised**: No labels needed
- Finds **natural groupings** in data
- Similar points grouped together, different points separated
- Common algorithms: **K-Means, Hierarchical, DBSCAN**
- Useful for **segmentation, exploration, anomaly detection**
- Cluster quality is subjective—requires domain knowledge
""",
        "key_points": [
            "Unsupervised learning—no labels needed",
            "Groups similar data points together automatically",
            "Discovers natural patterns and structure in data",
            "Common algorithms: K-Means, Hierarchical, DBSCAN",
            "Useful for segmentation, exploration, and anomaly detection"
        ]
    },
    
    "k-means": {
        "content": """
## What is it?

**K-Means** is the most popular clustering algorithm. It partitions data into K clusters by iteratively assigning points to the nearest cluster center (centroid) and updating centroids based on assigned points. Simple, fast, and works well for many problems.

The "K" in K-Means refers to the number of clusters you specify upfront.

## How it Works

K-Means alternates between two steps until convergence:

```
K-Means Algorithm:
1. Initialize: Randomly place K centroids
2. Assignment Step:
   └── Assign each point to nearest centroid
3. Update Step:
   └── Move each centroid to mean of its points
4. Repeat steps 2-3 until centroids stop moving

Convergence:
├── Typically 10-300 iterations
├── Stops when assignments don't change
└── Or maximum iterations reached
```

**Distance Calculation:**
```
Euclidean Distance (most common):
d = √[(x₁-c₁)² + (x₂-c₂)² + ... + (xₙ-cₙ)²]

Point Assignment:
├── Calculate distance to each centroid
└── Assign to closest one
```

**Initialization Matters:**
```
Random initialization can lead to poor results

K-Means++: Smart initialization
├── Choose first centroid randomly
├── Choose next centroid far from existing ones
├── Probability proportional to distance²
└── Much better convergence
```

[Diagram: K-Means Iteration Steps]

## Example

**Store Location Clustering:**

```
Data: Store coordinates (latitude, longitude)
Goal: Find 3 regional centers for distribution

Iteration 0 (Random centroids):
├── Centroid 1: (40.7, -74.0)  # NYC area
├── Centroid 2: (34.0, -118.2) # LA area
└── Centroid 3: (41.8, -87.6)  # Chicago area

Iteration 1:
├── Assign each store to nearest centroid
├── Recalculate centroids as mean of assigned stores
├── Centroid 1 moves to (40.8, -73.9)
├── Centroid 2 moves to (33.9, -118.1)
└── Centroid 3 moves to (41.9, -87.7)

Final (after convergence):
├── Cluster 1: 45 stores (Northeast region)
├── Cluster 2: 38 stores (West Coast region)
└── Cluster 3: 27 stores (Midwest region)

Result: 3 optimal distribution center locations
```

## When to Use

**Advantages:**
- **Simple and intuitive**: Easy to understand
- **Fast**: O(n × K × i) where i = iterations
- **Scalable**: Works with large datasets
- **Guaranteed convergence**: Will always stop

**Disadvantages:**
- **Must specify K**: Number of clusters upfront
- **Sensitive to initialization**: Use K-Means++
- **Assumes spherical clusters**: Struggles with elongated shapes
- **Sensitive to outliers**: Outliers pull centroids

**Best Practices:**
```
K-Means Checklist:
├── Scale features (StandardScaler)
├── Use K-Means++ initialization
├── Run multiple times, keep best result
├── Use elbow method to choose K
└── Check cluster sizes are reasonable
```

## Key Takeaways

- K-Means partitions data into **K clusters**
- Iterates between **assignment** and **update** steps
- Must specify **K upfront**
- Use **K-Means++** for better initialization
- **Scale features** for best results
- Simple, fast, but assumes **spherical clusters**
""",
        "key_points": [
            "Partitions data into K clusters by minimizing within-cluster distance",
            "Alternates between assignment and centroid update steps",
            "Must specify K (number of clusters) upfront",
            "Use K-Means++ initialization for better results",
            "Simple and fast, but assumes spherical clusters"
        ]
    },
    
    "hierarchical": {
        "content": """
## What is it?

**Hierarchical Clustering** builds a tree of clusters (dendrogram) that shows how clusters merge or split at different levels. Unlike K-Means, you don't need to specify the number of clusters upfront—you can choose K after viewing the dendrogram.

Two approaches: **Agglomerative** (bottom-up) and **Divisive** (top-down).

## How it Works

**Agglomerative (most common):**
```
Bottom-Up Approach:
1. Start: Each point is its own cluster (N clusters)
2. Find two closest clusters
3. Merge them into one cluster
4. Repeat until single cluster remains
5. Cut dendrogram at desired level for K clusters

Linkage Methods (how to measure cluster distance):
├── Single: Minimum distance between points
├── Complete: Maximum distance between points
├── Average: Mean distance between all pairs
└── Ward: Minimize variance increase (most common)
```

**Dendrogram:**
```
A tree showing merge history:

        ┌──────────┐
        │  All     │
        └────┬─────┘
      ┌──────┴───────┐
      │              │
   ┌──┴──┐        ┌──┴──┐
   │     │        │     │
  A,B    C      D,E     F

Cut at different heights = different K
├── Cut high: 2 clusters
├── Cut medium: 3 clusters
└── Cut low: 6 clusters (each point)
```

[Diagram: Dendrogram with Horizontal Cut Lines]

## Example

**Document Similarity Clustering:**

```
Documents: Research papers
Features: Word frequencies (TF-IDF)

Agglomerative Clustering Process:
├── Step 1: Each paper is its own cluster (100 papers)
├── Step 2: Merge two most similar papers
├── Step 3: Continue merging...
└── Final: All papers in one cluster

Dendrogram reveals:
├── Cut at height 2.0: 5 major topics
│   ├── Machine Learning papers
│   ├── Database papers
│   ├── Networking papers
│   ├── Security papers
│   └── Theory papers
├── Cut at height 1.0: 12 subtopics
└── Cut at height 0.5: 25 fine-grained topics

Flexibility: Choose granularity after analysis
```

**Ward Linkage Example:**
```
Cluster A: 10 points, variance = 5.0
Cluster B: 8 points, variance = 4.0

If merged:
├── New cluster: 18 points
├── New variance: 12.0
└── Variance increase: 12.0 - 5.0 - 4.0 = 3.0

Ward minimizes this increase at each merge
```

## When to Use

**Advantages:**
- **No K required**: Choose from dendrogram
- **Hierarchy revealed**: See relationships between clusters
- **Deterministic**: Same result each run
- **Any cluster shape**: Not limited to spherical

**Disadvantages:**
- **Computationally expensive**: O(n³) time, O(n²) space
- **Not scalable**: Struggles with large datasets
- **Irreversible merges**: Early bad merges can't be fixed
- **Dendrogram interpretation**: Subjective

**Choose Linkage Method:**
```
├── Ward: Most clusters of similar size (recommended default)
├── Complete: Compact, spherical clusters
├── Average: Balance between single and complete
└── Single: Can find elongated clusters but prone to chaining
```

## Key Takeaways

- Builds **tree (dendrogram)** of cluster merges
- **Don't need K upfront**: Choose from dendrogram
- **Agglomerative**: Bottom-up, most common
- **Ward linkage**: Usually best default choice
- **Not scalable**: Best for smaller datasets (< 10K points)
- Reveals **hierarchical structure** in data
""",
        "key_points": [
            "Builds a tree (dendrogram) showing cluster relationships",
            "Don't need to specify K upfront—choose from dendrogram",
            "Agglomerative (bottom-up) is most common approach",
            "Ward linkage usually gives best results",
            "Not scalable—best for smaller datasets"
        ]
    },
    
    "dbscan": {
        "content": """
## What is it?

**DBSCAN** (Density-Based Spatial Clustering of Applications with Noise) groups together points that are closely packed and marks points in low-density regions as outliers. Unlike K-Means, it can find clusters of arbitrary shape and automatically detects noise points.

Perfect when you expect irregular cluster shapes or outliers.

## How it Works

DBSCAN uses two parameters: **eps** (neighborhood radius) and **min_samples** (minimum neighbors).

```
Key Concepts:
├── Core Point: Has ≥ min_samples within eps radius
├── Border Point: Within eps of a core point, but < min_samples neighbors
└── Noise Point: Neither core nor border (outlier)

Algorithm:
1. Pick an unvisited point
2. If core point:
   ├── Start new cluster
   └── Add all density-reachable points
3. If not core point:
   └── Mark as noise (may change to border later)
4. Repeat until all points visited
```

**Density Reachability:**
```
Point B is density-reachable from A if:
├── A is a core point
├── B is within eps of A
└── OR B is reachable through chain of core points

This allows clusters to have arbitrary shapes!
```

[Diagram: Core, Border, and Noise Points]

## Example

**Identifying Shopping Mall Hotspots:**

```
Data: Customer location data in mall
Goal: Find high-traffic areas

Parameters:
├── eps = 10 meters
└── min_samples = 20 customers

Results:
├── Cluster 1: Food court area (300 customers)
├── Cluster 2: Main entrance (150 customers)
├── Cluster 3: Electronics section (80 customers)
├── Cluster 4: Fashion wing (120 customers)
└── Noise: 50 scattered customers (explorers)

K-Means would struggle here:
├── Clusters are irregular shapes
├── Food court is elongated
├── Some areas are just wanderers (noise)
└── DBSCAN handles all of this naturally
```

**Parameter Selection:**
```
Finding eps:
├── Plot k-distance graph
├── Find "elbow" point
└── That's your eps

Finding min_samples:
├── Rule of thumb: 2 × dimensions
├── More = stricter clusters
└── Less = more points included
```

## When to Use

**Advantages:**
- **No K required**: Discovers number of clusters
- **Arbitrary shapes**: Not limited to spherical
- **Handles noise**: Outliers marked automatically
- **Robust to outliers**: They don't affect cluster centroids

**Disadvantages:**
- **Sensitive to parameters**: eps and min_samples critical
- **Varying density fails**: Struggles when clusters have different densities
- **High-dimensional problems**: Distance becomes meaningless
- **Memory intensive**: Needs pairwise distances

**DBSCAN vs K-Means:**
```
Choose DBSCAN when:
├── Clusters have irregular shapes
├── Outliers expected in data
├── Number of clusters unknown
└── Clusters have similar density

Choose K-Means when:
├── Clusters are roughly spherical
├── K is known or easily determined
├── Need faster computation
└── Large dataset (DBSCAN slower)
```

## Key Takeaways

- **Density-based**: Finds regions of high density
- **No K required**: Automatically finds cluster count
- **Handles noise**: Outliers labeled separately
- **Arbitrary shapes**: Not limited to spherical clusters
- **Two parameters**: eps (radius) and min_samples (density)
- **Struggles with varying density** across clusters
""",
        "key_points": [
            "Density-based clustering that finds arbitrary-shaped clusters",
            "No need to specify K—discovers cluster count automatically",
            "Handles noise/outliers by labeling them separately",
            "Two key parameters: eps (radius) and min_samples",
            "Struggles when clusters have different densities"
        ]
    },
    
    "choosing-k": {
        "content": """
## What is it?

**Choosing K** (the number of clusters) is one of the most important decisions in clustering. Too few clusters oversimplify; too many create meaningless divisions. Several methods help determine the optimal K, with the **Elbow Method** and **Silhouette Score** being most popular.

## How it Works

**Elbow Method:**
```
Process:
1. Run K-Means for K = 1, 2, 3, ..., 10
2. Calculate Within-Cluster Sum of Squares (WCSS) for each K
3. Plot K vs WCSS
4. Find "elbow" where curve bends
5. That's your optimal K

WCSS = Σ(distance from each point to its centroid)²
├── K=1: Very high (all points in one cluster)
├── K=2: Lower (better fit)
├── K=3: Even lower
└── K=n: Zero (each point is its own cluster)

The elbow is where adding more clusters doesn't help much
```

**Silhouette Score:**
```
For each point, calculate:
a = average distance to points in same cluster
b = average distance to points in nearest other cluster

Silhouette = (b - a) / max(a, b)

Interpretation:
├── +1: Perfect (point is well-matched to cluster)
├── 0: Point is on border between clusters
├── -1: Wrong cluster (point closer to another cluster)

Average across all points for overall score
Best K = highest average silhouette score
```

[Diagram: Elbow Curve and Silhouette Plot]

## Example

**Customer Segmentation - Finding Optimal K:**

```
Dataset: 10,000 customers with purchasing features

Step 1: Elbow Method
K    WCSS
1    150,000
2    80,000   ↓ big drop
3    50,000   ↓ decent drop
4    42,000   ↓ smaller drop ← Elbow!
5    38,000   ↓ marginal
6    35,000

Elbow suggests K = 4

Step 2: Silhouette Score Validation
K    Silhouette
2    0.45
3    0.52
4    0.58 ← Highest
5    0.51
6    0.44

Silhouette confirms K = 4

Step 3: Business Validation
├── Cluster 1: "Price-Sensitive" (3,200 customers)
├── Cluster 2: "Premium Buyers" (2,100 customers)
├── Cluster 3: "Occasional Shoppers" (2,800 customers)
├── Cluster 4: "Loyal Regulars" (1,900 customers)
└── Each cluster is actionable and distinct ✓
```

## When to Use

**Method Comparison:**

| Method | Pros | Cons |
|--------|------|------|
| Elbow | Simple, intuitive | Elbow can be unclear |
| Silhouette | Quantitative score | Slower for large data |
| Gap Statistic | Handles random data | Computationally expensive |
| Domain Knowledge | Most valid | Subjective |

**Decision Framework:**
```
1. Start with elbow method (quick overview)
2. Validate with silhouette score
3. Check with domain expertise:
   ├── Do clusters make business sense?
   ├── Are they actionable?
   └── Is the granularity appropriate?
4. Prefer simpler K if results are similar
```

**Common Pitfalls:**
```
Avoid:
├── Choosing K only by algorithm (domain matters!)
├── Ignoring cluster sizes (one huge, many tiny)
├── Not validating cluster interpretability
└── Overfitting with too many clusters
```

## Key Takeaways

- **Elbow Method**: Plot WCSS vs K, find the bend
- **Silhouette Score**: Measures cluster cohesion and separation
- **Use both**: Algorithms suggest, domain decides
- **Business validation**: Clusters should be meaningful
- **When in doubt**: Prefer fewer clusters (simpler)
- No single "correct" K—it's a **trade-off**
""",
        "key_points": [
            "Elbow Method: Plot WCSS vs K and find the bend",
            "Silhouette Score: Measures how well points fit their clusters",
            "Use both methods together for validation",
            "Domain knowledge is essential—clusters must be meaningful",
            "When in doubt, prefer fewer clusters for simplicity"
        ]
    }
}
