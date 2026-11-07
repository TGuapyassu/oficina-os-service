# infra-k8s — OS Service

## manifests/app/

Deployment, Service, HPA, migration Job e ConfigMap do **oficina-os-service**.

## manifests/platform/

RabbitMQ e Redis compartilhados pela Saga (aplicar uma vez no namespace `oficina`).

```bash
kubectl apply -f manifests/platform/
kubectl apply -f manifests/app/namespace.yaml
# secrets + deploy via scripts/k8s-deploy.sh
```

Billing e Execution assumem `rabbitmq.oficina.svc` e `redis.oficina.svc`.
