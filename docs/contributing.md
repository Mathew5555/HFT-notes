---
title: Как дополнять HFT Notes
description: Инструкция для авторов и участников проекта
---

# Как дополнять HFT Notes

Все материалы проекта хранятся в Markdown. После push сайт автоматически пересобирается и публикуется на GitHub Pages.

## Структура проекта

```text
docs/
├── index.md
├── contributing.md
├── infrastructure/
│   ├── index.md
│   ├── 010-market-data.md
│   ├── 020-order-book.md
│   └── images/
│       └── order-book-depth.png
├── strategy-research/
│   ├── index.md
│   └── 010-backtesting.md
└── ml/
    ├── index.md
    └── 010-data-leakage.md
```

Каждая папка первого уровня внутри `docs/` — отдельный тематический раздел.

Файл `index.md` внутри раздела — его главная страница. Остальные Markdown-файлы — статьи или главы.

## Как добавить статью

Выберите нужный раздел:

```text
docs/infrastructure/
docs/strategy-research/
docs/ml/
```

Создайте Markdown-файл с именем:

```text
NNN-short-english-name.md
```

Например:

```text
010-market-data.md
020-order-book.md
030-exchange-connectivity.md
```

Числовой префикс задаёт порядок статей. Оставляйте интервалы `010`, `020`, `030`, чтобы позднее можно было вставить новую статью между существующими:

```text
010-market-data.md
015-market-data-normalization.md
020-order-book.md
```

### Шаблон статьи

```markdown
---
title: Книга заявок
description: Устройство и основные события limit order book
---

# Книга заявок

Короткое введение: что рассматривается в статье и зачем это нужно.

## Ценовые уровни

Текст раздела.

## Добавление заявки

Текст раздела.

## Отмена и исполнение

Текст раздела.

## Связанные материалы

- [Market Data](010-market-data.md)
- [Исследование стратегий](../strategy-research/)
```

Номер главы не нужно добавлять в `title` или заголовок `#`. Сайт автоматически пронумерует статьи согласно порядку файлов.

## Как изменить существующую статью

Откройте соответствующий `.md`-файл и измените текст.

Для разделов статьи используйте:

```markdown
# Название статьи

## Крупный раздел

### Подраздел
```

По заголовкам `##` и `###` сайт автоматически строит оглавление отдельной статьи.

## Как создать новый раздел

Создайте новую папку непосредственно внутри `docs/`:

```text
docs/risk-management/
```

Создайте главную страницу:

```text
docs/risk-management/index.md
```

Пример:

```markdown
---
title: Управление рисками
description: Контроль торговых и операционных рисков
---

# Управление рисками

В этом разделе рассматриваются механизмы управления рисками
в  торговых системах.

## Оглавление

<!-- AUTO_SECTION_INDEX -->

## Что будет рассмотрено

- 1) ..
- 2) ..


```

Добавьте статьи раздела:

```text
docs/risk-management/010-pre-trade-risk.md
docs/risk-management/020-position-limits.md
docs/risk-management/030-kill-switch.md
```

Новая папка автоматически появится в левой панели.

Если на главной странице используются карточки разделов, карточку нового раздела нужно добавить в `docs/index.md` вручную.

## Как добавлять изображения

Изображения хранятся непосредственно в репозитории. Для каждого раздела создавайте собственную папку `images/`:

```text
docs/infrastructure/images/

```

Вставьте его в статью:

```markdown
![Альтернативное описание](images/order-book-depth.png)
```

## Как добавлять внутренние ссылки

На статью в той же папке:

```markdown
[Книга заявок](020-order-book.md)
[Машинное обучение](../ml/)
[Утечки данных](../ml/020-data-leakage.md)
[Market-by-order](010-market-data.md#market-by-order)
```

## Локальная подготовка

Окружение создаётся один раз после клонирования репозитория.

### Linux и macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Для локального просмотра:

```bash
mkdocs serve --clean
```

Откройте:

```text
http://127.0.0.1:8000/
```

Перед отправкой изменений выполните:

```bash
mkdocs build --clean --strict
```

Сборка должна завершиться без ошибок.

## Как отправить изменения

Для командной работы используйте отдельную ветку и pull request.

### 1. Обновите `main`

```bash
git switch main
git pull --rebase origin main
```

### 2. Внесите изменения и проверьте сайт:

```bash
mkdocs serve --clean
```

### 3. Добавьте нужные файлы

Убедитесь, что не попало ничего лишнего!!!

### 4. Создайте коммит

```bash
git commit -m "Add order book notes"
```

### 5. Отправьте ветку

```bash
git push origin main
```

После push GitHub Actions автоматически пересоберёт и опубликует сайт.

Откройте вкладку **Actions** в репозитории и убедитесь, что workflow завершился успешно.
