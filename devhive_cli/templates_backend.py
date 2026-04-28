import os
from pathlib import Path

def generate_backend_agents_md(template_path: Path, language: str, framework: str, iac: str, use_di: bool) -> str:
    stack_list = []
    if language == 'python':
        stack_list.append("- **Language**: Python 3.10+ (Strict Type Hinting)")
        if framework == 'fastapi':
            stack_list.append("- **Framework**: FastAPI")
        elif framework == 'django':
            stack_list.append("- **Framework**: Django")
        else:
            stack_list.append("- **Framework**: None (Pure Python / Lambdas)")
    else:
        stack_list.append("- **Language**: Node.js + TypeScript (Strict Mode)")
        if framework == 'express':
            stack_list.append("- **Framework**: Express")
        elif framework == 'nestjs':
            stack_list.append("- **Framework**: NestJS (Built-in DI)")
            use_di = False # NestJS has its own DI
        else:
            stack_list.append("- **Framework**: None (Pure Node.js / Lambdas)")
        
        if use_di:
            stack_list.append("- **Dependency Injection**: InversifyJS")

    if iac == 'cdk':
        stack_list.append("- **Infrastructure as Code**: AWS CDK")
    elif iac == 'terraform':
        stack_list.append("- **Infrastructure as Code**: Terraform")
    else:
        stack_list.append("- **Infrastructure as Code**: Serverless Framework")

    stack_section = "\n".join(stack_list)
    iac_tool_upper = iac.upper()

    di_rules = ""
    if language == 'node' and use_di:
        di_rules = """
4. **InversifyJS Usage**:
   - Decorate concrete adapters in `infrastructure/` with `@injectable()`.
   - Bind interfaces to symbols in an `inversify.config.ts` container file.
   - Use the container in the `presentation/` layer to resolve use cases.
"""

    code_examples = ""
    if language == 'python':
        if framework == 'fastapi':
            code_examples = """### Example: FastAPI + Hexagonal Architecture

**1. Port (Application Layer)**
*File: `src/application/ports/user_repository.py`*
```python
from typing import Protocol
from src.domain.entities.user import User

class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> User | None:
        ...
```

**2. Adapter (Infrastructure Layer)**
*File: `src/infrastructure/database/postgres_user_repository.py`*
```python
from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User

class PostgresUserRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_by_id(self, user_id: str) -> User | None:
        # DB logic here returning Domain Entity
        return User(id=user_id, name="Alice")
```

**3. Use Case (Application Layer)**
*File: `src/application/use_cases/get_user.py`*
```python
from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User
from src.domain.exceptions import UserNotFoundError

class GetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user
```

**4. Controller (Presentation Layer)**
*File: `src/presentation/controllers/user_controller.py`*
```python
from fastapi import APIRouter, Depends, HTTPException
from src.application.use_cases.get_user import GetUserUseCase
from src.infrastructure.database.postgres_user_repository import PostgresUserRepository
from src.domain.exceptions import UserNotFoundError

router = APIRouter()

# Poor man's DI for FastAPI
def get_user_use_case() -> GetUserUseCase:
    repo = PostgresUserRepository(db_session=None)
    return GetUserUseCase(user_repo=repo)

@router.get("/users/{user_id}")
def get_user(user_id: str, use_case: GetUserUseCase = Depends(get_user_use_case)):
    try:
        return use_case.execute(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```
"""
        elif framework == 'django':
            code_examples = """### Example: Django + Hexagonal Architecture

**Note on Django**: Do NOT put business logic in Django Views or Models. Use Django ONLY as the `infrastructure/` and `presentation/` layers.

**1. Port (Application Layer)**
*File: `src/application/ports/user_repository.py`*
```python
import abc
from src.domain.entities.user import User

class UserRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass
```

**2. Adapter (Infrastructure Layer)**
*File: `src/infrastructure/database/django_user_repository.py`*
```python
from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User
from myapp.models import DjangoUserModel # Django ORM Model

class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id: str) -> User | None:
        try:
            orm_user = DjangoUserModel.objects.get(id=user_id)
            return User(id=str(orm_user.id), name=orm_user.name) # Map ORM to Domain
        except DjangoUserModel.DoesNotExist:
            return None
```

**3. Controller (Presentation Layer)**
*File: `src/presentation/views/user_views.py`*
```python
from django.http import JsonResponse
from src.application.use_cases.get_user import GetUserUseCase
from src.infrastructure.database.django_user_repository import DjangoUserRepository
from src.domain.exceptions import UserNotFoundError

def get_user_view(request, user_id: str):
    repo = DjangoUserRepository()
    use_case = GetUserUseCase(user_repo=repo)
    
    try:
        user = use_case.execute(user_id)
        return JsonResponse({"id": user.id, "name": user.name})
    except UserNotFoundError as e:
        return JsonResponse({"error": str(e)}, status=404)
```
"""
        else:
            code_examples = """### Example: Pure Python + Hexagonal Architecture

**1. Port (Application Layer)**
*File: `src/application/ports/user_repository.py`*
```python
from typing import Protocol
from src.domain.entities.user import User

class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> User | None:
        ...
```

**2. Use Case (Application Layer)**
*File: `src/application/use_cases/get_user.py`*
```python
from src.application.ports.user_repository import UserRepository
from src.domain.entities.user import User

class GetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: str) -> User:
        return self.user_repo.get_by_id(user_id)
```

**3. Handler (Presentation Layer - Lambda)**
*File: `src/presentation/handlers/user_handler.py`*
```python
from src.application.use_cases.get_user import GetUserUseCase
from src.infrastructure.database.dynamo_user_repository import DynamoUserRepository

# Initialize dependencies at the module level for Lambda cold starts
repo = DynamoUserRepository()
use_case = GetUserUseCase(user_repo=repo)

def lambda_handler(event, context):
    user_id = event.get('pathParameters', {}).get('userId')
    user = use_case.execute(user_id)
    return {"statusCode": 200, "body": user.to_json()}
```
"""
    else: # Node.js
        if use_di:
            code_examples = """### Example: Node.js + TypeScript + InversifyJS

**1. Port (Application Layer)**
*File: `src/application/ports/IUserRepository.ts`*
```typescript
import { User } from "../../domain/entities/User";

export const TYPES = {
    IUserRepository: Symbol.for("IUserRepository"),
    GetUserUseCase: Symbol.for("GetUserUseCase"),
};

export interface IUserRepository {
    getById(userId: string): Promise<User | null>;
}
```

**2. Adapter (Infrastructure Layer)**
*File: `src/infrastructure/database/PostgresUserRepository.ts`*
```typescript
import { injectable } from "inversify";
import "reflect-metadata";
import { IUserRepository } from "../../application/ports/IUserRepository";
import { User } from "../../domain/entities/User";

@injectable()
export class PostgresUserRepository implements IUserRepository {
    async getById(userId: string): Promise<User | null> {
        // DB Logic returning Domain Entity
        return new User(userId, "Alice");
    }
}
```

**3. Use Case (Application Layer)**
*File: `src/application/useCases/GetUserUseCase.ts`*
```typescript
import { inject, injectable } from "inversify";
import "reflect-metadata";
import { IUserRepository, TYPES } from "../ports/IUserRepository";
import { User } from "../../domain/entities/User";

@injectable()
export class GetUserUseCase {
    constructor(
        @inject(TYPES.IUserRepository) private userRepository: IUserRepository
    ) {}

    async execute(userId: string): Promise<User> {
        const user = await this.userRepository.getById(userId);
        if (!user) throw new Error("User not found");
        return user;
    }
}
```

**4. DI Container Setup (Infrastructure Layer)**
*File: `src/infrastructure/di/container.ts`*
```typescript
import { Container } from "inversify";
import { TYPES, IUserRepository } from "../../application/ports/IUserRepository";
import { PostgresUserRepository } from "../database/PostgresUserRepository";
import { GetUserUseCase } from "../../application/useCases/GetUserUseCase";

const container = new Container();

container.bind<IUserRepository>(TYPES.IUserRepository).to(PostgresUserRepository);
container.bind<GetUserUseCase>(TYPES.GetUserUseCase).to(GetUserUseCase);

export { container };
```

**5. Controller (Presentation Layer)**
*File: `src/presentation/controllers/UserController.ts`*
```typescript
import { Request, Response } from "express";
import { container } from "../../infrastructure/di/container";
import { TYPES } from "../../application/ports/IUserRepository";
import { GetUserUseCase } from "../../application/useCases/GetUserUseCase";

export class UserController {
    async getUser(req: Request, res: Response) {
        const useCase = container.get<GetUserUseCase>(TYPES.GetUserUseCase);
        try {
            const user = await useCase.execute(req.params.id);
            res.json(user);
        } catch (error) {
            res.status(404).json({ error: error.message });
        }
    }
}
```
"""
        else:
            code_examples = """### Example: Node.js + TypeScript (Manual DI)

**1. Port (Application Layer)**
*File: `src/application/ports/IUserRepository.ts`*
```typescript
import { User } from "../../domain/entities/User";

export interface IUserRepository {
    getById(userId: string): Promise<User | null>;
}
```

**2. Adapter (Infrastructure Layer)**
*File: `src/infrastructure/database/PostgresUserRepository.ts`*
```typescript
import { IUserRepository } from "../../application/ports/IUserRepository";
import { User } from "../../domain/entities/User";

export class PostgresUserRepository implements IUserRepository {
    async getById(userId: string): Promise<User | null> {
        // DB Logic returning Domain Entity
        return new User(userId, "Alice");
    }
}
```

**3. Use Case (Application Layer)**
*File: `src/application/useCases/GetUserUseCase.ts`*
```typescript
import { IUserRepository } from "../ports/IUserRepository";
import { User } from "../../domain/entities/User";

export class GetUserUseCase {
    constructor(private userRepository: IUserRepository) {}

    async execute(userId: string): Promise<User> {
        const user = await this.userRepository.getById(userId);
        if (!user) throw new Error("User not found");
        return user;
    }
}
```

**4. Controller (Presentation Layer)**
*File: `src/presentation/controllers/UserController.ts`*
```typescript
import { Request, Response } from "express";
import { GetUserUseCase } from "../../application/useCases/GetUserUseCase";
import { PostgresUserRepository } from "../../infrastructure/database/PostgresUserRepository";

export class UserController {
    async getUser(req: Request, res: Response) {
        const repo = new PostgresUserRepository();
        const useCase = new GetUserUseCase(repo);
        try {
            const user = await useCase.execute(req.params.id);
            res.json(user);
        } catch (error) {
            res.status(404).json({ error: error.message });
        }
    }
}
```
"""

    with open(template_path, 'r', encoding='utf-8') as f:
        md = f.read()

    md = md.replace("{{TECH_STACK}}", stack_section)
    md = md.replace("{{IAC_TOOL}}", iac_tool_upper)
    md = md.replace("{{DI_RULES}}", di_rules)
    md = md.replace("{{CODE_EXAMPLES}}", code_examples)

    return md
