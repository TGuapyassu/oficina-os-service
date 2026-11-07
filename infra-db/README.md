# infra-db — OS Service

Terraform para **RDS PostgreSQL** do microsserviço OS (`db_name = oficina_os`).

```bash
cd environments/homolog
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform apply
```

Em homolog compartilhado, pode existir um único RDS com databases distintos por serviço — cada repo mantém seu próprio state.
