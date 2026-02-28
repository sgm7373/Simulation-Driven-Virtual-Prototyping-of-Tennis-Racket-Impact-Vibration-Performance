from setuptools import setup, find_packages

setup(
    name="tennis-racket-sim",
    version="1.0.0",
    description="Simulation-Driven Virtual Prototyping of Tennis Racket Impact & Vibration Performance",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/YOUR_USERNAME/tennis-racket-sim",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "jupyter>=1.0.0",
            "notebook>=7.0.0",
            "ipykernel>=6.25.0",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
    entry_points={
        "console_scripts": [
            "tennis-racket-sim=main:main",
        ]
    },
)
