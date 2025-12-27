# Инструкция по деплою на Vercel

## Подготовка

1. Убедитесь, что у вас установлен Vercel CLI:
```bash
npm i -g vercel
```

2. Войдите в Vercel:
```bash
vercel login
```

## Деплой

### Вариант 1: Через Vercel CLI

```bash
# Из корня проекта
vercel

# Для production деплоя
vercel --prod
```

### Вариант 2: Через GitHub (рекомендуется)

1. Загрузите проект в GitHub репозиторий
2. Зайдите на [vercel.com](https://vercel.com)
3. Нажмите "Add New Project"
4. Импортируйте ваш GitHub репозиторий
5. Vercel автоматически определит настройки из `vercel.json`

## Настройка Environment Variables

**ВАЖНО:** После деплоя обязательно настройте переменные окружения в Vercel Dashboard:

1. Зайдите в Settings → Environment Variables
2. Добавьте следующие переменные:

```
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j
```

3. После добавления переменных нужно сделать redeploy проекта

## Ограничения Vercel

⚠️ **Важные ограничения для Python приложений на Vercel:**

1. **Таймаут функций:**
   - Hobby план: 10 секунд
   - Pro план: 60 секунд (настроено в vercel.json)
   - Enterprise: до 300 секунд

2. **Размер зависимостей:**
   - Максимум 50MB для serverless функций
   - Если зависимости слишком большие, может потребоваться оптимизация

3. **Холодный старт:**
   - Первый запрос может быть медленным (cold start)
   - Последующие запросы быстрее

4. **Память:**
   - Ограничена размером функции
   - FAISS и Neo4j могут потреблять много памяти

## Рекомендации

Если ваше приложение требует:
- Длительных операций (>60 секунд)
- Больших зависимостей
- Постоянного подключения к БД (Neo4j)

Рассмотрите альтернативы:
- **Railway** - отлично подходит для Python/FastAPI
- **Render** - простой деплой Python приложений
- **Fly.io** - хорошая поддержка Python
- **Google Cloud Run** - масштабируемые контейнеры

## Проверка деплоя

После деплоя проверьте:

```bash
# Health check
curl https://your-project.vercel.app/health

# API docs
https://your-project.vercel.app/docs
```

## Локальная разработка с Vercel

Для тестирования локально:

```bash
vercel dev
```

Это запустит локальный сервер, имитирующий Vercel окружение.

## Troubleshooting

### Ошибка: "Module not found"
- Убедитесь, что все зависимости в `requirements.txt`
- Проверьте, что `api/index.py` правильно импортирует приложение

### Ошибка: "Timeout"
- Увеличьте `maxDuration` в `vercel.json` (требует Pro план)
- Оптимизируйте код для более быстрого выполнения

### Ошибка: "Function too large"
- Удалите ненужные зависимости
- Используйте более легкие альтернативы (например, faiss-cpu вместо faiss-gpu)

