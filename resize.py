import argparse
import os
import sys
from pathlib import Path

from PIL import Image
from super_image import ImageLoader, models


# Supported image file extensions for directory/batch processing
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
MODELS = [
	"drln-bam",
	"edsr",
	"msrn",
	"mdsr",
	"msrn-bam",
	"edsr-base",
	"mdsr-bam",
	"awsrn-bam",
	"a2n",
	"carn",
	"carn-bam",
	"pan",
	"pan-bam",
]

# Default suffix appended to upscaled filenames. Can be overridden via CLI.
DEFAULT_UPSCALE_SUFFIX = "-upscaled"


def upscale(input_path: str, output_path: str, scale: int = 2, model=None) -> None:
	p_in = Path(input_path)
	if not p_in.is_file():
		raise FileNotFoundError(f"Input file not found: {input_path}")

	if model is None:
		raise ValueError(
			"Model instance is required; load the model once and pass it to `upscale()`."
		)

	# Ensure we pass a PIL Image (not a path string) into ImageLoader so
	# internal PIL operations like `.convert()` operate on Image objects.
	with Image.open(input_path) as img:
		img_rgb = img.convert("RGB")
		inputs = ImageLoader.load_image(img_rgb)

	preds = model(inputs)
	ImageLoader.save_image(preds, output_path)


def find_input_path(path_like: str) -> str:
	"""Normalize a path (expand ~ and resolve where possible)."""
	p = Path(path_like).expanduser()
	try:
		p = p.resolve()
	except Exception:
		# resolve may fail on non-existent paths; keep the normalized path
		p = p

	return str(p)


def default_output_for(input_path: str, up_suffix: str = DEFAULT_UPSCALE_SUFFIX) -> str:
	"""Return a default output filename using the provided suffix."""
	p = Path(input_path)
	parent = p.parent
	stem = p.stem
	suffix = p.suffix or ".jpg"
	return str(parent / f"{stem}{up_suffix}{suffix}")


def load_model(model_short: str, model_full: str, scale: int) -> models.SuperResolutionModel:
	match model_short:
		case "drln-bam":
			return models.DrlnModel.from_pretrained(model_full, scale=scale)
		case "edsr" | "edsr-base":
			return models.EdsrModel.from_pretrained(model_full, scale=scale)
		case "msrn" | "msrn-bam":
			return models.MsrnModel.from_pretrained(model_full, scale=scale)
		case "mdsr" | "mdsr-bam":
			return models.MdsrModel.from_pretrained(model_full, scale=scale)
		case "awsrn-bam":
			return models.AwsrnModel.from_pretrained(model_full, scale=scale)
		case "a2n":
			return models.A2nModel.from_pretrained(model_full, scale=scale)
		case "carn" | "carn-bam":
			return models.CarnModel.from_pretrained(model_full, scale=scale)
		case "pan" | "pan-bam":
			return models.PanModel.from_pretrained(model_full, scale=scale)
		case _:
			raise ValueError(f"Unsupported model: {model_short}")


def main() -> None:
	parser = argparse.ArgumentParser(
		description=(
			"Upscale an image or directory using a super-resolution model and "
			"save with a configurable suffix."
		)
	)
	parser.add_argument("input", help="Input image path or directory.")
	parser.add_argument(
		"--output",
		"-o",
		help=(
			"Output path or directory (for directory input, treated as "
			"output directory)."
		),
	)
	parser.add_argument(
		"--model",
		"-m",
		default="edsr-base",
		help=f"Model name to use (must be in {', '.join(MODELS)}).",
	)
	parser.add_argument(
		"--scale",
		"-s",
		type=int,
		choices=[2, 3, 4],
		default=2,
		help=(
			"Upscaling factor passed to the model (must be 2, 3, or 4; "
			"default: 2)"
		),
	)
	parser.add_argument(
		"--upscale-suffix",
		"-u",
		default=DEFAULT_UPSCALE_SUFFIX,
		help=f"Suffix to append to filenames for upscaled outputs (default: '{DEFAULT_UPSCALE_SUFFIX}')",
	)
	args = parser.parse_args()

	raw_in = args.input

	# If user supplied a trailing '*' or path separator, tolerate and strip it.
	if raw_in.endswith("*"):
		raw_in = raw_in[:-1].rstrip("/\\")

	p = Path(raw_in)
	try:
		p = p.expanduser().resolve()
	except Exception:
		p = p

	# Validate chosen model against supported list
	if args.model not in MODELS:
		sys.exit(f"Invalid model: {args.model}. Supported models: {', '.join(MODELS)}")

	# Build full pretrained identifier (supports passing full identifier too)
	model_full = args.model if "/" in args.model else f"eugenesiow/{args.model}"

	# Load the model once (fail fast on load errors)
	try:
		model = load_model(args.model, model_full, scale=args.scale)
	except Exception as exc:  # pragma: no cover - propagate error message
		sys.exit(f"Error loading model {model_full}: {exc}")

	# Configurable suffix for upscaled filenames
	up_suffix = args.upscale_suffix

	# Directory processing: process all supported images inside
	if p.is_dir():
		dir_path = p
		if not dir_path.exists():
			sys.exit(f"Directory not found: {dir_path}")

		files = [
			c for c in dir_path.iterdir() if c.is_file() and c.suffix.lower() in SUPPORTED_EXTS
		]

		if not files:
			sys.exit(f"No supported image files found in: {dir_path}")

		out_dir = Path(args.output) if args.output else dir_path
		out_dir = out_dir.expanduser()
		if args.output and not out_dir.exists():
			try:
				out_dir.mkdir(parents=True, exist_ok=True)
			except Exception as exc:
				sys.exit(f"Cannot create output directory: {exc}")

		for f in files:
			# Skip files that already contain the upscale suffix in name/stem
			if up_suffix in f.stem or up_suffix in f.name:
				print(f"Skipping (already upscaled): {f}")
				continue

			out_path = out_dir / f"{f.stem}{up_suffix}{f.suffix}"

			# If the target upscaled file already exists in the output directory, skip
			if out_path.exists():
				print(f"Skipping (target exists): {out_path}")
				continue

			try:
				upscale(str(f), str(out_path), scale=args.scale, model=model)
				print(f"Saved upscaled: {out_path}")
			except Exception as exc:
				print(f"Error processing {f}: {exc}")

		return

	# Single file path processing
	input_path = find_input_path(str(p))
	if not Path(input_path).is_file():
		sys.exit(f"Input file not found or is not a file: {args.input}")

	# If the single input already appears upscaled, skip processing
	_p = Path(input_path)
	if up_suffix in _p.stem or up_suffix in _p.name:
		print(f"Skipping (already upscaled): {_p}")
		return

	output_path = args.output or default_output_for(input_path, up_suffix)

	# Skip if the target upscaled file already exists
	_out_path = Path(output_path)
	if _out_path.exists():
		print(f"Skipping (target exists): {_out_path}")
		return

	try:
		upscale(input_path, output_path, scale=args.scale, model=model)
		print(f"Saved upscaled image to: {output_path}")
	except Exception as exc:
		sys.exit(f"Error during upscaling: {exc}")


if __name__ == "__main__":
	main()

