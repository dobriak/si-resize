# Image upscaler

Small utility to upscale local images using `super_image` models.

**Status**
- **State**: Working CLI utility for local image upscaling. Models are loaded via `super_image` and may require additional runtimes (e.g., `torch`).
- **Limitations**: Single-threaded, no progress UI, and no explicit GPU management in the script. Tests stub `super_image` to keep CI lightweight.

**Prerequisites**
- **Python**: 3.8+
- **Install deps**:

```bash
pip install -r requirements.txt
```

If a model backend requires `torch`, install a matching `torch` build for your platform (see https://pytorch.org).

**Quick behavior**
- Passing a file path upscales that single file and writes an output (default suffix `-upscaled`).
- Passing a directory processes all supported images inside: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`.
- Files with the upscale suffix already present or with an already-existing target output are skipped.

**CLI Options (full list)**
- **`input` (positional)**: Input image file path or directory.
- **`--output`, `-o`**: Output path or directory. For directory input this is the output directory; if omitted the script writes files next to inputs using the upscale suffix.
- **`--model`, `-m`**: Model short name or full identifier. Default: `edsr-base`.
	Supported short names: drln-bam, edsr, msrn, mdsr, msrn-bam, edsr-base, mdsr-bam, awsrn-bam, a2n, carn, carn-bam, pan, pan-bam.
	If a short name is provided (no `/`), the script prefixes `eugenesiow/` when forming the full pretrained identifier.
- **`--scale`, `-s`**: Upscaling factor (choices: `2`, `3`, `4`). Default: `2`.
- **`--upscale-suffix`, `-u`**: Suffix appended to upscaled filenames. Default: `-upscaled`.

**Directory processing details**
- The script lists files in the input directory and filters by supported extensions (case-insensitive).
- If `--output` points to a non-existent directory, the script will try to create it.
- Files whose stem or name already contain the upscale suffix are skipped to avoid re-processing.

**Examples**
- Upscale a single file (default scale 2):

```bash
python3 resize.py path/to/image.jpg
```

- Upscale a single file with explicit output and scale:

```bash
python3 resize.py path/to/image.jpg -o out.jpg --scale 3 --model edsr
```

- Upscale a directory and write outputs into `out_dir`:

```bash
python3 resize.py path/to/dir --output out_dir --upscale-suffix "-x2" --scale 2
```

**Developer notes**
- The script loads the chosen model once (fail-fast on load errors) and reuses it for all images.
- Image IO uses PIL; images are converted to RGB before being passed to `super_image` helpers.
- Call the `upscale()` function programmatically by loading a model with `load_model()` and then passing file paths.

If you'd like, I can add a short snippet showing programmatic usage or add extra examples for specific models.
