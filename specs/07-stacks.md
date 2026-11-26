# Languages and Frameworks

The `applied-to` field uses `languages` and `frameworks` as two separate dimensions. The relation between them is AND; the relation within each is OR.

## Languages

| Key          | Description       |
|--------------|-------------------|
| `java`       | Java              |
| `kotlin`     | Kotlin            |
| `typescript` | TypeScript        |
| `javascript` | JavaScript        |
| `python`     | Python            |
| `go`         | Go                |
| `csharp`     | C#                |
| `ALL`        | Matches any language (wildcard) |

## Frameworks / Runtimes

| Key        | Description          |
|------------|----------------------|
| `spring`   | Spring (Java/Kotlin) |
| `quarkus`  | Quarkus              |
| `node`     | Node.js              |
| `nestjs`   | NestJS               |
| `express`  | Express              |
| `angular`  | Angular              |
| `react`    | React                |
| `vue`      | Vue                  |
| `fastapi`  | FastAPI              |
| `django`   | Django               |
| `dotnet`   | .NET                 |
| `ALL`      | Matches any framework (wildcard) |

## Validation

- The generator must reject any `languages` entry not in the languages list.
- The generator must reject any `frameworks` entry not in the frameworks list.
- `ALL` cannot appear alongside other values in either dimension (it is standalone).
