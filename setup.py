from setuptools import find_namespace_packages, setup  # type: ignore

requirements = [
    "aioshutdown==0.0.2",
]

requirements_dev = [
    "pre-commit==3.6.1",
]

setup(
    name="maelstrom",
    version="0.1.0",
    url="https://github.com/aliev/maelstrom",
    packages=find_namespace_packages(include=["maelstrom", "maelstrom.*"]),
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={"dev": requirements_dev},
    package_data={"maelstrom": ["py.typed"]},
    entry_points={
        "console_scripts": [
            "mnode=maelstrom.main:run",
        ]
    },
)
