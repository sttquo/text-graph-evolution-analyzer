from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .examples import EXAMPLES
from .pipeline import analyze_dynamic_evolution
from .visualization import VISUALIZATION_AVAILABLE

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

RESULTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Text Graph Evolution Analyzer")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/results-assets", StaticFiles(directory=RESULTS_DIR), name="results-assets")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

REPORT_FILES = [
    "0_original_texts.txt",
    "1_alignment.txt",
    "2_syntax_analysis.txt",
    "2a_dependencies_original.txt",
    "2b_dependencies_edited.txt",
    "3_semantic_analysis.txt",
    "4_statistics.txt",
    "5_evolution_report.txt",
]


def get_example(example_id: str):
    for example in EXAMPLES:
        if example["id"] == example_id:
            return example
    return None


def list_reports(folder: Path):
    reports = []
    for filename in REPORT_FILES:
        file_path = folder / filename
        if file_path.exists():
            reports.append(
                {
                    "name": filename,
                    "content": file_path.read_text(encoding="utf-8", errors="replace"),
                }
            )
    return reports


def list_frame_images(folder: Path, run_id: str):
    frames_dir = folder / "frames"
    if not frames_dir.exists():
        return []
    return [f"/results-assets/{run_id}/frames/{image_path.name}" for image_path in sorted(frames_dir.glob("*.png"))]


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "examples": EXAMPLES,
            "visualization_available": VISUALIZATION_AVAILABLE,
        },
    )


@app.post("/analyze")
def analyze(
    example_id: str = Form(default=""),
    original_text: str = Form(default=""),
    edited_text: str = Form(default=""),
):
    selected_example = get_example(example_id) if example_id else None
    if selected_example is not None:
        title = selected_example["title"]
        original_text = selected_example["original"]
        edited_text = selected_example["edited"]
    else:
        title = "Пользовательский ввод"

    original_text = original_text.strip()
    edited_text = edited_text.strip()
    if not original_text or not edited_text:
        raise HTTPException(status_code=400, detail="Оба текста должны быть заполнены.")

    artifacts = analyze_dynamic_evolution(original_text, edited_text, title=title, verbose=False)
    return RedirectResponse(url=f"/results/{artifacts.run_id}", status_code=303)


@app.get("/results/{run_id}")
def result_page(request: Request, run_id: str):
    folder = RESULTS_DIR / run_id
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=404, detail="Результат не найден.")

    syntax_original_url = None
    syntax_edited_url = None
    if (folder / "syntax_original.png").exists():
        syntax_original_url = f"/results-assets/{run_id}/syntax_original.png"
    if (folder / "syntax_edited.png").exists():
        syntax_edited_url = f"/results-assets/{run_id}/syntax_edited.png"

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "run_id": run_id,
            "reports": list_reports(folder),
            "frame_images": list_frame_images(folder, run_id),
            "syntax_original_url": syntax_original_url,
            "syntax_edited_url": syntax_edited_url,
            "visualization_available": VISUALIZATION_AVAILABLE,
        },
    )
