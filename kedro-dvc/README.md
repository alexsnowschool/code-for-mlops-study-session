## To Following the steps below, you will need to have the following installed:

- [Python 3.11+](https://www.python.org/downloads/)
- [DVC](https://dvc.org/doc/install)
- [Kedro](https://docs.kedro.org/en/stable/get_started/install.html)

## Steps to reproduce the project:

### Step 1: Kedro Project Setup

1. Clone the project: `git clone https://github.com/d3m-labs/d3m-kedro-project.git`
2. Change the directory: `cd kedro-dvc`
3. Create conda environment: `conda create --name kedro-dvc python=3.11 -y`
4. Activate the conda environment: `conda activate kedro-dvc`
5. Install the project dependencies: `pip install -r requirements.txt`
6. Create new branch: `git checkout -b kedro-dvc-demo`
7. Run the project: `kedro new --starter=spaceflights-pandas`
8. Change the directory: `cd spaceflights-pandas`

### Step 2: DVC Setup

1. Initialize DVC: `dvc init --subdir`
