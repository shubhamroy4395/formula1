from setuptools import setup, find_packages

setup(
    name="F1Paddock",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "setuptools>=68.0.0",
        "wheel",
        "numpy>=1.26.0",
        "pandas>=2.0.3",
        "matplotlib>=3.7.2",
        "streamlit>=1.28.0",
        "fastf1>=3.2.0",
        "python-dotenv>=1.0.0",
        "supabase>=1.2.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
        "tabulate>=0.9.0"
    ],
    python_requires=">=3.10, <3.13",
) 