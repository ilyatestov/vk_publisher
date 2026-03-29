name: 📝 Pull Request
description: Предложите изменения в проект
title: "[PR]: "
labels: ["needs review"]
body:
  - type: markdown
    attributes:
      value: |
        Спасибо за ваш вклад! Пожалуйста, заполните эту форму для вашего Pull Request.
        
        ⚠️ **Перед созданием PR:**
        - Убедитесь, что код работает корректно
        - Проверьте стиль кода (PEP 8)
        - Обновите документацию (если нужно)
        - Прочитайте [CONTRIBUTING.md](../blob/main/.github/CONTRIBUTING.md)

  - type: textarea
    id: description
    attributes:
      label: Описание изменений
      description: Подробно опишите, что вы изменили и зачем
      placeholder: Например: Добавлена новая функция для..., Исправлена ошибка...
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Мотивация
      description: Почему эти изменения необходимы?
      placeholder: Опишите причину изменений
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: Тестирование
      description: Как вы тестировали свои изменения?
      placeholder: |
        - Запустил тесты...
        - Проверил вручную...
        - Добавил новые тесты...
    validations:
      required: true

  - type: dropdown
    id: type
    attributes:
      label: Тип изменений
      description: Выберите тип изменений
      options:
        - Исправление ошибки (bug fix)
        - Новая функция (new feature)
        - Улучшение документации (docs)
        - Рефакторинг (refactor)
        - Улучшение производительности (performance)
        - Другое
    validations:
      required: true

  - type: input
    id: related_issue
    attributes:
      label: Связанные issues
      description: Укажите номера связанных issues (если есть)
      placeholder: Например: #123, #456
    validations:
      required: false

  - type: textarea
    id: screenshots
    attributes:
      label: Скриншоты (если применимо)
      description: Добавьте скриншоты, демонстрирующие изменения
      placeholder: Перетащите скриншоты в это поле
    validations:
      required: false

  - type: textarea
    id: checklist
    attributes:
      label: Чеклист
      description: Отметьте выполненные пункты
      value: |
        - [ ] Код соответствует стилю проекта
        - [ ] Добавлены комментарии к сложным местам
        - [ ] Обновлена документация (если нужно)
        - [ ] Все тесты проходят успешно
        - [ ] Нет лишних файлов (.pyc, __pycache__, .env)
        - [ ] Сообщение коммита понятное
    validations:
      required: true

  - type: checkboxes
    id: terms
    attributes:
      label: Подтверждение
      description: Подтвердите выполнение следующих условий
      options:
        - label: Я прочитал CONTRIBUTING.md
          required: true
        - label: Мой код не нарушает лицензию проекта
          required: true
        - label: Я готов ответить на вопросы по этим изменениям
          required: true
