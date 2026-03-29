# Security Policy

## Supported Versions

Этот проект активно поддерживается в текущей ветке разработки.

## Reporting a Vulnerability

Если вы нашли уязвимость:
1. Не публикуйте детали в публичных issue.
2. Сообщите ответственному сопровождающему приватно.
3. Приложите шаги воспроизведения и потенциальное влияние.

## Secret Management Rules

- Никогда не коммитьте токены (`ghp_...`, `github_pat_...`, API keys).
- Храните секреты только в `.env`/secret manager.
- Используйте `.env.example` только с плейсхолдерами.
- Перед push запускайте:
  - `pre-commit run --all-files`
  - `pre-commit run gitleaks --all-files`

## Incident Response (если секрет утёк)

1. Немедленно revoke/rotate секрет.
2. Удалить секрет из git history (`git filter-repo` / BFG) при необходимости.
3. Проверить CI/CD и логи на следы использования.
4. Зафиксировать пост-мортем и превентивные меры.
