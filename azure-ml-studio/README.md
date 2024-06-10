## To Following the steps below, you will need to have the following installed:

- [Python 3.11+](https://www.python.org/downloads/)
- [Kedro](https://docs.kedro.org/en/stable/get_started/install.html)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- [Kedro-azureml plugin](https://kedro-azureml.readthedocs.io/)

## Steps to reproduce the project:

### Step 1: Kedro Project Setup

1. Clone the project: `git clone https://github.com/alexsnowschool/code-for-mlops-study-session.git`
2. Change the directory: `cd azure-ml-studio`
3. Create conda environment: `conda create --name kedro-dvc-ml-studio python=3.11 -y`
4. Activate the conda environment: `conda activate kedro-dvc-ml-studio`
5. Install the project dependencies: `pip install "kedro>=0.18.2,<0.19" "kedro-docker" "kedro-azureml"`
7. Run the project: `kedro new --starter=spaceflights`
8. Change the directory: `cd spaceflights`
9. Change the `required_cloud_info.sh` file with your Azure credentials and run the file: `source required_cloud_info.sh`

10. Run the project: `kedro azureml init  $SUBSCRIPTION_ID $RESOURCE_GROUP $WORKSPACE_NAME $EXPERIMENT_NAME $CLUSTER_NAME --docker-image=arralyze.azurecr.io/kedro_spaceflights:latest -a $STORAGE_ACCOUNT_NAME -c $STORAGE_CONTAINER_NAME`
```bash
# For docker image flow (1.), use the following init command:
 kedro azureml init <AZURE_SUBSCRIPTION_ID> <AZURE_RESOURCE_GROUP> <AML_WORKSPACE_NAME> <EXPERIMENT_NAME> <COMPUTE_NAME> \
 --docker-image <YOUR_ARC>.azurecr.io/<IMAGE_NAME>:latest -a <STORAGE_ACCOUNT_NAME> -c <STORAGE_CONTAINER_NAME>

# For code upload flow (2.), use the following init command:
kedro azureml init <AZURE_SUBSCRIPTION_ID> <AZURE_RESOURCE_GROUP> <AML_WORKSPACE_NAME> <EXPERIMENT_NAME> <COMPUTE_NAME> \
 --aml-env <YOUR_ARC>.azurecr.io/<IMAGE_NAME>:latest -a <STORAGE_ACCOUNT_NAME> -c <STORAGE_CONTAINER_NAME>
```
11. Double check the `azure-ml-studio/spaceflights/conf/base/azureml.yml` file to ensure that the `azureml.yml` is correctly configured.
12. Run to generate docker file for kedro project: `kedro docker init`
13. Add `kedro-azureml[mlflow]` to the `requirements.txt` file.
13. Build the docker image: `kedro docker build --docker-args "--build-arg=BASE_IMAGE=python:3.9" --image=arralyze.azurecr.io/kedro_spaceflights:latest`

### Step 2: Kedro-AzureML Plugin Setup

1. Login to Azure: `az login` 
2. Login to Container register Azure with CLI: `az acr login --name arralyze`
3. Push the docker image to Azure Container Registry: `docker push arralyze.azurecr.io/kedro_spaceflights:latest`
4. Run the kedro-azureml plugin: `kedro azureml run -s $SUBSCRIPTION_ID  --wait-for-completion`
5. Check the status from Pipeline from Azure ML Studio and Register the model after successfully run the pipeline.