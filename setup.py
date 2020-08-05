from setuptools import setup
from setuptools import find_packages


with open("VERSION", "r") as f:
    VERSION = f.read().strip("\n")


def read_requierments(filename):
    with open(filename, "r") as f:
        for line in f.readlines():
            if len(line) == 0 or line[0] == "#" or "://" in line:
                continue
            yield line.strip()


setup(
    name="sowba",
    version=VERSION,
    long_description=(
        open("README.md").read() + "\n" + open("CHANGELOG.md").read()),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/oukone/sowba",
    license="Private License",
    setup_requires=["pytest-runner"],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages("sowba", exclude=["integration_tests", "tests"]),
    package_dir={"": "sowba"},
    install_requires=[r for r in read_requierments("requirements.txt")],
    # extras_require={
    #     "test": [r for r in read_requierments("test-requirements.txt")]
    # },
    entry_points={"console_scripts": ["sowba-cli = commands:cli_runner"]},
)
