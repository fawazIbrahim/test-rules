# Application Types

The `types` dimension in `applied-to` uses these values. The relation within the list is OR: a rule matches if the project is any one of the listed types.

| Key        | Description                                  |
|------------|----------------------------------------------|
| `api`      | REST / GraphQL / gRPC backend                |
| `batch`    | Scheduled or bulk jobs                       |
| `worker`   | Event/message consumer (Kafka, RabbitMQ...)  |
| `spa`      | Client-side web app                          |
| `ssr`      | Server-rendered web (Next, Thymeleaf...)     |
| `mobile`   | Mobile application                           |
| `library`  | Shared lib / SDK                             |
| `cli`      | Command-line interface                       |
| `function` | Serverless function                          |
| `iac`      | Terraform, Helm, K8s manifests               |
| `ALL`      | Matches any type (wildcard)                  |

## Validation

- The generator must reject any `types` entry that is not in this list.
- `ALL` cannot appear alongside other values (it is standalone).
