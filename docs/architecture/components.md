# Diagrama de Componentes

```mermaid
flowchart TB
  subgraph clients [Clientes]
    Web[Web_Vercel]
    Mobile[App_Cliente]
    Admin[Backoffice]
  end

  subgraph edge [Borda AWS]
    APIGW[API_Gateway_HTTP]
  end

  subgraph compute [Compute]
    Lambda[Lambda_Auth_CPF]
    EKS[EKS_Cluster]
    API[Deployment_oficina_api]
    HPA[HPA_2_a_10]
    ALB[ALB_Ingress]
  end

  subgraph data [Dados]
    RDS[(RDS_PostgreSQL_16)]
    SM[Secrets_Manager]
  end

  subgraph obs [Observabilidade]
    DD[Datadog_Agent_APM_Logs]
  end

  Web --> APIGW
  Mobile --> APIGW
  Admin --> APIGW
  APIGW -->|POST_/auth/cpf| Lambda
  APIGW -->|REST_/api| ALB
  ALB --> API
  API --> HPA
  EKS --> API
  Lambda --> RDS
  API --> RDS
  SM --> Lambda
  SM --> API
  API --> DD
  Lambda --> DD
  EKS --> DD
```

## Responsabilidades

| Componente | Repo | Função |
|------------|------|--------|
| API Gateway | `oficina-infra-k8s` | Roteamento, CORS, ponto único de entrada |
| Lambda Auth | `oficina-auth-lambda` | Validar CPF, consultar cliente, emitir JWT |
| EKS + HPA | `oficina-infra-k8s` + `oficina-api` | Escalabilidade da API |
| RDS | `oficina-infra-db` | Persistência gerenciada |
| Datadog | `oficina-infra-k8s` + app | Latência, CPU/mem, health, alertas OS |
