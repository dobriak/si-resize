import importlib.util
import sys
import types
from pathlib import Path


def _load_module():
    # Ensure a stub for `super_image` so the module imports cleanly.
    fake = types.ModuleType("super_image")
    fake.ImageLoader = types.SimpleNamespace(
        load_image=lambda img: img, save_image=lambda preds, out: None
    )
    fake.models = types.SimpleNamespace()
    sys.modules["super_image"] = fake

    mod_path = Path(__file__).parent.parent / "resize.py"
    spec = importlib.util.spec_from_file_location("resize_module", str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_default_output_for_custom_suffix(tmp_path):
    mod = _load_module()
    inp = tmp_path / "img.png"
    inp.write_text("")
    out = mod.default_output_for(str(inp), up_suffix="_X")
    assert Path(out) == tmp_path / "img_X.png"


def test_skip_single_file_when_target_exists(tmp_path, monkeypatch, capsys):
    mod = _load_module()
    # create an input image and an existing upscaled target
    from PIL import Image

    img = tmp_path / "photo.jpg"
    Image.new("RGB", (10, 10)).save(img)
    target = tmp_path / f"photo{mod.DEFAULT_UPSCALE_SUFFIX}.jpg"
    target.write_bytes(b"")

    # Prevent actual model loading / upscaling
    monkeypatch.setattr(mod, "load_model", lambda *a, **k: object())

    def fail_upscale(*args, **kwargs):
        raise AssertionError("upscale should not be called when target exists")

    monkeypatch.setattr(mod, "upscale", fail_upscale)

    monkeypatch.setattr(sys, "argv", ["resize.py", str(img)])
    mod.main()
    captured = capsys.readouterr()
    assert "Skipping (target exists)" in captured.out


def test_directory_processing_calls_upscale(tmp_path, monkeypatch):
    mod = _load_module()
    from PIL import Image

    d = tmp_path / "imgs"
    d.mkdir()
    img = d / "a.jpg"
    Image.new("RGB", (8, 8)).save(img)

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    monkeypatch.setattr(mod, "load_model", lambda *a, **k: object())

    def fake_upscale(input_path, output_path, scale=2, model=None):
        Path(output_path).write_bytes(b"ok")

    monkeypatch.setattr(mod, "upscale", fake_upscale)
    monkeypatch.setattr(sys, "argv", ["resize.py", str(d), "--output", str(out_dir)])

    mod.main()

    expected = out_dir / f"a{mod.DEFAULT_UPSCALE_SUFFIX}.jpg"
    assert expected.exists()
