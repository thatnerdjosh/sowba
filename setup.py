from setuptools import setup
from setuptools import find_packages


# with open("VERSION", "r") as f:
#     VERSION = f.read().strip("\n")

# with open("requirements.txt", "r") as f:
#     requirements = []
#     for line in f.readlines():
#         if len(line) == 0 or line[0] == "#" or "://" in line:
#             continue
#         requirements.append(line.strip())

# with open("test-requirements.txt", "r") as f:
#     test_requirements = []
#     for line in f.readlines():
#         if len(line) == 0 or line[0] == "#" or "://" in line:
#             continue
#         test_requirements.append(line)

setup(
    name="compass-api",
    # version=VERSION,
    # long_description=(open("README.md").read() + "\n" + open("CHANGELOG.md").read()),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://bitbucket.org/simotus/sws",
    license="Private License",
    # setup_requires=["pytest-runner"],
    zip_safe=True,
    include_package_data=True,
    packages=find_packages("app", exclude=["integration_tests", "tests"]),
    package_dir={"": "app"},
    # install_requires=requirements,
    # extras_require={"test": test_requirements},
    # entry_points={"console_scripts": ["sws = core.commands:command_runner"]},
)
