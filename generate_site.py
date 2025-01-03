import os
import json
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import datetime
from dotenv import load_dotenv, dotenv_values

load_dotenv(".env")
CONFIG = dotenv_values(".env")

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / os.getenv("HTML_OUTPUT_DIR")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def generate_html_jinja(context: dict = {}, output_filename="index.html") -> Path:
    global CONFIG
    context.update(CONFIG)
    # Create the Jinja2 environment
    env = Environment(loader=FileSystemLoader("templates"))

    # Load the template
    template = env.get_template("index.html")

    # Data to render
    # Load data from context.json

    with open("context.json", "r") as file:
        context_file = json.load(file)

    context.update(context_file)
    context["_TIMESTAMP"] = datetime.datetime.now().isoformat()

    # Render the template with data
    rendered = template.render(**context)

    # Write the rendered content to index.html
    output_path = OUTPUT_DIR / output_filename

    print(f"Writing to {output_path.relative_to(BASE_DIR)}")

    with open(output_path, "w") as f:
        f.write(rendered)

    return output_path


# Output the result
if __name__ == """__main__""":
    generate_html_jinja()
