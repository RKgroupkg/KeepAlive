from setuptools import setup, find_packages

setup(
    name="keep_alive_ping",  
    version="0.0.2",  
    packages=find_packages(),
    install_requires=[
      "Flask>=2.0.0",
      "requests>=2.25.0",
      "apscheduler>=3.7.0",
      "pytz",
      ],  # List dependencies here
    author="Rkgroup",
    author_email="rkgroup.coder@gmail.com",
    description="An advnace pinger and keepalive",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/RKgroupkg/KeepAlive",  
    classifiers=[
        "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
],
    python_requires='>=3.5',
)