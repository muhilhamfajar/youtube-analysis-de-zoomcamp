# How to run this project on your local machine

## Pre-Requisite
1. Docker
2. Docker Compose
3. Terraform client installation
4. GCP account

## Setup GCP account
1. Create an account with your Google email ID 
2. Setup your first [project](https://console.cloud.google.com/) if you haven't already
    * eg. "Zoomcamp prooject", and note down the "Project ID" (we'll use this later when deploying infra with TF)
3. Setup [service account & authentication](https://cloud.google.com/docs/authentication/getting-started) for this project
    * Go to the *IAM* section of *IAM & Admin* https://console.cloud.google.com/iam-admin/iam
   * Click the *Edit principal* icon for your service account.
   * Add these roles in addition to *Viewer* : **Storage Admin** + **Storage Object Admin** + **BigQuery Admin**
   * Download service-account-keys (.json)
4. Place your service-account-keys (.json) to folder `terraform/keys` and `airflow/keys`. But don't forget to change the file to `gcp.json`.
   ```bash 
    cp /downloads/service-account.json final-project-zoomcamp/terraform/keys/gcp.json
    ```
   ```bash 
   cp /downloads/service-account.json final-project-zoomcamp/airflow/keys/gcp.json
   ```

## Setup
### 1. Run terraform
We are going to use Terraform to build our AWS infrastructure

From the project root folder, move to the `./terraform` directory
```bash
cd terraform
```
Run terraform commands one by one

- Initialization
    ```bash
    terraform init
    ```

- Planning
    ```bash
    terraform plan
    ```
- Applying
    ```bash
    terraform apply
    ```

### 2. Run pipeline
After the cloud infrastructure is up, you can do this step.

We are going to run all pipeline here.

From the project root folder, move to the `./airflow` directory
```bash
cd airflow
```

Do these task one by one:
- Initialize database for airflow
    ```bash
    docker compose up airflow-init
    ```
- Run airflow in docker
    ```bash
    docker compose up
    ```

- Open airflow web UI in `localhost:8080` using your local browser. For access just use `airflow` for username and `airflow` for password
- Find in DAG in airflow for `youtube_analysis_ingestion`
- then turn it on and trigger manual the DAG.
- Wait ~ the magic is running

### 3. Visualize data on looker studio
After the DAG is finished, you can go to [Looker studio](https://lookerstudio.google.com).

Try it by yourself for data visualization, for my recommendation to import the gold layer data only. If you need more data ready-to-use just create the gold layer in DBT folder (`airflow/dbt/youtube-warehouse/models/gold`) then run the DBT.