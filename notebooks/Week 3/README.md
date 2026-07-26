# Week 3 Lecture Notebooks: Deep Learning for Computer Vision

Hands-on PyTorch companions to the Week 3 lectures (Prof. Vineeth N Balasubramanian, IIT-H).
One notebook per lecture. Each one runs top to bottom on Google Colab (CPU or GPU, no GPU
required), builds ideas bottom-up from scratch and then in idiomatic PyTorch, and includes
interactive sliders so you can see how each hyperparameter changes the result.

## How to run

- Open a notebook in Google Colab (or any Jupyter with PyTorch and ipywidgets).
- Run the first cell (setup) once, then go top to bottom.
- Everything is tiny and finishes in seconds; no datasets are downloaded.

## The ten notebooks

| # | Notebook | What you build |
|---|----------|----------------|
| 1 | L01_MP_Neuron_and_Perceptron | McCulloch-Pitts neuron, the perceptron, the learning algorithm, and the geometric reason it works |
| 2 | L02_XOR_MLP_and_Activations | Why XOR breaks a single perceptron, how an MLP fixes it, activation functions, universal approximation |
| 3 | L03_Feedforward_and_Gradient_Descent | Networks as function composition, gradient descent from scratch, why the negative gradient |
| 4 | L04_Backpropagation | Backprop derived by hand and verified against autograd, then used to train a net |
| 5 | L05_Momentum_and_Nesterov | Loss surfaces, saddle points, momentum, and Nesterov accelerated gradient |
| 6 | L06_SGD_and_Adaptive_Optimizers | Batch vs SGD vs mini-batch, learning-rate schedules, Adagrad, RMSProp, Adam |
| 7 | L07_Regularization_and_L2 | Overfitting, Lp norms, L2 weight decay, and the eigenvalue view of what it does |
| 8 | L08_EarlyStopping_Augmentation_Dropout | Early stopping, data augmentation, noise injection, ensembles, dropout from scratch |
| 9 | L09_Activation_Functions_In_Depth | Sigmoid, tanh, ReLU, saturation, vanishing gradients, the dying ReLU problem |
| 10 | L10_Weight_Init_and_BatchNorm | Init symmetry, variance propagation, Xavier and He init, batch normalization |

## What to look for in each notebook

- A short pointwise explanation of the idea and its math, matched to the slides.
- A from-scratch build ("peel the onion") followed by the PyTorch way, with the two checked against each other.
- Clear labeled plots (decision boundaries, loss curves, trajectories, histograms).
- Slider widgets that let you change the key hyperparameters and watch the effect live.
