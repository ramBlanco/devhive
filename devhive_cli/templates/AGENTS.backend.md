# Backend Architecture & AI Agent Guidelines

This `AGENTS.md` (or `GUIDELINES.md`) file serves as the strict instruction manual for OpenCode and DevHive agents. It defines the technical stack, architectural patterns, and coding conventions for this backend project.

## 🛠️ 1. Tech Stack
{{TECH_STACK}}

## 🧠 2. OpenCode Skills to Load
Agents **MUST** load the following specialized skills before executing tasks:
- `architecture-patterns`: For maintaining clean separation of concerns and Hexagonal Architecture.
- `backend-architect`: For scalable API design and domain modeling.
- `backend-security-coder`: For secure coding practices, input validation, and auth.
- `devhive-devops`: For {{IAC_TOOL}} infrastructure setup.

## 📂 3. Project Structure (Hexagonal Architecture)
For maximum scalability, testability, and maintainability, the project MUST strictly follow Hexagonal Architecture (Ports & Adapters).

```text
src/
├── domain/             # ENTERPRISE BUSINESS RULES (No external dependencies)
│   ├── entities/       # Pure domain models
│   └── exceptions/     # Domain-specific errors
├── application/        # APPLICATION BUSINESS RULES (Use Cases & Ports)
│   ├── use_cases/      # Orchestrates domain logic
│   └── ports/          # Interfaces for outbound communication (Repositories, External APIs)
├── infrastructure/     # ADAPTERS (Database, External Services, Third-party libs)
│   ├── database/       # Concrete implementation of repository ports
│   └── di/             # Dependency Injection container/setup
└── presentation/       # ENTRY POINTS (Controllers, REST APIs, GraphQL, Lambdas)
    └── controllers/    # Parses HTTP requests and calls use cases

infrastructure/         # IaC DEFINITIONS (Outside src/)
└── # {{IAC_TOOL}} configurations
```

## 📐 4. Architectural Rules & Clean Code (CRITICAL)

1. **The Dependency Rule**: Source code dependencies MUST only point inward, toward the `domain/`. 
   - `domain/` knows nothing about anything else.
   - `application/` depends only on `domain/`.
   - `infrastructure/` and `presentation/` depend on `application/` and `domain/`.
   - **Never import an infrastructure detail (like a DB model) into a use case.**

2. **Ports and Adapters**:
   - Outbound communication (like DB queries) MUST be defined as an interface (Port) in the `application/` layer.
   - The actual database logic MUST be implemented as an Adapter in the `infrastructure/` layer.

3. **Dependency Injection**:
   - Use Cases must receive their dependencies (Ports) via constructor injection.
   - The Presentation layer resolves these dependencies and passes them to the Use Cases.
{{DI_RULES}}
## 💻 5. Code Examples

{{CODE_EXAMPLES}}
