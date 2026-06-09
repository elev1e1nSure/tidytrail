# TidyTrail

Консольная утилита для анализа и сортировки папки загрузок.

## Установка

```bash
pip install -e .
```

## Быстрый старт

```bash
# Интерактивный режим (запуск без аргументов)
tidytrail

# Или используй команды напрямую
tidytrail preview
tidytrail sort
tidytrail dupes
tidytrail old -d 90
tidytrail clean
```

## Команды

| Команда | Описание |
|---------|----------|
| `preview` | Показать план сортировки |
| `sort` | Разложить файлы по папкам |
| `dupes` | Найти дубликаты (MD5) |
| `old` | Показать старые файлы |
| `clean` | Удалить мусор и пустые папки |

## Опции

- `-r, --recursive` — сканировать вложенные папки
- `-d, --days N` — количество дней для команды `old`
- `-y, --yes` — пропустить подтверждение
- `-n, --dry-run` — показать план без выполнения

## Категории

- `images/` — картинки, фото, анимации
- `docs/` — документы, PDF, Excel, Word
- `archives/` — zip, rar, 7z, tar
- `video/` — видео
- `audio/` — музыка
- `code/` — исходный код
- `executables/` — exe, msi, dmg

## Примеры

```bash
tidytrail                    # интерактивное меню
tidytrail preview            # показать план для Downloads
tidytrail sort -r            # сортировать включая подпапки
tidytrail dupes              # найти дубликаты
tidytrail old -d 30          # файлы старше 30 дней
tidytrail clean -r -y        # удалить мусор без подтверждения
```