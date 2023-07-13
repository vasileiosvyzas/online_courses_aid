from pathlib import Path

from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]
    
style_packages = [
    "black==23.7.0",
    "flake8==6.0.0",
    "isort==5.12.0"
]

# Define our package
setup(
    name="online_course_aid",
    version=0.1,
    description="",
    python_requires=">=3.7",
    packages=find_namespace_packages(),
    install_requires=[required_packages],
    extras_require={"dev": style_packages + ["pre-commit==3.3.2"]},
)