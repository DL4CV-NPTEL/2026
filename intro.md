# Deep Learning for Computer Vision

Companion notebooks for the NPTEL course **Deep Learning for Computer Vision**.

:::{warning}
**This website is under active development and is prone to mistakes.**

Content is still being written, revised and corrected. Expect errors in the text,
the code and the figures. If something looks wrong, it may well be. Please treat the
lecture videos and slides as the authoritative source, and
[report anything you find](https://github.com/DL4CV-NPTEL/2026/issues).
:::

## About this book

The course runs for twelve weeks. Every lecture has a page in this book, and each
page carries three things:

- the **lecture video**, embedded and playable in place,
- a link to the **slide deck** for that lecture,
- an **Open in Colab** badge, so the notebook runs in the browser with nothing to install.

Where a notebook has hands-on material, it follows the same shape throughout:
*What you will learn* and *Contents* up front, a *Review* of the previous lecture,
a *Setup* cell, the numbered sections, then *Key takeaways* and *Exercises*.

Read a page here to follow the derivations and figures, or click **Open in Colab**
at the top of any page to run and edit the code yourself.

:::{note}
**The sliders on this site are not interactive. To use them, open the notebook in Colab.**

Several notebooks end with an *Explore and verify* section containing `ipywidgets`
sliders. A slider needs a running Python kernel behind it, and these pages are static
HTML, so on this website the widgets are frozen at their default values. Every such
section is paired with a static figure sweeping the same parameter, so you can see the
effect here regardless.

To move the sliders yourself, click **Open in Colab** at the top of the page and run
the cells.
:::

Weeks 1 to 9 have full hands-on notebooks. Weeks 10 to 12 currently provide the
lecture video and slides for each lecture, with the hands-on material still to
be written.

## Course outline

:::{dropdown} Week 1: Introduction and Overview
- Course Introduction and Overview
- History *(optional)*
- Image Formation *(optional)*
- Image Representation
- Linear Filtering, Correlation, Convolution
- Code Walkthroughs
:::

:::{dropdown} Week 2: Visual Features and Representations
- Edge Detection
- From Edges to Blobs and Corners
- Scale Space, Image Pyramids and Filter Banks
- SIFT and Variants
- Human Visual System *(optional)*
- Code Walkthroughs
:::

:::{dropdown} Week 3: Deep Learning Basics
- Neural Networks: A Review
- Feedforward Neural Networks and Backpropagation
- Gradient Descent and Variants
- Regularization in Neural Networks
- Improving Training of Neural Networks
- Code Walkthroughs
:::

:::{dropdown} Week 4: Convolutional Neural Networks for Image Classification
- Convolutional Neural Networks: An Introduction
- Backpropagation in CNNs
- CNN Architecture for Image Classification
- Code Walkthroughs
:::

:::{dropdown} Week 5: Beyond Basic CNNs: Architectures, Finetuning and Visualization
- Evolution of CNN Architectures: VGG, Inception, ResNets
- ResNet Variants, MobileNet, EfficientNet
- Finetuning CNNs
- Visualizing CNNs
- Code Walkthroughs
:::

:::{dropdown} Week 6: CNNs for Object Detection and Segmentation
- CNNs for Object Detection: Two-stage Models
- CNNs for Object Detection: Single-stage Models
- CNNs for Segmentation
- Code Walkthroughs
:::

:::{dropdown} Week 7: Recurrent Neural Networks and their use in Vision
- Recurrent Neural Networks: Introduction
- Backpropagation in RNNs
- LSTMs and GRUs
- Video Understanding using CNNs and RNNs
- Code Walkthroughs
:::

:::{dropdown} Week 8: Attention Models and Transformers
- Attention in Vision Models: An Introduction
- Soft and Hard Attention: Image Captioning
- Self-Attention and Transformers
- Code Walkthroughs
:::

:::{dropdown} Week 9: Vision Transformers and Applications
- From Transformers to Vision Transformers
- Transformers for Detection
- Transformers for Segmentation
- Code Walkthroughs
:::

:::{dropdown} Week 10: Deep Generative Models: GANs and VAEs
- Deep Generative Models: An Introduction
- Generative Adversarial Networks
- GAN Hacks and Improvements
- Variational Autoencoders and Disentanglement
- Code Walkthroughs
:::

:::{dropdown} Week 11: Deep Generative Models: Diffusion Models
- Introduction to Diffusion Models: DDPMs
- Classifier and Classifier-Free Diffusion Guidance
- Text-conditioned Diffusion Models
- Under the Hood: Sampling, Prediction Space, Noise Schedules, Architectures
- Code Walkthroughs
:::

:::{dropdown} Week 12: Vision-Language Models and Recent Developments
- Self-Supervised Learning: SimCLR
- Contrastive Learning
- Vision-Language Models
- CLIP, BLIP, BLIP-2
- Code Walkthroughs
- Course Conclusion
:::

:::{dropdown} Additional Material: Miscellaneous Advanced Topics *(optional)*
- Applications and Case Studies
- Few-shot and Zero-shot Learning
- Adversarial Robustness
- Pruning and Model Compression
- Neural Architecture Search
- Recent Developments
  - From VLMs to MM-LLMs: LLaVA, Video ChatGPT, ChatGPT-4V, Gemini 1.5
  - DALL-E 1, 2, 3 and Imagen
:::

## Instructor

```{image} images/vineeth.jpg
:alt: Vineeth N Balasubramanian
:width: 190px
:align: left
:class: bg-transparent
```

**Vineeth N Balasubramanian**

Principal Researcher, Microsoft Research India
Professor, Computer Science and Engineering, IIT Hyderabad

His broader research interests lie in deep learning, computer vision, multimodality,
reasoning and explainable AI. His ongoing work at Microsoft Research focuses on
multimodality in foundation models, large reasoning models, machine learning for
retrieval in LLMs, and applications to trustworthy and safe AI, human-in-the-loop AI
and healthcare. His research has produced over 100 peer-reviewed publications at
venues including ICML, NeurIPS, CVPR, ICCV, KDD and AAAI, and he received the
Teaching Excellence Award at IIT Hyderabad in 2017.

[Microsoft Research profile](https://www.microsoft.com/en-us/research/people/vineethn/) ·
[IIT Hyderabad profile](https://iith.ac.in/cse/vineethnb/)

```{eval-rst}
.. raw:: html

   <div style="clear: both;"></div>
```

## Teaching Assistants

**Anuj Lalla** — Microsoft Research

**Rishabh Lalla** — MBZUAI (Mohamed bin Zayed University of Artificial Intelligence)

<!-- Further course information (grading, schedule, references) to be added. -->
