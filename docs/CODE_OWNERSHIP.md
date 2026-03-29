# Code ownership (initial draft)

Черновой ownership до формализации CODEOWNERS.

## Python application

### Core runtime
- `src/main.py`
- `src/workers/*`
- `src/core/*`

Ответственность: запуск, оркестрация, runtime-поведение.

### Infrastructure adapters
- `src/infrastructure/*`
- `src/database/*`

Ответственность: интеграции (VK/Ollama/DB/Telegram).

### Processing and publishing
- `src/processor/*`
- `src/publisher/*`

Ответственность: контент-пайплайн, дедуп, форматирование.

## Legacy
- `src/legacy/*`
- shim-модули на старых путях

Ответственность: только backward compatibility до полного удаления legacy.

## PHP SDK
- `src/Client/*`
- `src/Services/*`
- `src/DTO/*`
- `src/Exceptions/*`
- `src/Config/*`

Ответственность: библиотечный API для интеграции с VK.

## Документация
- `README.md`
- `docs/*`

Ответственность: актуальность onboarding и архитектурных решений.
