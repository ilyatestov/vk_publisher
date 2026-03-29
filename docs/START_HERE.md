# START HERE — VK Publisher за 15 минут

Если вы запутались в проекте, начните отсюда.

## Шаг 1. Понять, что это за репозиторий

Сейчас тут смешаны два слоя:
1. **Python App** (pipeline, web UI, БД, обработка контента)
2. **PHP Library** (SDK для VK API)

Подробно: [`ARCHITECTURE_RECONSTRUCTION_RU.md`](./ARCHITECTURE_RECONSTRUCTION_RU.md)

## Шаг 2. Выбрать цель

### Мне нужно просто запустить текущую систему
1. Прочитать: [`UBUNTU_VPS_INSTALL.md`](./UBUNTU_VPS_INSTALL.md) или [`WINDOWS_INSTALL.md`](./WINDOWS_INSTALL.md)
2. Настроить VK: [`VK_API_SETUP.md`](./VK_API_SETUP.md)
3. Проверить UI: [`WEB_UI_GUIDE.md`](./WEB_UI_GUIDE.md)

### Мне нужно привести код в порядок
1. Прочитать: [`ARCHITECTURE_RECONSTRUCTION_RU.md`](./ARCHITECTURE_RECONSTRUCTION_RU.md)
2. Открыть аудит: [`PROJECT_AUDIT_RU.md`](./PROJECT_AUDIT_RU.md)
3. Открыть roadmap: [`PRODUCT_IMPROVEMENT_PLAN_RU.md`](./PRODUCT_IMPROVEMENT_PLAN_RU.md)

## Шаг 3. Минимальные правила, чтобы не усугублять хаос

- Все новые изменения делать только в `main`.
- Любая фича = код + тест + обновление документации.
- Не создавать новые legacy-слои и дубликаты клиентов.

## Шаг 4. Что делать в ближайшие 7 дней

1. Зафиксировать «боевые» entrypoint-и.
2. Развести Python и PHP как минимум по структуре каталогов.
3. Разделить CI для Python и PHP.
4. Свести документацию к одному индексу.

