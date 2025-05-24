from setuptools import setup, find_packages

setup(
    name="hospital-outcomes-analyzer",
    version="1.0.0",
    description="Hospital Outcomes Analyzer for DRG 329-334 Data",
    author="Hospital Analytics Team",
    py_modules=["hospital_analyzer"],
    install_requires=[
        "pandas>=1.5.0",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "hospital-analyzer=hospital_analyzer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.xlsx"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)