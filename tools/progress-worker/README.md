# Синхронизация прогресса (Cloudflare Worker + KV)

Прогресс методичек лежит в `localStorage` браузера (`lab-redesign-v1:<лаба>`) и пропадает при очистке данных сайта.
Worker хранит копию в KV; клиентский скрипт `works/js/sync.js` подтягивает её обратно.

Секретов в репозитории нет: пароль — секрет Worker `PASSWORD`, хранилище — привязка KV `PROGRESS`.

## Развёртывание (один раз, в панели Cloudflare)

1. **KV:** Storage & Databases → KV → Create → имя `anitech-progress`.
2. **Worker:** Workers & Pages → Create → Create Worker → имя `anitech-progress` → Deploy → Edit code → вставить содержимое `worker.js` → Deploy.
3. **Привязка:** Worker → Settings → Bindings → Add → KV namespace → переменная `PROGRESS` → `anitech-progress`.
4. **Пароль:** Worker → Settings → Variables and Secrets → Add → тип Secret → `PASSWORD` = длинная фраза (записать у себя).
5. Адрес Worker (`https://anitech-progress.<аккаунт>.workers.dev`) вписать в `WORKER` в `works/js/sync.js`.

Проверка: `https://<адрес>/api/progress` без пароля отвечает `{"error":"unauthorized"}`.

## Использование

Кнопка ☁ слева внизу на страницах методичек и «Все работы»: ввести пароль → «Подключить». Дальше прогресс сохраняется сам
(зелёная точка — синхронизировано). После очистки браузера: ввести пароль заново, прогресс вернётся.
Резервный путь без сервера — кнопки «Экспорт в файл» и «Импорт из файла».

## Правила слияния

- побеждает более новая запись по времени; но пустой прогресс никогда не затирает непустой;
- при открытии страницы, если с сервера пришло что-то новое, страница один раз перезагружается.

## Проверка и обслуживание

- `node tools/progress-worker/test.mjs` — проверки Worker без Cloudflare (пароль, лимит попыток, origin, формат данных).
- Чужие origin блокируются (список `ORIGINS` в `worker.js`; для тестов можно добавить переменную `EXTRA_ORIGINS`).
- Сменить пароль: изменить секрет `PASSWORD` в Cloudflare и ввести новый в панели ☁.
