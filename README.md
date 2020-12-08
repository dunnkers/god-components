# The evolution of God Components
How did big, bulky software components come into being? In this project, we explore the evolution of so-called _God Components_; pieces of software with a large number of classes or lines of code that got very large over time.


## Running project code
... code under `/`

### Designite analysis
Code to investigate God Components for every version (commit) of the code is under `/designite`. First, set your DesigniteJava Enterprise key to a environment variable, like so:

```shell
export DESIGNITE_ENTERPRISE=<your_key>
```

We also rely on some dependencies, so create a virtual environment using:

```shell
python3 -m venv venv
source venv/bin/activate
pip3 install pandas
```

Put the command in `.bashrc` or `.zshrc` to persist the environment variable. Now, to run the analysis, execute:

```shell
python3 extraction.py
```

## Report
Latex report source is under `/report`, built PDF available in submission.

## About
Project during the Software Maintance and Evolution course `WMCS013-05.2020-2021.1B` at the University of Groningen.

By Jeroen Overschie and Konstantina Gkikopouli.
