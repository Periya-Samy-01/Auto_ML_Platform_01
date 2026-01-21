"""
Neural Networks Topic Content
Lesson content for the Neural Networks topic
"""

NEURAL_NETWORKS_CONTENT = {
    "what-are-neural-networks": {
        "content": """
## What is it?

**Neural Networks** are computing systems inspired by biological neural networks in the brain. They consist of interconnected nodes (neurons) organized in layers that can learn complex patterns from data. Neural networks form the foundation of deep learning.

They excel at tasks where traditional algorithms struggle: image recognition, natural language understanding, and speech recognition.

## How it Works

**Biological Inspiration:**
```
Biological Neuron:
├── Dendrites: Receive signals from other neurons
├── Cell Body: Processes signals
├── Axon: Transmits signal to other neurons
└── Synapse: Connection strength between neurons

Artificial Neuron:
├── Inputs (x): Receive values from previous layer
├── Weights (w): Connection strengths (learned)
├── Bias (b): Threshold adjustment
├── Activation: Non-linear transformation
└── Output: Passed to next layer
```

**Basic Structure:**
```
Input Layer → Hidden Layer(s) → Output Layer

Layer Roles:
├── Input: Receives raw features
├── Hidden: Learns representations
└── Output: Produces predictions
```

## Example

**Handwritten Digit Recognition:**

```
Task: Classify images of digits (0-9)

Input:
├── 28×28 pixel image = 784 input neurons
├── Each pixel = one input value (0-255)

Network:
├── Input Layer: 784 neurons
├── Hidden Layer 1: 128 neurons
├── Hidden Layer 2: 64 neurons
└── Output Layer: 10 neurons (one per digit)

Process:
├── Image pixels → Input layer
├── Hidden layers extract features:
│   ├── Layer 1: Edges, curves
│   └── Layer 2: Loops, lines
├── Output layer: Probability per digit
└── Highest probability = prediction
```

[Diagram: Neural Network Architecture with Layers]

## When to Use

**Neural Networks Excel At:**
```
├── Image recognition and classification
├── Natural language processing
├── Speech recognition
├── Game playing (reinforcement learning)
├── Complex pattern recognition
└── Problems with lots of data
```

**NOT Ideal For:**
```
├── Small datasets (need lots of data)
├── Need for interpretability
├── Tabular data (tree methods often better)
├── Real-time with limited compute
└── When simpler models work
```

## Key Takeaways

- Inspired by **biological neurons** but simpler
- Consist of **layers** of interconnected neurons
- Learn **complex patterns** through training
- Require **lots of data** to train effectively
- Foundation of **deep learning** revolution
- Trade-off: Powerful but **less interpretable**
""",
        "key_points": [
            "Inspired by biological neurons in the brain",
            "Organized in layers: input, hidden, output",
            "Learn complex patterns through training",
            "Require lots of data for effective training",
            "Powerful but less interpretable than simpler models"
        ]
    },
    
    "perceptrons": {
        "content": """
## What is it?

The **Perceptron** is the simplest neural network—a single artificial neuron. It takes multiple inputs, applies weights, sums them, and passes through an activation function to produce an output. Despite its simplicity, it's the building block of all neural networks.

Introduced by Frank Rosenblatt in 1958.

## How it Works

```
Perceptron Formula:
output = activation(Σ(wᵢ × xᵢ) + b)

Where:
├── xᵢ = input values
├── wᵢ = weights (learned)
├── b = bias term
├── Σ = weighted sum
└── activation = step function (originally)
```

**Step Function (Original):**
```
if weighted_sum > 0:
    output = 1
else:
    output = 0

Creates binary classification
```

**Learning Rule:**
```
For each training example:
1. Compute output
2. If wrong:
   └── Adjust weights: w = w + α × (target - output) × x
3. Repeat until correct

α = learning rate (small value like 0.01)
```

## Example

**AND Gate with Perceptron:**

```
AND Truth Table:
x₁  x₂  |  AND
0   0   |   0
0   1   |   0
1   0   |   0
1   1   |   1

Training a Perceptron:

Initial: w₁=0.5, w₂=0.5, b=-0.7, threshold=0

Test (1,1):
├── sum = 0.5×1 + 0.5×1 + (-0.7) = 0.3
├── 0.3 > 0 → output = 1 ✓

Test (0,1):
├── sum = 0.5×0 + 0.5×1 + (-0.7) = -0.2
├── -0.2 < 0 → output = 0 ✓

Test (1,0):
├── sum = 0.5×1 + 0.5×0 + (-0.7) = -0.2
├── -0.2 < 0 → output = 0 ✓

Test (0,0):
├── sum = 0.5×0 + 0.5×0 + (-0.7) = -0.7
├── -0.7 < 0 → output = 0 ✓

Perceptron learned AND!
```

## When to Use

**Capable Of:**
```
├── Linearly separable problems
├── AND, OR, NOT gates
├── Simple binary classification
└── Building block for larger networks
```

**Limitation - XOR Problem:**
```
XOR cannot be solved by single perceptron:
x₁  x₂  |  XOR
0   0   |   0
0   1   |   1
1   0   |   1
1   1   |   0

No single line can separate 1s from 0s!
Solution: Multiple layers (MLP)
```

## Key Takeaways

- **Simplest neural network**: Single neuron
- **Weighted sum** of inputs + bias + activation
- Can learn **linearly separable** patterns only
- **XOR problem**: Cannot solve without multiple layers
- Foundation for **multi-layer perceptrons**
- Historical importance in neural network development
""",
        "key_points": [
            "Simplest neural network—single artificial neuron",
            "Computes weighted sum of inputs plus bias",
            "Limited to linearly separable problems",
            "Cannot solve XOR problem (needs multiple layers)",
            "Foundation for multi-layer perceptrons"
        ]
    },
    
    "mlp": {
        "content": """
## What is it?

A **Multi-Layer Perceptron (MLP)** is a neural network with one or more hidden layers between input and output. The hidden layers allow the network to learn non-linear patterns that single perceptrons cannot, like the XOR problem.

Also called a "feedforward neural network."

## How it Works

```
MLP Structure:
Input Layer → Hidden Layer(s) → Output Layer

Data flows forward (feedforward):
├── No cycles or loops
├── Each neuron connects to all neurons in next layer
└── Called "fully connected" or "dense" layers
```

**Universal Approximation:**
```
With enough neurons in hidden layer:
├── MLP can approximate ANY continuous function
├── This is why neural networks are so powerful
└── More layers = more complex functions
```

**Why Hidden Layers Work:**
```
Single layer: Can only draw one line (linear)

Two layers: Can combine multiple lines
├── Hidden neurons each compute a line
├── Output combines them
└── Creates non-linear boundaries

More layers:
├── Even more complex boundaries
├── Hierarchical feature learning
└── But harder to train
```

## Example

**Solving XOR with MLP:**

```
XOR Problem:
(0,0) → 0    (1,1) → 0
(0,1) → 1    (1,0) → 1

MLP Architecture:
├── Input: 2 neurons
├── Hidden: 2 neurons (with ReLU)
└── Output: 1 neuron (with sigmoid)

How it works:
├── Hidden neuron 1: Activates for (0,1) and (1,0) and (1,1)
├── Hidden neuron 2: Activates for (1,1) only
├── Output combines: hidden1 AND NOT hidden2
└── Result: Correct XOR!

Visualization:
Hidden layer creates new representation:
├── (0,0) → (0, 0) → 0
├── (0,1) → (1, 0) → 1
├── (1,0) → (1, 0) → 1
├── (1,1) → (1, 1) → 0
Now linearly separable!
```

**Hidden Layer as Feature Extraction:**
```
Image Classification:
├── Layer 1: Edges, corners
├── Layer 2: Shapes, textures
├── Layer 3: Object parts
├── Layer 4: Whole objects
└── Output: Class probabilities
```

## When to Use

**MLP Good For:**
```
├── Non-linear classification
├── Regression with complex patterns
├── Tabular data with many features
├── When simpler models fail
└── As baseline deep learning model
```

**Architecture Choices:**
```
Width (neurons per layer):
├── More neurons = more capacity
├── Risk of overfitting if too many
└── Common: 64, 128, 256, 512

Depth (number of layers):
├── More layers = more abstraction
├── Harder to train (vanishing gradients)
└── Common for tabular: 2-5 layers

Rule of thumb:
├── Start small, increase if underfitting
└── Use validation set to detect overfitting
```

## Key Takeaways

- **Hidden layers** enable non-linear pattern learning
- **Universal approximator**: Can learn any function
- Deeper networks learn **hierarchical features**
- **Width and depth** are key architectural choices
- Start simple, add complexity as needed
- More layers = more power but harder to train
""",
        "key_points": [
            "Hidden layers enable non-linear pattern learning",
            "Universal approximator—can learn any function",
            "Deeper networks learn hierarchical features",
            "Width and depth are key architectural choices",
            "Start simple, add complexity as needed"
        ]
    },
    
    "activation-functions": {
        "content": """
## What is it?

**Activation functions** introduce non-linearity into neural networks. Without them, stacking layers would be equivalent to a single linear layer. They determine whether a neuron "fires" and how strongly.

The choice of activation function significantly impacts training and performance.

## How it Works

**Why Non-linearity?**
```
Without activation functions:
├── Layer 1: y = W₁x + b₁
├── Layer 2: y = W₂(W₁x + b₁) + b₂
├── Simplifies to: y = Wx + b
└── Just a linear function! No power in depth.

With activation functions:
├── Non-linear transformation at each layer
├── Network can learn complex patterns
└── Depth becomes meaningful
```

**Common Activation Functions:**

```
ReLU (Rectified Linear Unit):
f(x) = max(0, x)
├── Most popular for hidden layers
├── Fast to compute
├── Can cause "dying ReLU" (neurons output 0)
└── Use for: Hidden layers (default)

Sigmoid:
f(x) = 1 / (1 + e^(-x))
├── Output range: (0, 1)
├── Good for probabilities
├── Vanishing gradient problem
└── Use for: Binary classification output

Tanh:
f(x) = (e^x - e^(-x)) / (e^x + e^(-x))
├── Output range: (-1, 1)
├── Zero-centered (unlike sigmoid)
├── Still has vanishing gradient
└── Use for: Hidden layers (sometimes)

Softmax:
f(xᵢ) = e^xᵢ / Σe^xⱼ
├── Outputs sum to 1
├── Multi-class probabilities
└── Use for: Multi-class classification output
```

## Example

**Choosing Activation Functions:**

```
Binary Classification (Spam Detection):
├── Hidden layers: ReLU
└── Output layer: Sigmoid (probability 0-1)

Multi-class Classification (Digit Recognition):
├── Hidden layers: ReLU
└── Output layer: Softmax (10 probabilities sum to 1)

Regression (House Prices):
├── Hidden layers: ReLU
└── Output layer: Linear (no activation, or ReLU if positive only)

Example flow for digit "7":
Input (784 pixels)
    ↓ ReLU
Hidden 1 (128 neurons): [0, 2.3, 0, 1.5, 0.8, ...]
    ↓ ReLU
Hidden 2 (64 neurons): [0.5, 0, 3.2, 0, 1.1, ...]
    ↓ Softmax
Output (10 neurons): [0.01, 0.02, 0.01, 0.02, 0.01, 0.01, 0.03, 0.85, 0.02, 0.02]
                                                              ↑
                                                          Predicted: 7
```

## When to Use

**Quick Reference:**

| Activation | Use For | Output Range |
|------------|---------|--------------|
| ReLU | Hidden layers (default) | [0, ∞) |
| Leaky ReLU | Hidden (if dying ReLU) | (-∞, ∞) |
| Sigmoid | Binary output | (0, 1) |
| Softmax | Multi-class output | (0, 1), sum=1 |
| Tanh | Hidden (alternative) | (-1, 1) |
| Linear | Regression output | (-∞, ∞) |

**Vanishing Gradient Problem:**
```
Sigmoid/Tanh gradients approach 0 for large inputs
├── Weights don't update (learning stops)
├── Deep networks affected most
└── Solution: Use ReLU in hidden layers
```

## Key Takeaways

- **Enable non-linearity**: Make deep networks powerful
- **ReLU**: Default for hidden layers (fast, effective)
- **Sigmoid**: Binary classification output
- **Softmax**: Multi-class classification output
- **Vanishing gradients**: Problem with sigmoid/tanh
- Output activation depends on **task type**
""",
        "key_points": [
            "Enable non-linear transformations in networks",
            "ReLU is default for hidden layers",
            "Sigmoid for binary output, Softmax for multi-class",
            "Vanishing gradients occur with sigmoid/tanh in deep networks",
            "Choose output activation based on task type"
        ]
    },
    
    "forward-propagation": {
        "content": """
## What is it?

**Forward propagation** is the process of passing input data through the network layer by layer to produce an output prediction. Data flows forward from input to output, with each layer transforming the data using weights, biases, and activation functions.

This is how neural networks make predictions.

## How it Works

```
Forward Propagation Steps:
1. Input: x (raw features)
2. For each layer l:
   ├── Linear: z = W × a_prev + b
   └── Activation: a = activation(z)
3. Output: Final layer's activation = prediction
```

**Layer-by-Layer:**
```
a⁰ = x (input)

Layer 1:
├── z¹ = W¹ × a⁰ + b¹
└── a¹ = ReLU(z¹)

Layer 2:
├── z² = W² × a¹ + b²
└── a² = ReLU(z²)

Output Layer:
├── z³ = W³ × a² + b³
└── a³ = Softmax(z³) = ŷ (prediction)
```

**Matrix Operations:**
```
Input batch: X (batch_size × features)
Weights: W (features × neurons)
Bias: b (neurons)

Z = X @ W + b  (matrix multiplication)
A = activation(Z)

Efficient for GPU computation!
```

## Example

**Forward Pass in Digit Classification:**

```
Network: 784 → 128 → 64 → 10

Input: Flatten 28×28 image → x (784 values)

Layer 1 (784 → 128):
├── z₁ = W₁(128×784) × x(784) + b₁(128)
├── z₁ shape: 128 values
└── a₁ = ReLU(z₁) → 128 activations

Layer 2 (128 → 64):
├── z₂ = W₂(64×128) × a₁(128) + b₂(64)
├── z₂ shape: 64 values
└── a₂ = ReLU(z₂) → 64 activations

Output (64 → 10):
├── z₃ = W₃(10×64) × a₂(64) + b₃(10)
├── z₃ shape: 10 values (logits)
└── ŷ = Softmax(z₃) → 10 probabilities

Example output:
[0.01, 0.02, 0.01, 0.02, 0.01, 0.01, 0.03, 0.85, 0.02, 0.02]
                                              ↑
                                         Prediction: 7
```

## When to Use

**Forward propagation is used:**
```
├── Making predictions (inference)
├── First step of training (before backprop)
├── Evaluating model on validation set
└── Deploying model in production
```

**Key Considerations:**
```
Computational Cost:
├── O(n × m) per layer (n inputs, m outputs)
├── Efficient with batches (parallelized)
└── GPU accelerated

Memory:
├── Store activations for backpropagation
├── Larger batches = more memory
└── Trade-off: speed vs memory
```

## Key Takeaways

- Data flows **forward** through layers
- Each layer: **linear transformation + activation**
- **Matrix operations** enable efficient computation
- Produces **prediction** as final output
- Must **store activations** for backpropagation
- Same process for **training and inference**
""",
        "key_points": [
            "Data flows forward through network layers",
            "Each layer applies linear transformation then activation",
            "Matrix operations enable efficient GPU computation",
            "Produces prediction as final output",
            "Activations must be stored for backpropagation"
        ]
    },
    
    "loss-functions": {
        "content": """
## What is it?

**Loss functions** (or cost functions) measure how wrong the model's predictions are compared to the actual values. The goal of training is to minimize the loss. Different tasks require different loss functions.

The loss tells the network what it needs to fix.

## How it Works

**Common Loss Functions:**

```
Binary Cross-Entropy (Log Loss):
L = -[y×log(ŷ) + (1-y)×log(1-ŷ)]
├── For binary classification
├── Penalizes confident wrong predictions heavily
└── Used with sigmoid output

Categorical Cross-Entropy:
L = -Σ(yᵢ × log(ŷᵢ))
├── For multi-class classification
├── y is one-hot encoded target
└── Used with softmax output

Mean Squared Error (MSE):
L = (1/n) × Σ(y - ŷ)²
├── For regression
├── Penalizes large errors more
└── Sensitive to outliers

Mean Absolute Error (MAE):
L = (1/n) × Σ|y - ŷ|
├── For regression
├── More robust to outliers
└── Less common in neural networks
```

## Example

**Classification Loss Example:**

```
True label: "cat" → one-hot: [1, 0, 0]
Predicted probabilities: [0.7, 0.2, 0.1]

Categorical Cross-Entropy:
L = -[1×log(0.7) + 0×log(0.2) + 0×log(0.1)]
L = -log(0.7)
L = 0.357

If prediction was [0.9, 0.05, 0.05]:
L = -log(0.9) = 0.105 (lower = better!)

If prediction was [0.3, 0.4, 0.3]:
L = -log(0.3) = 1.204 (higher = worse!)
```

**Regression Loss Example:**
```
Actual prices: [300, 400, 350]
Predicted:     [320, 380, 360]
Errors:        [20, -20, 10]

MSE = (20² + 20² + 10²) / 3 = 300

MAE = (20 + 20 + 10) / 3 = 16.67

MSE penalizes the 20s more than MAE
```

## When to Use

**Loss Function Selection:**

| Task | Loss Function |
|------|---------------|
| Binary Classification | Binary Cross-Entropy |
| Multi-class Classification | Categorical Cross-Entropy |
| Regression | MSE or MAE |
| Regression with outliers | MAE or Huber |

**Why Cross-Entropy for Classification:**
```
Cross-entropy vs MSE for classification:
├── Cross-entropy: Gradients scale with error
├── MSE: Gradients can vanish with sigmoid
└── Cross-entropy trains faster, converges better
```

## Key Takeaways

- Measures **how wrong** predictions are
- Training minimizes the loss value
- **Cross-entropy** for classification
- **MSE/MAE** for regression
- Choice affects **gradient behavior** and training
- Different losses have different **error penalties**
""",
        "key_points": [
            "Measures how wrong predictions are compared to actual",
            "Training minimizes the loss value",
            "Cross-entropy for classification tasks",
            "MSE/MAE for regression tasks",
            "Choice affects gradient behavior and convergence"
        ]
    },
    
    "backpropagation": {
        "content": """
## What is it?

**Backpropagation** is the algorithm that calculates how each weight in the network contributed to the error. It works backwards from the output layer to the input, computing gradients (derivatives) that tell us how to adjust each weight to reduce the loss.

The magic that makes neural networks learn.

## How it Works

```
Backpropagation Steps:
1. Forward pass: Compute predictions and loss
2. Compute output layer gradients
3. For each hidden layer (backwards):
   └── Compute gradients using chain rule
4. Store gradients for weight updates
```

**Chain Rule:**
```
To find how W₁ affects loss:
∂L/∂W₁ = ∂L/∂a₃ × ∂a₃/∂z₃ × ∂z₃/∂a₂ × ∂a₂/∂z₂ × ∂z₂/∂a₁ × ∂a₁/∂z₁ × ∂z₁/∂W₁

Breaking it down:
├── ∂L/∂a₃: How output affects loss
├── ∂a₃/∂z₃: Activation derivative
├── ∂z₃/∂a₂: Connection weights
└── ...chain continues to W₁
```

**Why "Back" Propagation:**
```
Forward: Input → Layer 1 → Layer 2 → Output → Loss
         
Backward: Loss → Output → Layer 2 → Layer 1 → Input
         ∂L/∂W₃ ← ∂L/∂W₂ ← ∂L/∂W₁

Gradients flow backwards through network
```

## Example

**Simple Backprop Example:**

```
Network: x → [w₁] → a₁ → [w₂] → ŷ
Loss: L = (y - ŷ)²

Forward pass:
├── a₁ = ReLU(w₁ × x)
├── ŷ = w₂ × a₁
└── L = (y - ŷ)²

Backward pass:
├── ∂L/∂ŷ = 2(ŷ - y)
├── ∂L/∂w₂ = ∂L/∂ŷ × a₁
├── ∂L/∂a₁ = ∂L/∂ŷ × w₂
├── ∂L/∂w₁ = ∂L/∂a₁ × ReLU'(z₁) × x
└── Now we know how each weight affects loss!

Numerical example (x=2, y=10, w₁=1, w₂=2):
├── a₁ = ReLU(1×2) = 2
├── ŷ = 2×2 = 4
├── L = (10-4)² = 36
├── ∂L/∂ŷ = 2(4-10) = -12
├── ∂L/∂w₂ = -12 × 2 = -24 (w₂ should increase)
└── ∂L/∂w₁ = -12 × 2 × 1 × 2 = -48 (w₁ should increase)
```

## When to Use

**Backpropagation is:**
```
├── Core of neural network training
├── Automatic in modern frameworks (PyTorch, TensorFlow)
├── Enabled by storing activations in forward pass
└── Combined with gradient descent for updates
```

**Challenges:**
```
Vanishing Gradients:
├── Gradients shrink as they propagate back
├── Early layers learn very slowly
├── Solution: ReLU, skip connections

Exploding Gradients:
├── Gradients grow very large
├── Weights become NaN
├── Solution: Gradient clipping
```

## Key Takeaways

- Calculates **gradients** by propagating error backwards
- Uses **chain rule** from calculus
- Tells us **how to adjust each weight**
- Enabled by **storing activations** during forward pass
- **Automatic** in modern deep learning frameworks
- Can suffer from **vanishing/exploding gradients**
""",
        "key_points": [
            "Calculates gradients by propagating error backwards",
            "Uses chain rule to connect layers",
            "Tells us how to adjust each weight to reduce loss",
            "Requires storing activations from forward pass",
            "Can have vanishing or exploding gradient problems"
        ]
    },
    
    "gradient-descent": {
        "content": """
## What is it?

**Gradient descent** is the optimization algorithm that updates weights to minimize the loss. Using gradients from backpropagation, it takes small steps in the direction that reduces error. There are several variants: batch, stochastic (SGD), and mini-batch.

How neural networks actually learn.

## How it Works

```
Gradient Descent Update Rule:
w_new = w_old - learning_rate × gradient

Where:
├── gradient = ∂L/∂w (from backpropagation)
├── learning_rate = step size (hyperparameter)
└── Subtract because we want to go downhill
```

**Variants:**

```
Batch Gradient Descent:
├── Compute gradient on ENTIRE dataset
├── Update weights once per epoch
├── Stable but slow
└── May get stuck in local minima

Stochastic Gradient Descent (SGD):
├── Compute gradient on ONE sample
├── Update weights after each sample
├── Noisy but can escape local minima
└── Fast but unstable

Mini-batch SGD (Most Common):
├── Compute gradient on BATCH of samples (32, 64, 128)
├── Update weights after each batch
├── Balance of speed and stability
└── Standard in deep learning
```

**Advanced Optimizers:**
```
SGD with Momentum:
├── Accumulates past gradients
├── Faster convergence
└── Helps escape shallow local minima

Adam (Adaptive Moment Estimation):
├── Adaptive learning rates per parameter
├── Combines momentum + RMSprop
├── Most popular, works well out of box
└── Default choice for most problems
```

## Example

**Gradient Descent Visualization:**

```
Weight space with loss landscape:

     Loss
      ↑
   ╭──────╮
  ╱        ╲
 ╱    ╭──╮  ╲
╱    ╱    ╲  ╲
    START   ↓
             ↓
           GOAL (minimum)

Steps:
├── Start: w = 5, Loss = 10
├── Gradient = 4 (pointing uphill)
├── Update: w = 5 - 0.1×4 = 4.6
├── New Loss = 8.5 (decreased!)
├── Repeat...
└── Eventually: w = 2, Loss = 0.1 (converged)
```

**Batch Size Effects:**
```
Batch Size 1 (SGD):
├── Very noisy updates
├── Can escape local minima
└── Slow (can't parallelize well)

Batch Size 32:
├── Moderate noise
├── Good balance
└── Efficient GPU usage

Batch Size 1024:
├── Stable updates
├── May converge to sharp minima
└── Needs larger learning rate
```

## When to Use

**Optimizer Selection:**

| Optimizer | Use When |
|-----------|----------|
| SGD + Momentum | Computer vision, large models |
| Adam | Default starting point |
| AdamW | With weight decay regularization |
| RMSprop | RNNs, non-stationary problems |

**Batch Size Guidance:**
```
├── Start with 32 or 64
├── Increase if GPU memory allows
├── Larger batches → larger learning rate
└── Powers of 2 are GPU-efficient
```

## Key Takeaways

- Updates weights to **minimize loss**
- **Mini-batch SGD**: Most common variant
- **Adam**: Best default optimizer
- **Learning rate**: Critical hyperparameter
- **Batch size**: Trade-off between noise and speed
- Combines with **backpropagation** for training
""",
        "key_points": [
            "Updates weights in direction that reduces loss",
            "Mini-batch SGD is the standard approach",
            "Adam optimizer is the best default choice",
            "Learning rate is a critical hyperparameter",
            "Batch size affects noise, speed, and convergence"
        ]
    },
    
    "learning-rate": {
        "content": """
## What is it?

The **learning rate** controls how big the weight updates are during training. Too high and training is unstable; too low and training is too slow or gets stuck. It's one of the most important hyperparameters in deep learning.

Often the first thing to tune.

## How it Works

```
Update Rule:
w_new = w_old - learning_rate × gradient

Learning Rate Effects:
├── Too high (e.g., 1.0):
│   └── Overshoots minimum, diverges
├── Too low (e.g., 0.00001):
│   └── Very slow, may get stuck
├── Just right (e.g., 0.001):
│   └── Converges smoothly to minimum
```

**Learning Rate Schedules:**
```
Constant:
├── Same rate throughout training
└── Simple but not optimal

Step Decay:
├── Reduce LR by factor every N epochs
├── e.g., 0.001 → 0.0005 → 0.00025
└── Common in CV competitions

Exponential Decay:
├── LR = initial_LR × decay^epoch
└── Smooth decrease

Cosine Annealing:
├── LR oscillates following cosine curve
├── Can escape local minima
└── Popular in modern training

Warm-up:
├── Start low, ramp up, then decay
├── Helps with large batch training
└── Common with Adam/Transformers
```

## Example

**Learning Rate Finding:**

```
Learning Rate Range Test:
├── Start with tiny LR: 0.0000001
├── Increase LR each batch exponentially
├── Plot loss vs learning rate
└── Find where loss drops fastest

Result:
LR: 0.00001  →  Loss: 2.5 (barely changing)
LR: 0.0001   →  Loss: 2.0 (starting to learn)
LR: 0.001    →  Loss: 0.8 (good!)
LR: 0.01     →  Loss: 0.5 (fast but noisy)
LR: 0.1      →  Loss: 5.0 (diverging!)

Best starting LR: Around 0.001

Schedule example (Step Decay):
├── Epochs 1-30: LR = 0.001
├── Epochs 31-60: LR = 0.0005
├── Epochs 61-90: LR = 0.00025
└── Epochs 91-100: LR = 0.0001
```

## When to Use

**Starting Points by Optimizer:**

| Optimizer | Typical Starting LR |
|-----------|---------------------|
| SGD | 0.01 - 0.1 |
| Adam | 0.001 - 0.0001 |
| AdamW | 0.001 - 0.0001 |

**Best Practices:**
```
├── Use learning rate finder if unsure
├── Start with optimizer's default
├── Use a schedule (usually helps)
├── Reduce LR when validation loss plateaus
├── Larger batch → can use larger LR
└── Fine-tuning: Use smaller LR than training
```

## Key Takeaways

- Controls **step size** of weight updates
- **Too high**: Diverges. **Too low**: Slow/stuck
- **Schedules** reduce LR during training
- **Adam default**: 0.001 is good start
- **Warm-up** helps large batch training
- Often the **first hyperparameter** to tune
""",
        "key_points": [
            "Controls the step size of weight updates",
            "Too high causes divergence, too low is too slow",
            "Schedules reduce LR during training for fine-tuning",
            "Adam default of 0.001 is a good starting point",
            "Often the first hyperparameter to tune"
        ]
    },
    
    "overfitting-nn": {
        "content": """
## What is it?

**Overfitting in neural networks** occurs when the model learns the training data too well, including noise, and fails to generalize to new data. Neural networks are especially prone to overfitting due to their high capacity. Several techniques exist to prevent it.

The eternal enemy of deep learning.

## How it Works

**Signs of Overfitting:**
```
├── Training loss decreases, validation loss increases
├── Large gap between train and validation accuracy
├── Model performs well on train, poorly on test
└── Complex model, limited data
```

**Prevention Techniques:**

```
1. Dropout:
├── Randomly "drop" neurons during training
├── Probability p (e.g., 0.5) of setting to 0
├── Forces redundancy, prevents co-adaptation
└── Disable during inference

2. L2 Regularization (Weight Decay):
├── Add penalty: Loss + λ×Σw²
├── Encourages smaller weights
└── Built into optimizers (AdamW)

3. Early Stopping:
├── Monitor validation loss
├── Stop when validation loss increases
├── Restore best weights
└── Simple and effective

4. Data Augmentation:
├── Create variations of training data
├── Images: Rotate, flip, crop, color jitter
├── Increases effective dataset size
└── Very effective for images
```

## Example

**Applying Dropout:**

```
Training (Dropout = 0.5):
Input: [1.0, 0.5, 0.8, 0.2, 0.9]
Mask:  [1,   0,   1,   0,   1]   (random)
Output:[2.0, 0,   1.6, 0,   1.8] (scaled by 2)

Different pass:
Input: [1.0, 0.5, 0.8, 0.2, 0.9]
Mask:  [0,   1,   0,   1,   1]   (different random)
Output:[0,   1.0, 0,   0.4, 1.8] (scaled by 2)

Inference (No Dropout):
Input: [1.0, 0.5, 0.8, 0.2, 0.9]
Output:[1.0, 0.5, 0.8, 0.2, 0.9]
```

**Early Stopping Example:**
```
Epoch  Train Loss  Val Loss
1      2.5         2.4
5      1.2         1.3
10     0.5         0.8
15     0.2         1.0  ← Val increasing
20     0.1         1.5

Stop at epoch 10! Restore those weights.
```

## When to Use

**Regularization Guide:**

| Technique | When to Use |
|-----------|-------------|
| Dropout | Default for MLPs, CNNs |
| L2/Weight Decay | Always (use AdamW) |
| Early Stopping | Always monitor val loss |
| Data Augmentation | Limited training data |
| Batch Norm | Deep networks (also regularizes) |

**Typical Dropout Rates:**
```
├── Input layer: 0.1-0.2 (light dropout)
├── Hidden layers: 0.3-0.5
├── Before output: 0.5 (more aggressive)
└── RNNs: 0.2-0.3 (be careful)
```

## Key Takeaways

- Neural networks **easily overfit** due to high capacity
- **Dropout**: Randomly drop neurons (50% common)
- **L2 regularization**: Penalize large weights
- **Early stopping**: Stop when validation worsens
- **Data augmentation**: Especially for images
- Use **multiple techniques** together
""",
        "key_points": [
            "Neural networks easily overfit due to high capacity",
            "Dropout randomly drops neurons during training",
            "L2/Weight decay penalizes large weights",
            "Early stopping prevents training too long",
            "Data augmentation increases effective dataset size"
        ]
    },
    
    "batch-normalization": {
        "content": """
## What is it?

**Batch Normalization** normalizes layer inputs by adjusting and scaling activations during training. It stabilizes training, allows higher learning rates, and acts as regularization. One of the most important innovations in deep learning.

Makes training deeper networks practical.

## How it Works

```
Batch Norm Steps:
1. Compute batch mean: μ = (1/m) × Σxᵢ
2. Compute batch variance: σ² = (1/m) × Σ(xᵢ - μ)²
3. Normalize: x̂ = (x - μ) / √(σ² + ε)
4. Scale and shift: y = γ × x̂ + β

Where:
├── m = batch size
├── ε = small constant for stability
├── γ, β = learnable parameters
└── Network learns optimal scale/shift
```

**Why It Works:**
```
Problems it solves:
├── Internal Covariate Shift: Layer inputs change during training
├── Vanishing Gradients: Keeps activations in good range
├── Sensitivity to Initialization: More robust to bad init
└── Learning Rate: Can use higher rates, faster training

Benefits:
├── Faster convergence (2-10x)
├── Higher learning rates
├── Slight regularization effect
└── Enables very deep networks
```

## Example

**Batch Norm in Action:**

```
Before Batch Norm:
Layer outputs: [100.5, -50.2, 0.3, 200.1, -10.5]
├── Wide range of values
├── Some activations saturate
└── Gradients vanish or explode

After Batch Norm:
├── μ = 48.04, σ = 88.9
├── Normalized: [0.59, -1.10, -0.54, 1.71, -0.66]
├── Scale (γ=1.5): [0.89, -1.65, -0.81, 2.57, -0.99]
├── Shift (β=0.5): [1.39, -1.15, -0.31, 3.07, -0.49]
└── Activations in reasonable range!
```

**Training vs Inference:**
```
Training:
├── Use batch statistics (μ, σ from current batch)
└── Update running averages

Inference:
├── Use running averages (fixed)
├── No batch dependency
└── Single sample works fine
```

## When to Use

**Where to Place Batch Norm:**
```
Common patterns:
├── Conv → BatchNorm → ReLU → ... (most common)
├── Dense → BatchNorm → ReLU → ...
├── Before activation (original paper)
└── After activation (some prefer)
```

**When to Use:**
```
├── Deep networks (10+ layers)
├── Convolutional neural networks
├── When training is unstable
├── Want to use higher learning rates
└── Most modern architectures include it
```

**When NOT to Use:**
```
├── Very small batch sizes (statistics unreliable)
├── RNNs/LSTMs (use Layer Norm instead)
├── GANs (often problematic)
└── Online learning (single sample)
```

## Key Takeaways

- **Normalizes** activations within each batch
- Enables **higher learning rates** and **faster training**
- Provides slight **regularization**
- Use **running averages** during inference
- Essential for training **deep networks**
- For RNNs, use **Layer Normalization** instead
""",
        "key_points": [
            "Normalizes activations within each mini-batch",
            "Enables higher learning rates and faster convergence",
            "Provides slight regularization effect",
            "Uses running averages during inference",
            "Essential for training deep networks"
        ]
    },
    
    "hyperparameter-tuning": {
        "content": """
## What is it?

**Hyperparameter tuning** in neural networks involves finding the best architecture and training settings. Unlike regular parameters (weights) that are learned, hyperparameters are set before training: number of layers, neurons, learning rate, batch size, etc.

Can dramatically impact model performance.

## How it Works

**Key Hyperparameters:**
```
Architecture:
├── Number of layers (depth)
├── Neurons per layer (width)
├── Activation functions
└── Regularization (dropout rate)

Training:
├── Learning rate
├── Batch size
├── Number of epochs
├── Optimizer choice
└── Weight decay

Common Search Methods:
├── Grid Search: Try all combinations
├── Random Search: Random combinations (often better!)
├── Bayesian Optimization: Smart search based on results
└── Population-based: Evolutionary approach
```

**Why Random > Grid:**
```
Grid Search with 3 values each:
├── Learning rate: [0.1, 0.01, 0.001]
├── Batch size: [32, 64, 128]
└── 9 combinations, evenly spaced

Random Search with 9 trials:
├── Learning rate: Random from 0.001 to 0.1
├── Batch size: Random from 16 to 256
└── 9 combinations, better coverage

Random explores more unique values per parameter!
```

## Example

**Tuning a Neural Network:**

```
Baseline Architecture:
├── Layers: [128, 64]
├── Dropout: 0.5
├── Learning rate: 0.001
├── Batch size: 32
└── Validation accuracy: 82%

Hyperparameter Search Space:
├── Layers: [[64], [128, 64], [256, 128, 64]]
├── Dropout: [0.3, 0.5, 0.7]
├── Learning rate: [0.0001, 0.001, 0.01]
└── Batch size: [16, 32, 64, 128]

Top Results:
Config                           Val Acc
[256, 128, 64], drop=0.5, lr=0.001, bs=64    87%
[128, 64], drop=0.3, lr=0.001, bs=32         85%
[256, 128, 64], drop=0.5, lr=0.0001, bs=32   84%

Winner: Deeper network, moderate dropout, default LR
```

## When to Use

**Tuning Priority:**

| Priority | Hyperparameter | Impact |
|----------|----------------|--------|
| 1 | Learning rate | Very high |
| 2 | Architecture (depth/width) | High |
| 3 | Batch size | Medium |
| 4 | Regularization | Medium |
| 5 | Optimizer | Low (Adam usually fine) |

**Best Practices:**
```
├── Start with proven architectures
├── Tune learning rate first
├── Use validation set for all decisions
├── Log all experiments
├── Set compute budget before starting
└── Early stopping to save time
```

## Key Takeaways

- **Hyperparameters** are set before training
- **Learning rate** is most important to tune
- **Random search** often beats grid search
- Use **validation set** to evaluate
- **Log experiments** for reproducibility
- Start simple, add complexity as needed
""",
        "key_points": [
            "Hyperparameters are set before training begins",
            "Learning rate is the most important to tune",
            "Random search often beats grid search",
            "Use validation set for all tuning decisions",
            "Start simple and add complexity as needed"
        ]
    },
    
    "when-to-use-nn": {
        "content": """
## What is it?

**When to use neural networks** is a critical decision. Despite their power, neural networks aren't always the best choice. They excel with large datasets and complex patterns but struggle with small data, interpretability requirements, and structured tabular data.

Choose the right tool for the job.

## How it Works

**Neural Networks Excel When:**
```
├── Large dataset (10,000+ samples)
├── Complex patterns (images, text, audio)
├── Unstructured data
├── Feature engineering is difficult
├── Compute resources available
└── Interpretability not critical
```

**Traditional ML Better When:**
```
├── Small dataset (< 1,000 samples)
├── Tabular/structured data
├── Need interpretability
├── Limited compute resources
├── Fast training required
└── Features already meaningful
```

**Decision Framework:**
```
Data type?
├── Images → CNN
├── Text → Transformers/RNN
├── Audio → CNN/RNN
├── Sequences → RNN/Transformer
├── Tabular → Tree methods often better!
└── Mixed → Depends on primary modality

Data size?
├── < 1,000: Logistic Regression, Trees
├── 1,000 - 10,000: Trees, small NN
├── 10,000 - 100,000: NN viable
└── > 100,000: NN often best
```

## Example

**Comparing Approaches:**

```
Task 1: Classify 50K images (dogs vs cats)
├── Neural Network (CNN): 97% accuracy
├── Random Forest on pixels: 72% accuracy
└── Winner: CNN (unstructured, large data)

Task 2: Predict loan default (10K customers, 50 features)
├── XGBoost: 89% AUC
├── Neural Network: 87% AUC
└── Winner: XGBoost (structured tabular data)

Task 3: Fraud detection (1K transactions)
├── Random Forest: 82% F1
├── Neural Network: 75% F1 (overfits)
└── Winner: Random Forest (small dataset)

Task 4: Sentiment analysis (100K reviews)
├── BERT (Transformer): 94% accuracy
├── Naive Bayes: 82% accuracy
└── Winner: BERT (text, large data)
```

## When to Use

**Summary Table:**

| Scenario | Recommended |
|----------|-------------|
| Image classification | CNN |
| Text processing | Transformer |
| Tabular, small data | XGBoost/Random Forest |
| Tabular, large data | NN or XGBoost |
| Need explanations | Tree methods |
| Sequence data | RNN/Transformer |
| Fast prototyping | Simpler models first |

**Red Flags for Neural Networks:**
```
├── Less than 1,000 samples
├── Stakeholders need to understand decisions
├── Limited GPU access
├── Need to deploy on edge devices
├── Tabular data with meaningful features
└── Strict latency requirements
```

## Key Takeaways

- **Not always the best choice** despite power
- **Images, text, audio**: Neural networks shine
- **Tabular data**: Trees often win
- **Small datasets**: NN will overfit
- **Consider interpretability** requirements
- Always **compare with simpler baselines**
""",
        "key_points": [
            "Not always the best choice despite their power",
            "Excel with images, text, audio, and large datasets",
            "Tree methods often beat NNs on tabular data",
            "Small datasets cause overfitting in NNs",
            "Always compare with simpler baselines first"
        ]
    },
    
    "frameworks": {
        "content": """
## What is it?

**Deep learning frameworks** are software libraries that provide the building blocks for creating, training, and deploying neural networks. They handle the complex math (automatic differentiation), GPU acceleration, and provide pre-built layers and optimizers.

You don't need to implement backpropagation from scratch!

## How it Works

**Major Frameworks:**

```
PyTorch (Facebook/Meta):
├── Dynamic computation graph
├── Pythonic, intuitive syntax
├── Great for research and prototyping
├── Growing industry adoption
└── Preferred in academia

TensorFlow (Google):
├── Static and dynamic graphs (TF 2.0)
├── Production-focused, deployment tools
├── TensorFlow Lite for mobile
├── TensorFlow.js for web
└── Keras as high-level API

Others:
├── JAX (Google): Functional, great for research
├── MXNet (Apache): Scalable, Amazon uses
├── ONNX: Model interchange format
└── Hugging Face: Pre-trained models
```

**Key Features:**
```
All frameworks provide:
├── Automatic differentiation (autograd)
├── GPU/TPU acceleration
├── Pre-built layers (Dense, Conv, LSTM)
├── Optimizers (Adam, SGD)
├── Data loading utilities
└── Model saving/loading
```

## Example

**Same Network in PyTorch vs TensorFlow:**

```
# PyTorch
model = torch.nn.Sequential(
    torch.nn.Linear(784, 128),
    torch.nn.ReLU(),
    torch.nn.Linear(128, 10)
)

# TensorFlow/Keras
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10)
])

Both create:
├── Input: 784 features
├── Hidden: 128 neurons, ReLU
└── Output: 10 classes
```

## When to Use

**Framework Selection:**

| Use Case | Recommended |
|----------|-------------|
| Research/Prototyping | PyTorch |
| Production deployment | TensorFlow |
| Mobile apps | TensorFlow Lite |
| Web deployment | TensorFlow.js |
| NLP/Transformers | Hugging Face |
| Tabular AutoML | scikit-learn first |

## Key Takeaways

- **Frameworks handle complexity**: Autograd, GPU, etc.
- **PyTorch**: Research-friendly, Pythonic
- **TensorFlow**: Production-focused, deployment tools
- Both are **excellent choices** for most tasks
- Learn **one well** before trying others
- Community and **pre-trained models** matter
""",
        "key_points": [
            "Frameworks handle autograd, GPU acceleration, and more",
            "PyTorch is research-friendly and Pythonic",
            "TensorFlow is production-focused with deployment tools",
            "Both are excellent choices for most deep learning tasks",
            "Learn one well before trying others"
        ]
    }
}

