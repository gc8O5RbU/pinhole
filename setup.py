import setuptools


install_requires = [
    "scrapy",
    "loguru",
    "pydantic",
    "pymupdf",
    "markdownify",
    "streamlit",
    "dateparser",
    "fastapi", "fastapi-cli"
]

extras_require = {
    "dev": [
        "mypy",
        "pycodestyle"
    ]
}


setuptools.setup(
    name="pinhole",
    version="2024.6",
    install_requires=install_requires,
    extras_require=extras_require,
    packages=setuptools.find_packages(".", exclude=["tests"])
)
