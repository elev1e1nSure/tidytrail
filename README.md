# TidyTrail

Консольная утилита для анализа и сортировки папки загрузок.

## Установка

```bash
pip install -e .
```

## Использование

```bash
tidytrail <command> [OPTIONS] [PATH]
```

### Команды

- **preview** — показать план сортировки
- **sort** — разложить файлы по папкам
- **dupes** — найти дубликаты (MD5)
- **old N** — показать файлы старше N дней
- **clean** — удалить мусор и пустые папки

### Примеры

```bash
tidytrail ./Downloads --preview
tidytrail ./Downloads --sort
tidytrail ./Downloads --dupes
tidytrail ./Downloads --old 90
tidytrail ./Downloads --clean
tidytrail ./Downloads --sort --dry-run
```

## Категории

- `images/` — картинки
- `docs/` — документы
- `archives/` — архивы
- `video/` — видео
- `code/` — код
- `audio/` — аудио
- `executables/` — исполняемые файлы