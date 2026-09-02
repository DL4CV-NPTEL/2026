# Deep Learning for Computer Vision (NPTEL, 2026)

Companion notebooks and slides for the NPTEL course **Deep Learning for Computer Vision**.

**Website:** https://dl4cv-nptel.github.io/2026/

**Instructor:** Prof. Vineeth N Balasubramanian, Department of Computer Science and
Engineering, IIT Hyderabad

**Teaching Assistants:** Anuj Lalla, Rishabh Lalla

## What is here

```
notebooks/Week 1 .. Week 12    one notebook per lecture (64 in total)
Slides/Week 1 .. Week 12       the lecture slide decks
weeks/                         a landing page per week, used by the website
```

Every notebook opens with an **Open in Colab** badge, the **lecture video** embedded
and playable, and a link to that lecture's **slides**. Weeks 1 to 9 have full hands-on
material; Weeks 10 to 12 currently carry the video and slides, with the notebooks still
to be written.

## Building the website

The site is built with [Jupyter Book](https://jupyterbook.org) and published by the
`Build and deploy Jupyter Book` GitHub Actions workflow on every push to `main`.

To build it locally:

```bash
pip install -r requirements-docs.txt
jupyter-book build .
```

Then open the site over HTTP rather than as a `file://` path, otherwise the embedded
YouTube players will not load:

```bash
cd _build/html && python3 -m http.server 8000   # then visit http://localhost:8000
```

`_config.yml` sets `execute_notebooks: "off"`, so the build uses the outputs stored in
each notebook and never starts a kernel. If you change a notebook's code, re-run that
notebook and commit the new outputs. Switching to `cache` would execute at build time,
and then Weeks 1 and 2 additionally need `scikit-image` and `opencv-python`.

## Editing a notebook

Three scripts in `tools/` keep the notebooks consistent and runnable:

```bash
# Execute a notebook top to bottom in a fresh kernel and store its outputs in place.
# Downloads land in a git-ignored data/ folder next to the notebook.
python3 tools/execute_notebooks.py "notebooks/Week 9/W09_L1_From_Transformers_to_Vision_Transformers.ipynb"

# Check the header cells, sections, widgets, device handling and execution time
# against the conventions used across the book.
python3 tools/check_notebook.py "notebooks/Week 9/W09_L1_From_Transformers_to_Vision_Transformers.ipynb"

# The notebooks run on Colab GPUs but are executed here on a CPU. This re-runs a copy on the
# Mac's mps device to catch tensors left on the wrong device (the classic Colab GPU crash).
python3 tools/execute_notebooks.py "notebooks/Week 9/W09_L1_From_Transformers_to_Vision_Transformers.ipynb" --simulate-gpu
```

`tools/sanitize_outputs.py` strips local filesystem paths from outputs; the execute script
already runs it, so you only need it after executing a notebook some other way.

Every notebook is written to finish in a few minutes on the free Colab tier (CPU or a T4 GPU)
and under about three minutes on a laptop CPU: datasets are synthetic or small torchvision
subsets, models are tiny, and widgets only redraw precomputed results.
