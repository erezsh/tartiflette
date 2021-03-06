import subprocess
import os
import sys
from setuptools import find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py


def _find_libgraphqlparser_artifact():
    if os.path.exists("./libgraphqlparser/libgraphqlparser.so"):
        return "./libgraphqlparser/libgraphqlparser.so"

    if os.path.exists("./libgraphqlparser/libgraphqlparser.dylib"):
        return "./libgraphqlparser/libgraphqlparser.dylib"

    return None


def _build_libgraphqlparser():
    os.chdir("./libgraphqlparser/.")
    subprocess.run(["cmake", "."], stdout=subprocess.PIPE)
    subprocess.run(["make"], stdout=subprocess.PIPE)
    os.chdir("..")

    artifact_path = _find_libgraphqlparser_artifact()

    if not artifact_path:
        print("Libgraphqlparser compilation has failed")
        sys.exit(-1)

    os.rename(
        artifact_path, "tartiflette/parser/cffi/%s" % os.path.basename(artifact_path)
    )


class BuildExtCmd(build_ext):
    def run(self):
        _build_libgraphqlparser()
        build_ext.run(self)


class BuildPyCmd(build_py):
    def run(self):
        _build_libgraphqlparser()
        build_py.run(self)


_TEST_REQUIRE = [
    "pytest",
    "pytest-benchmark",
    "pytest-cov",
    "pytest-asyncio",
    "pytz",
    "pylint==1.8.1",
    "xenon",
    "black==18.6b4",
]

_VERSION = "0.0.1"

_PACKAGES = find_packages(exclude=["tests*"])

# Builder = BuBuBuilder(
#     # STEP 1, cmake & make.
#     # STEP 2, mv lib to the corrects place
#     # STEP 3 kifflalife
# )


setup(
    name="tartiflette",
    version=_VERSION,
    description="GraphQL Request Executor for python",
    long_description=open("README.md").read(),
    url="https://github.com/dailymotion/tartiflette",
    author="Dailymotion Core API Team",
    author_email="team@tartiflette.io",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords="api graphql protocol api rest relay tartiflette dailymotion",
    packages=_PACKAGES,
    install_requires=[
        "cython",
        "uvloop==0.9.1",
        "cffi",
        "python-rapidjson",
        "lark-parser==0.6.4",
    ],
    tests_require=_TEST_REQUIRE,
    extras_require={"test": _TEST_REQUIRE},
    cmdclass={"build_ext": BuildExtCmd, "build_py": BuildPyCmd},
    include_package_data=True,
)
