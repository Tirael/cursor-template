---
name: security-architecture
description: Архитектура безопасности: threat modeling, authn/authz, TLS/mTLS, аудит, секреты.
version: 1.0
lastUpdated: 2026-02-04
---

# Security Architecture (Skill)

## Когда применять

- Проектируем perimeter и модель доступа
- Добавляем интеграции с внешними провайдерами
- Определяем аудит и требования к логам

## Правила

- Threat modeling: STRIDE по основным потокам.
- Authn: OAuth2/OIDC.
- Authz: ABAC на базе `tenantId` + роль + контекст.
- Шифрование: TLS везде, mTLS для внутренних gRPC.
- Секреты: только Vault, запрет секретов в репозитории.
- Аудит: операции записи в `audit_log`.
