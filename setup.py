from setuptools import find_packages, setup


with open("README.md", "r") as fh:
    long_description = fh.read()

# this grabs the requirements from requirements.txt
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name='manu_dede',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description="Téléchargement d'URL youtube",
    install_requires=REQUIREMENTS,
    python_requires='>=3.8',
    author='Grand Dub',
    author_email='',
    #url='',
    license='The Unlicense',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: The Unlicense",
        "Operating System :: OS Independent",
    ],
    # long_description_content_type="text/markdown",
    # long_description=long_description,
)
