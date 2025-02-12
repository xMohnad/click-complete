from setuptools import find_packages, setup

# Define constants for reuse
URL = "https://github.com/xMohnad/click-complete"


def parse_requirements(filename):
    with open(filename, "r", encoding="utf8") as f:
        requirements = f.read().strip().split("\n")
        requirements = [
            r.strip() for r in requirements if r.strip() and not r.startswith("#")
        ]
        return requirements


# EXTRAS_REQUIRE = {
#     "standard": ["click"]
# }

setup(
    name="click-complete",
    version="0.1.0",
    description="Generate shell completion scripts for Click apps.",
    url=URL,
    license="MIT",
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests*"]),  # Exclude test packages
    install_requires=parse_requirements("requirements.txt"),
    # extras_require=EXTRAS_REQUIRE,  # Define optional dependencies
    # entry_points={
    #     "console_scripts": [
    #         "click_complete = click_complete.core.main:cli",
    #     ],
    # },
    long_description=open(
        "README.md", encoding="utf-8"
    ).read(),  # Long description can be loaded from a README file
    long_description_content_type="text/markdown",
    author="xMohnad",
    # author_email=AUTHOR_EMAIL,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    keywords="click shell auto-complete automation",
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
    },
)
