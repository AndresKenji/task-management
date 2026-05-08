# Infrastructure

Terraform code for the task-management AWS deployment.

## Layout

```
infrastructure/
  modules/
    cognito/
    database/
    lambda_api/
    frontend_hosting/
  envs/
    dev/
    prod/
```

## Conventions

Modules are reusable across environments. Per-env config lives in `envs/<env>/`.

The `database/` module is a contract. It does not provision a database. It accepts connection params (Supabase or any external Postgres) as inputs and writes them to AWS Secrets Manager. To swap providers, replace its implementation while preserving its `secret_arn` output.

Remote state will use S3 + DynamoDB lock; configured in milestone 5.

## Usage

```bash
cd envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Always confirm `terraform apply` interactively.
