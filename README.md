# Image upscaler

Small utility to upscale local images using `super_image`'s `EdsrModel`.

Prerequisites
- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

Note: `super_image` may require a runtime backend such as PyTorch. If you see errors about missing backends, install `torch` appropriate for your platform (see https://pytorch.org).

Usage (pip)

- Upscale a specific file:

```bash
python3 resize.py path/to/image.jpg
```

- Specify output or scale:

```bash
python3 resize.py club1 -o club1-upscaled.jpg --scale 2
```
