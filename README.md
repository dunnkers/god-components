# The evolution of God Components
How did big, bulky software components come into being? In this project, we explore the evolution of so-called _God Components_; pieces of software with a large number of classes or lines of code that got very large over time.


## Running project code
The analysis process consists out of two steps: (1) fetching the data using _Designite_ and (2) analyze the data using a Jupyter Notebook.

### (1) Running Designite
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

Put the command in `.bashrc` or `.zshrc` to persist the environment variable. **Now, to run the analysis, execute:**

```shell
python3 designite/find-gcs.py
```

This will clone tika repositories under `/designite/repositories` and run Designite for all commits. It will continue where it left off if you cancel the process. When it's finished, it will combine all reports in a single one at `/designite/output/all_reports.csv`. To only execute the combination process, run:

```shell
python3 designite/find-gcs.py --skip
```

#### Running on Peregrine
The process might take a while. For that reason, the `find-gcs.py` program is built to be executed in parallel. By default, it utilises all your available CPU's. To speed up even more, however, running on _Peregrine_ might be desired.

To run on Peregrine, ssh into Peregrine, clone this repo there and execute:

```shell
sbatch designite/peregrine.sh
```

The program will automatically utilise all Peregrine cores available on the given node ✨

### (2) Analyzing the data
The data is analyzed in a Jupyter Notebook, `statistics.ipynb`. It contains written text notes, images and code; it should be self-explanatory 🙂.

## Report
Latex report source is under `/report`, built PDF available in submission.

## About
Project during the Software Maintance and Evolution course `WMCS013-05.2020-2021.1B` at the University of Groningen.

By Jeroen Overschie and Konstantina Gkikopouli.
