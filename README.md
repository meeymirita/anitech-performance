# ANITECH PERFORMANCE — обучающая платформа: Docker, Traefik, Caddy, Kubernetes, PHP, OOP, алгоритмы, RabbitMQ, Redis, Laravel, Laravel Performance, Inertia, JS, Vue, TypeScript, Nuxt, Angular, CSS, Tailwind, NestJS, GraphQL, PostgreSQL

![ANITECH PERFORMANCE](https://raw.githubusercontent.com/meeymirita/works-lab/main/images/banner.png)

Сборный репозиторий с лабораторными работами. Каждая работа подключена как git submodule в отдельной папке и живёт в собственном репозитории — со своей историей коммитов, независимо от остальных. Репозиторий будет пополняться новыми работами.

Витрина всех работ и их описания — на [`index.html`](index.html): живая версия — [anitech.meeymirita.ru](https://anitech.meeymirita.ru), локально открывается прямо в браузере.

## Как это выглядит

На примере NestJS Lab: карточка на главной → страница лабы с описанием → оглавление методички → сама методичка.

| Карточки лаб на главной | Страница лабы |
|---|---|
| ![Карточки лаб](https://meeymirita-files.storage.yandexcloud.net/site/screenshots/1-cards.jpg) | ![Страница лабы](https://meeymirita-files.storage.yandexcloud.net/site/screenshots/2-lab-page.jpg) |
| **Оглавление методички** | **Методичка** |
| ![Оглавление](https://meeymirita-files.storage.yandexcloud.net/site/screenshots/3-toc.jpg) | ![Методичка](https://meeymirita-files.storage.yandexcloud.net/site/screenshots/4-manual.jpg) |

## Работы

Порядок — от простого к сложному, с учётом того, что лабы переиспользуют друг друга: OOP-лаба даёт фундамент для RabbitMQ и Laravel; «Чистый PHP» встал рядом с OOP, потому что тоже про язык, но без фреймворка (её ссылки на Laravel-лабу — в будущем времени, так как та ещё не пройдена). Kubernetes использует код `api/` из Traefik-лабы (в самой Kubernetes-лабе он тоже приведён целиком) — без пройденной Traefik-лабы не имеет смысла. RabbitMQ стоит пройти до Redis (методичка постоянно сравнивает Streams с брокером) и до Laravel-лабы (она ссылается на обе). «Чистый JS» — общий фундамент для Vue и TypeScript; Vue — до TypeScript (сессия 5 использует Vue). NestJS и GraphQL — самостоятельные проекты, каждый со своим доменом: NestJS не собирает бэкенд Vue-лабы (это отдельное изучение технологии с нуля, домен Helpdesk похож на Vue Lab только по смыслу), а GraphQL не требует прохождения NestJS. Nuxt — после Vue и TypeScript: код из них не берёт, но объясняет только то, что Nuxt добавляет поверх Vue (SSR, Nitro, состояние на сервере, режимы рендеринга). PostgreSQL — тоже самостоятельная: разбирает то, что во всех остальных лабах пряталось за ORM, поэтому её можно проходить в любой момент, но полезнее всего — после одной-двух лаб с Laravel, когда Eloquent уже знаком. Inertia — самостоятельный проект на Laravel + Vue, кода из других лаб не берёт, но предполагает знакомство с обоими (Laravel Lab, Vue Lab); логичнее всего идёт после Laravel-лабы. Алгоритмы на PHP — самостоятельная лаба: нужен только синтаксис PHP, идёт рядом с чистым PHP и ООП. Laravel Performance — после Laravel Lab: на приложении Laravel 13 с миллионом заказов в PostgreSQL измеряет и ускоряет его (k6, профилировщики, OPcache, кеш в Redis, Octane); отдельных лаб-предшественников у неё нет, но нужен базовый Laravel. Docker и Traefik самодостаточны и не завязаны на остальные. Caddy — тоже самостоятельная: свой проект Edge (Node.js-бэкенды и PHP-FPM), решает ту же задачу, что Traefik (reverse proxy, TLS), но другим инструментом и подходом — проходить обе не обязательно, но рядом они показывают разницу решений.

> **Аудит, вычитка и проверка запуском (24.09–04.10.2026).** Все 21 методичка (пункты 1–21 таблицы) вычитаны построчно и исправлены, проверены стыки между лабами (DevOps, фронтенд, бэкенд). 03–04.10 каждая лаба прошла «сухой прогон»: собрана по блокам методички во временной папке (Docker, веб — Chromium), результаты сверены с «Ожидаемым результатом», найденные ошибки исправлены. Что и чем проверено, пошагово и со сносками «*» (аккаунт, домен, ключи, «Production Hell» — задания без подсказок) — на странице [«Что чем проверено»](works/verification.html); находки и решения — в [`fixes/`](https://github.com/meeymirita/lab-fixes) (отдельный репозиторий, сабмодуль), хронология — в [«Хронологии»](works/changelog.html). У каждой карточки на главной внизу — сноска «что требуется».
>
> **Caddy Lab (22) в этот аудит не входит** — добавлена позже (05.10.2026), вычитка проектом и сухой прогон ещё впереди. Автор методички проверил на реальном Caddy v2.11.7 сессии 1–6 и 9–11 (45 из 49 конфигов проходят `caddy validate`); Docker/Compose, PHP-FPM, сборка через xcaddy, systemd и кластер не запускались — в тексте помечены «сверьтесь».

| № | Папка | Лаба | Сложность | Репозиторий |
|---|---|---|---|---|
| 1 | [`docker`](docker) | Docker + Bash — крепкое владение с нуля | Базовая по входу, объёмная | [docker-lab](https://github.com/meeymirita/docker-lab) |
| 2 | [`php-coffee`](php-coffee) | OOP на PHP/Laravel — Coffee Shop API | Базовая по материалу | [oop-lab](https://github.com/meeymirita/oop-lab) |
| 3 | [`php`](php) | Чистый PHP — свой роутер, DI-контейнер, PDO, CSRF | Базовая по материалу | [php-lab](https://github.com/meeymirita/php-lab) |
| 4 | [`traefik`](traefik) | Traefik — reverse proxy, service discovery, TLS | Низкая–средняя | [traefik-lab](https://github.com/meeymirita/traefik-lab) |
| 5 | [`kubernetes`](kubernetes) | Kubernetes — от Compose к оркестрации | Средняя–высокая | [kubernetes-lab](https://github.com/meeymirita/kubernetes-lab) |
| 6 | [`rabbitmq`](rabbitmq) | RabbitMQ — Transactional Outbox, воркеры, DLQ | Высокая | [rabbitmq-lab](https://github.com/meeymirita/rabbitmq-lab) |
| 7 | [`redis`](redis) | Redis — кэш, локи, rate limit, Streams | Средняя | [redis-lab](https://github.com/meeymirita/redis-lab) |
| 8 | [`js`](js) | Чистый JS — Vanilla Helpdesk, фундамент без фреймворка | Средняя | [js-lab](https://github.com/meeymirita/js-lab) |
| 9 | [`vue`](vue) | Vue 3 — Helpdesk (Router, Pinia, WebSocket, тесты) | Высокая | [vue-lab](https://github.com/meeymirita/vue-lab) |
| 10 | [`typescript`](typescript) | TypeScript 6 — Warehouse (generics, Zod, API + Vue) | Высокая | [typescript-lab](https://github.com/meeymirita/typescript-lab) |
| 11 | [`nestjs`](nestjs) | NestJS — Helpdesk API с нуля (свой DI, JWT-ротация, WebSocket) | Высокая | [nestjs-lab](https://github.com/meeymirita/nestjs-lab) |
| 12 | [`graphql`](graphql) | GraphQL — CineGraph, самостоятельный проект (резолверы, DataLoader, Subscriptions) | Высокая | [graphql-lab](https://github.com/meeymirita/graphql-lab) |
| 13 | [`laravel`](laravel) | Laravel 13 изнутри — TaskFlow (таск-трекер с ролями) | Высокая | [laravel-lab](https://github.com/meeymirita/laravel-lab) |
| 14 | [`postgresql`](postgresql) | PostgreSQL — Coffee Shop изнутри (EXPLAIN, индексы, изоляция, блокировки, MVCC) | Средняя–высокая | [postgresql-lab](https://github.com/meeymirita/postgresql-lab) |
| 15 | [`nuxt`](nuxt) | Nuxt 4 — Help Center (SSR/SSG/SWR/SPA, Nitro, Drizzle, Nuxt Content) | Высокая | [nuxt-lab](https://github.com/meeymirita/nuxt-lab) |
| 16 | [`angular`](angular) | Angular 22 — RoomBook (сигналы, DI, httpResource, Signal Forms, RxJS) | Высокая | [angular-lab](https://github.com/meeymirita/angular-lab) |
| 17 | [`css`](css) | CSS с нуля — FrontFest (каскад, @layer, Flexbox, Grid, container queries, :has, темы) | Базовая | [css-lab](https://github.com/meeymirita/css-lab) |
| 18 | [`tailwind`](tailwind) | Tailwind CSS v4 — Pulse (`@theme`, варианты, container queries, dark mode) | Базовая | [tailwind-lab](https://github.com/meeymirita/tailwind-lab) |
| 19 | [`inertia`](inertia) | Inertia 3 + Laravel + Vue — Inkwell, блог-платформа | Средняя | [inertia-lab](https://github.com/meeymirita/inertia-lab) |
| 20 | [`laravel-performance`](laravel-performance) | Laravel Performance — CoffeePerf (k6, SPX, OPcache, кеш, Octane) | Базовая | [laravel-performance-lab](https://github.com/meeymirita/laravel-performance-lab) |
| 21 | [`algorithms-php`](algorithms-php) | Алгоритмы и структуры данных на PHP — CoffeeAlgo | Базовая | [algorithms-php-lab](https://github.com/meeymirita/algorithms-php-lab) |
| 22 | [`caddy`](caddy) | Caddy 2 — Edge, reverse proxy с автоматическим HTTPS | Средняя | [caddy-lab](https://github.com/meeymirita/caddy-lab) |

> Личный прогресс (моя пометка, не часть плана репозитория): ✅ пройдено — RabbitMQ. 🔵 сейчас прохожу — OOP (`php-coffee`).

---

## 1. Docker Lab (`docker/`)

> **Сложность: базовая по входу, но объёмная.** Не требует предыдущих лаб — рассчитана на полных новичков в контейнерах; Bash даётся параллельно, ровно в том объёме, который нужен для entrypoint-скриптов.

**О чём:** Docker и Bash разобраны подробно и с нуля — то, на что в Traefik-лабе был выделен всего один вводный раздел. Только сам Docker (образы, контейнеры, Dockerfile, тома, сети, Compose) и Bash как параллельный трек.

**Стек:** Node.js (Express) + PostgreSQL, всё в Docker / Docker Compose.

**Формат:** методичка `docker.html` — методичка готова, прохождение впереди.

**Что внутри (3 сессии):** разбор Docker с нуля (образ vs контейнер vs Dockerfile), Bash параллельным треком (shebang, переменные, циклы, `set -e -u -o pipefail`), ENTRYPOINT vs CMD, тома и сети, Docker Compose (`depends_on` + healthcheck) — пошаговая сборка маленького Node.js + PostgreSQL проекта, заканчивается явной точкой возврата к Traefik Lab.

---

## 2. OOP Lab (`php-coffee/`)

> **Сложность: базовая по материалу** (нужен только синтаксис PHP, фреймворк — с сессии 5), но именно здесь стоит не спешить, если ООП пока даётся тяжело: это фундамент, который потом всплывает во всех остальных лабах.

**О чём:** объектно-ориентированное программирование на PHP 8.4 с нуля — не абстрактно, а на маленьком API кофейни. Отдельный, ни от чего не зависящий проект (в отличие от Redis/RabbitMQ-лаб не растёт из общей системы заказов).

**Стек:** Laravel 13 (PHP 8.4) + PostgreSQL 18 + RabbitMQ + Mailpit — брокер появляется только в последней сессии.

**Формат:** методичка `php-coffee.html` (вычитана и исправлена 24.09) — ниже план по оглавлению. Первая сессия начинается с чистого PHP без фреймворка, чтобы увидеть ООП "без магии Laravel".

**Что внутри (5 сессий):**
- **Сессия 1** — касса на массивах (и почему это плохо) → первый объект `Money` → `abstract class Drink` + `enum` + полиморфизм → заказ с инвариантами
- **Сессия 2** — тесты для `Money`; иерархия напитков-наследников; фабрика `DrinkType` + `GET /api/menu`
- **Сессия 3** — интерфейс `Beverage`; паттерн **Decorator** для добавок (сироп, шот и т.д.); сущность `Order` + `OrderStatus`; Repository + `POST /api/orders`
- **Сессия 4** — `DiscountPolicy` + `Clock`; чекаут со стратегиями оплаты (`PaymentMethod`) + `/pay`; тесты на стратегиях; эксперимент "а если бы делали через наследование" (чтобы почувствовать разницу с композицией)
- **Сессия 5** — `EventPublisher` + событие `order.paid`; воркеры (бариста + уведомления) на RabbitMQ (один topic-exchange, две очереди — подробно эту схему разберёте позже в RabbitMQ-лабе); сквозной тест без БД и без брокера; финал "до/после"

Проходит через: 4 принципа ООП, `abstract class` vs `interface`, наследование vs композиция, паттерны (Factory, Decorator, Strategy, Repository), SOLID — всё на одном сквозном примере.

---

## 3. Чистый PHP Lab (`php/`)

> **Сложность: базовая по материалу** (нужен только синтаксис PHP и пройденная OOP-лаба — её принципы используются без повторного объяснения), но ближе к концу ощутимо прибавляет: сессии 1–4 — язык, сессии 5–8 — своя инфраструктура (роутер, DI-контейнер, PDO, CSRF).

**О чём:** чистый PHP 8.4 без единого фреймворка — то, что обычно прячет Laravel: `strict_types` и copy-on-write массивы, суперглобалы, исключения, замыкания и генераторы, магические методы, современный синтаксис (`match`, nullsafe), Composer и PSR-4 — и дальше своими руками: роутер, DI-контейнер, PDO-слой, сессии/CSRF. Домен — та же кофейня, что в OOP-лабе, но здесь пишется инфраструктура, которую там давал фреймворк.

**Стек:** PHP 8.4 CLI, встроенный dev-сервер, PostgreSQL через голый PDO, Composer только для автозагрузки (PSR-4) — без единого стороннего пакета до сессии 7.

**Формат:** методичка `php.html` — готова, прохождение впереди.

**Что внутри (8 сессий):**
- **Сессия 1** — стенд; `declare(strict_types=1)` + таблица `==` (чем PHP 7 отличается от PHP 8)
- **Сессия 2** — copy-on-write массивов на измерении момента копирования; `array_filter` vs `usort` (ключи, мутация); `mb_*` на кириллице + `sprintf` + regex
- **Сессия 3** — предсказать → проверить: `$_GET` и приведение типов; `php://input` — JSON-тело запроса; `finally` vs exception handler — порядок выполнения
- **Сессия 4** — `use ($var)` vs `use (&$var)` в замыканиях; генератор vs жадное чтение — измеряем память; свой фасад через `__callStatic`; `match` + nullsafe на неполных данных
- **Сессия 5** — PSR-4: автозагрузка до и после; свой роутер v1 (наивный) → v2 (regex-параметры)
- **Сессия 6** — боль без DI-контейнера (ручное связывание) → контейнер v1 (явные фабрики + singleton) → v2 (autowiring через Reflection)
- **Сессия 7** — SQL-инъекция: найти → исправить; транзакция с `rollBack` после частичного сбоя; CSRF своими руками (сессия + `hash_equals`); свой `.env`-парсер
- **Сессия 8** — финал: сборка `index.php`, middleware-цепочка, тесты + таблица «что даёт Laravel»

Разделы 1–12 методички — теория языка и рантайма, раздел 13 — восемь сессий заданий, разделы 14–17 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 4. Traefik Lab (`traefik/`)

> **Сложность: низкая–средняя** (инфраструктурная, не про код — backend/frontend уже даны готовыми). Нужно перед стартом: Docker Compose на уровне «поднять сервис и почитать логи»; для новичков в контейнерах есть отдельный вводный раздел 0.

**О чём:** reverse proxy и service discovery для стека из нескольких сервисов — без ручной правки конфигов при каждом деплое, через Docker-labels.

**Стек:** Traefik 3 + Docker Compose (с заметками про Podman) + Node.js API + статический frontend + PostgreSQL + Adminer.

**Формат:** методичка `traefik.html` — не пройдена, ниже план по оглавлению. Есть отдельный раздел 0 "Введение в Docker с нуля" для тех, кто раньше не работал с контейнерами.

**Что внутри (3 сессии):**
- **Сессия 1** — каталоги и `traefik/traefik.yml`; базовый `docker-compose.yml`; первый роутер через labels на тестовом сервисе `whoami`; dashboard Traefik и его защита; заметка про rootless Podman
- **Сессия 2** — backend API; frontend с path-routing (`StripPrefix`); PostgreSQL + Adminer за прокси; масштабирование API + healthcheck; цепочка middlewares
- **Сессия 3** — TLS через `mkcert` (локально) и Let's Encrypt (staging); canary-деплой (weighted round robin); "Production Hell" — финальный сценарий без подсказок

Модель для понимания: `EntryPoint → Router → Middleware → Service` — весь курс выстроен вокруг этой цепочки.

---

## 5. Kubernetes Lab (`kubernetes/`)

> **Сложность: средняя–высокая.** Нужны пройденные Docker Lab и Traefik Lab — сюда переносится ровно их стек (API + frontend + PostgreSQL + Adminer), поэтому новый домен не изучается, а сразу нужны настоящие понятия Kubernetes. Нужен код `api/` из Traefik-лабы (Dockerfile, server.js, package.json — в самой Kubernetes-лабе он тоже приведён целиком).

**О чём:** миграция уже знакомого стека из `docker-compose.yml` в Kubernetes, шаг за шагом — видно именно то, что меняется при переходе от одной машины к оркестрации, а не тонет в шуме нового кода. Кластер — [kind](https://kind.sigs.k8s.io/) (Kubernetes IN Docker): настоящий control plane и worker-узлы в контейнерах, тот же `kubectl` и те же объекты, что и в проде.

**Стек:** Kubernetes (kind) + kubectl + Traefik как Ingress-контроллер (IngressRoute CRD) — тот же стек приложения, что в Traefik Lab: Node.js API + статический frontend + PostgreSQL 18 + Adminer. Проверено на kind v0.24.0 / Kubernetes v1.31.0.

**Формат:** методичка [`kubernetes.html`](kubernetes/kubernetes.html) — открывается в браузере, прогресс по чекбоксам сохраняется локально.

**Что внутри (3 сессии):**
- **Сессия 1** — kind-кластер; первый Pod руками и его смертность; Deployment и самолечение через ReplicaSet; сборка образа API и `kind load`; Service и стабильный адрес поверх набора Pod'ов
- **Сессия 2** — полный стек: ConfigMap/Secret вместо `.env`; Volumes и PersistentVolumeClaim для PostgreSQL; readiness/liveness-пробы; requests/limits
- **Сессия 3** — Traefik снаружи кластера через IngressRoute CRD; HorizontalPodAutoscaler вместо ручных "x3 реплики"; "Production Hell" — финальный сценарий без подсказок

Раздел 0 — зачем эта лаба и что дальше; разделы 1–8 — теория (Control Plane/Node, Pod, Deployment, Service, ConfigMap/Secret, Volumes, Probes, Traefik как Ingress-контроллер), раздел 9 — три сессии заданий, разделы 10–13 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 6. RabbitMQ Lab (`rabbitmq/`)

> **Сложность: высокая.** Нужно перед стартом: уверенный Laravel/PHP (транзакции, Artisan-команды, очереди хотя бы на уровне концепции), базовые транзакции SQL, Docker Compose «запустить и посмотреть логи».

**О чём:** асинхронная обработка заказов интернет-магазина через очереди, с упором на паттерны надёжной доставки — то, что в реальных системах спасает от потери и дублирования сообщений.

**Стек:** Laravel 13 (PHP 8.4) + PostgreSQL 18 + RabbitMQ (Management UI) + Mailpit, всё в Docker Compose.

**Архитектура:** HTTP-запрос создаёт заказ и **сразу** пишет "записку" о событии в таблицу `outbox_messages` — в той же транзакции БД (паттерн **Transactional Outbox**, чтобы не потерять событие, если публикация в брокер упадёт). Отдельный процесс `outbox-relay` забирает записки и публикует их в exchange `orders.topic`. Дальше три независимых воркера (`order-worker`, `email-worker`, `analytics-worker`) разбирают свои копии сообщения из очередей: резервируют склад, шлют письмо, пишут в аналитику.

**Что пройдено (все 3 сессии):**
- Хопы 1–8: путь заказа от HTTP до БД, шаг за шагом, с точками наблюдения (`dd()`, логи, RabbitMQ UI)
- Что происходит, когда не хватает товара на складе
- **Идемпотентный consumer**: таблица `processed_messages` защищает от повторной обработки при redelivery
- Competing consumers + **prefetch** (`basic_qos`) — честное распределение нагрузки vs эффект "воркера-заложника" при большом prefetch
- Crash-тесты: `docker compose kill` (грубое убийство) и падение **после коммита, но до `ack`** — на практике поймали баг с `SIGKILL` на PID 1 в контейнере (ядро Linux его игнорирует), заменили на `exit()`
- **Retry с TTL → DLX** для писем: `email.retry.1/2/3` (10с/30с/300с) → `email.dlx` → назад в `email.queue` или в `email.dlq` после исчерпания попыток
- Читатель DLQ (`worker:failed-email`) — ручной разбор "мёртвых" сообщений
- Сравнение с нативными Laravel Queue Jobs (`$tries`/`$backoff`/`failed_jobs`) на том же RabbitMQ — чтобы почувствовать, где ручной AMQP-слой даёт то, чего нет из коробки (идемпотентность, publisher confirms, чужие consumer'ы не на Laravel)
- **Priority queues** (`x-max-priority`) с backlog — почему приоритет виден только при накопленной очереди
- **Fanout** (`lab:broadcast` / `worker:broadcast`) — широковещание всем подписчикам через `system.broadcast`, в отличие от topic-маршрутизации остального проекта

**Пример выполнения — в самом репозитории `rabbitmq-lab` (сабмодуль `rabbitmq/`):**
- рабочий код всех воркеров и команд — `laravel-app/app/Console/Commands/`
- пошаговый разбор пути заказа (хопы, точки наблюдения, что смотреть в БД/UI/логах) — [`docs/order-path-explained.md`](https://github.com/meeymirita/rabbitmq-lab/blob/main/docs/order-path-explained.md)
- ответы на все 18 вопросов для самопроверки, привязанные к коду проекта — [`docs/self-check-answers.md`](https://github.com/meeymirita/rabbitmq-lab/blob/main/docs/self-check-answers.md)
- подборка справочных материалов по темам лабы — [`docs/rabbit.md`](https://github.com/meeymirita/rabbitmq-lab/blob/main/docs/rabbit.md)

---

## 7. Redis Lab (`redis/`)

> **Сложность: средняя.** Нужно перед стартом: то же, что для RabbitMQ-лабы (Laravel, Docker), домен заказов переиспользуется. Рекомендуется после RabbitMQ Lab: методичка постоянно сравнивает Streams с брокером.

**О чём:** Redis как кэш, хранилище сессий, примитив синхронизации и брокер событий — одновременно, на кусочке той же системы заказов. Лаба специально показывает, где каждая из этих ролей "подводит" (что будет при рестарте без AOF, при отвале Pub/Sub-подписчика, при гонке за один и тот же лок).

**Стек:** Laravel 13 + PostgreSQL 18 + Redis 8.

**Формат:** методичка `redis.html` (открывается в браузере, прогресс по чекбоксам сохраняется локально) — ещё не пройдена, ниже план по оглавлению.

**Что внутри (3 сессии):**
- **Сессия 1** — docker-compose и `redis.conf`, Laravel + `.env`, миграции; **Cache-Aside** для карточки товара (`ProductRepository`); сессии в Redis (`SESSION_DRIVER=redis`); `StreamPublisher` — первый producer в Redis Streams; первый consumer (happy path)
- **Сессия 2** — **distributed lock** (`SET NX PX`) в `StockReservationService`, чтобы не продать один товар дважды; **rate limiter** (sliding window); competing consumers + нагрузочный тест; crash-тест на **PEL** (Pending Entries List) и идемпотентность
- **Сессия 3** — retry через `XAUTOCLAIM`; ручной DLQ-поток; приоритет очереди через `ZSET`; Pub/Sub-дашборд в реальном времени; "Production Hell" — комплексный сценарий без подсказок

Логика подачи материала зеркалит RabbitMQ-лабу (архитектура → сборка по шагам → "под капотом" → что почитать перед следующим шагом), но через призму структур данных Redis вместо AMQP.

---

## 8. Чистый JS Lab — Vanilla Helpdesk (`js/`)

> **Сложность: средняя.** Не требует предыдущих лаб — нужен только базовый синтаксис JS. Это общий фундамент для Vue Lab и TypeScript Lab, поэтому логично проходить её первой из трёх.

**О чём:** JavaScript с нуля, без единого фреймворка и без бандлера — то, что Vue и другие фреймворки обычно прячут: как на самом деле работают `var`/`let`/`const` и hoisting, `this` и замыкания, прототипы под капотом `class`, event loop, DOM и модули. Домен практики (тикеты) намеренно совпадает с Vue Lab — Helpdesk, чтобы в финале явно сравнить «vanilla vs Vue»; код при этом полностью свой, без единой связи с тем репозиторием.

**Стек:** JavaScript (ES2022+, без TypeScript и без сборки) + Node 24+ (LTS) для сессий-песочниц; в браузере — нативные ES-модули без бандлера; `json-server` как мок-API (только `db.json`, ноль кода); собственный ~15-строчный сервер на `node:http`; тесты — встроенный `node --test`; Docker (compose-файл создаётся в сессии 1).

**Формат:** методичка `js.html` — готова, прохождение впереди.

**Что внутри (8 сессий):**
- **Сессия 1** — переменные, область видимости, hoisting: воспроизведён и починен баг с `var` в цикле тремя способами
- **Сессия 2** — типы, приведение, объекты, массивы: рефакторинг императивного кода в функциональный на методах массивов
- **Сессия 3** — `this`, замыкания, паттерны: каррирование, мемоизация, приватность до и после `#private`
- **Сессия 4** — прототипы, `class`, `Symbol`, коллекции: цепочка прототипов руками → `class` → сравнение с `Map`/`Set`
- **Сессия 5** — event loop, Promises, fetch, debounce/throttle: своя очередь задач, реальный fetch к `json-server`, тесты на `node --test`
- **Сессия 6** — DOM без фреймворка: список тикетов рендерится и обновляется без единой строки фреймворка
- **Сессия 7** — модули (ESM), Storage, своя реактивность на `Proxy`
- **Сессия 8** — финал: мини-SPA (свой роутер на `history.pushState`, стор на `Proxy`, рендер шаблонными строками) с явной таблицей сравнения «что Vue даёт бесплатно»

Разделы 1–14 методички — теория языка и рантайма (от типичных багов без понимания фундамента до event loop, DOM и модулей), раздел 15 — стек, структура проекта и поток данных, раздел 16 — восемь сессий заданий, разделы 17–20 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 9. Vue Lab (`vue/`)

> **Сложность: высокая, если фронтенд — новая территория.** Нужно перед стартом: уверенный JavaScript (ES6+, async/await, деструктуризация); если сомневаетесь в фундаменте — сначала «Чистый JS» (`js/`). Опыт с Vue или другими фреймворками не требуется, готовый мини-бэкенд (Node) дан за вас.

**О чём:** Helpdesk (система тикетов) на Vue 3 с нуля — реактивность, компоненты, роутинг и общее состояние, каждое понятие на одном сквозном примере. Бэкенд (готовый мини-бэкенд на Node) дан в первой же сессии — писать его не нужно, только запустить.

**Стек:** Vue 3.5 + Vite 7 + Vue Router 4 + Pinia 2+ + Vitest, бэкенд — готовый мини-бэкенд (Node). Composition API + `<script setup>` (Options API — только в теории для сравнения). Всё в Docker.

**Формат:** методичка `vue.html` — не пройдена, ниже план по оглавлению.

**Что внутри (5 сессий, порядок строгий — Pinia раньше Router, потому что guard'ам роутера нужен auth-store):**
- **Сессия 1** — стенд (`docker-compose`, скаффолд готового бэкенда и `create-vue`); готовый мини-бэкенд на Node (auth, tickets, comments, history, WebSocket-gateway) — дан готовым; песочница реактивности: `ref`/`reactive`/`computed`/`watch`, директивы, `v-model`, `v-for`/`key`; `useAsync` и первый запрос к API
- **Сессия 2** — разбор списка тикетов на компоненты: `StatusBadge`, `TicketCard`, `TicketList` (props/emits, слоты); `BaseModal` (слоты, Teleport, lifecycle, template refs); тосты через `provide`/`inject`; composable `useNow`/`RelativeTime`
- **Сессия 3** — Pinia: `state`/`getters`/`actions`, `storeToRefs`, auth-стор с токеном, persist-плагин; оптимистичная смена статуса тикета с откатом при ошибке
- **Сессия 4** — Vue Router: маршруты, lazy loading, `RouterLink`, guards (`requiresAuth`, роли, redirect после логина), вложенные маршруты, query-синхронизация, 404; страница тикета с вкладками, форма создания, `onBeforeRouteLeave`
- **Сессия 5** — WebSocket (`useSocket`) с живыми обновлениями через store; канбан-доска (`TransitionGroup`, `defineAsyncComponent`, динамический компонент); тесты на Vitest (компонент, composable, store, router guard); production-сборка и деплой за прокси

Главная мысль лабы: Vue — это реактивность + компоненты + экосистема (Router — состояние адресной строки, Pinia — общее состояние), и каждое задание про то, где живёт состояние и кто его меняет.

---

## 10. TypeScript Lab (`typescript/`)

> **Сложность: высокая** — абстрактное мышление на уровне типов (generics, conditional/mapped types) непривычно после динамического PHP. Нужно перед стартом: тот же JavaScript, что для Vue-лабы; логично проходить после или параллельно с ней (сессия 5 использует Vue).

**О чём:** типизация домена складского учёта (Warehouse) с нуля — без фреймворков до последней сессии, чтобы увидеть TypeScript в чистом виде и потом узнавать его в Nest/Vue. Что типы реально ловят (перепутанные аргументы, `NaN` от строки вместо числа, `undefined` в рантайме), а что — нет.

**Стек:** TypeScript 6.0 (код проверен и на 5.9) + Node 24+ (LTS) + `tsx` + Vitest + Zod, в финале — Express и Vue 3 + TS. Отдельный репозиторий на npm workspaces: `packages/core`, `cli`, `api`, `web`. Всё в Docker.

**Формат:** методичка `typescript.html` — не пройдена, ниже план по оглавлению. Каждый шаг заканчивается зелёным `npm run typecheck` — это главный критерий готовности.

**Что внутри (5 сессий, порядок строгий):**
- **Сессия 1** — стенд (Docker, workspaces, `tsconfig.base`, `tsx`, Vitest); песочница: аннотации, вывод типов, примитивы/объекты, union и литералы, `type` vs `interface`, функции, `any`/`unknown`/`never`, `strict`, `as const`
- **Сессия 2** — домен склада: branded IDs, размеченное объединение `Movement`, exhaustive `switch`, `Result` вместо исключений, type predicates, `readonly` — `applyMovement` с тестами, невозможные состояния невыразимы на уровне типов
- **Сессия 3** — generics и абстракции: `Repository<T>`, `TypedEmitter<Events>`, mapped/conditional/template literal types, `satisfies` — сервис `Warehouse`, собранный из типизированных кубиков
- **Сессия 4** — CLI: `parseArgs`, команды как union из template literal types, валидация через Zod и `z.infer`, `unknown` в `catch`, `.d.ts` для JS, сборка esbuild — рабочий `wh`: `item:add`, `stock:in/out/transfer/list/low`, `import:csv`
- **Сессия 5** — сквозная типизация: `ApiContract`, generic-клиент с conditional types, Express + Zod на бэкенде, Vue 3 + TS (`defineProps`/`defineEmits` с generics, типизированный store), `vue-tsc` — один источник типов и в API, и в браузере

---

## 11. NestJS Lab (`nestjs/`)

> **Сложность: высокая.** Проект полностью самостоятельный — не требует прохождения других лаб. TypeScript-минимум, нужный для Nest, объясняется по ходу в сессии 1. Это полное изучение NestJS с нуля как отдельной технологии: домен Helpdesk похож на Vue Lab только по смыслу, зависимости от неё нет.

**О чём:** Helpdesk API собирается с нуля слой за слоем, и на каждом шаге видно, что скрывает декоратор `@Injectable()`, когда его пишут не глядя: свой мини-DI контейнер и метаданные декораторов, границы модулей и provider scopes, DTO и `ValidationPipe`, Prisma и транзакции, JWT-ротация refresh-токенов с reuse-detection, RBAC и владение через `TicketPolicy`, доменные события, WebSocket-шлюз с комнатами и своей авторизацией на handshake, свой динамический модуль, unit- и e2e-тесты.

**Стек:** NestJS 11 + TypeScript (strict), Node 24+ (LTS), Prisma 7 + PostgreSQL 18, class-validator/class-transformer, `@nestjs/passport` + `passport-jwt` + `@nestjs/jwt` + argon2, `@nestjs/event-emitter`, `@nestjs/websockets` (Socket.IO), `@nestjs/swagger`, helmet + `@nestjs/throttler`, `@nestjs/terminus`, Jest + supertest. Всё в Docker.

> Prisma 7 везде (NestJS- и GraphQL-лабы): в командах стоит `@7`, потому что на npm у `prisma` сейчас latest — 8.0 RC. NestJS закреплён на 11 (`@nestjs/cli@11`): `@latest` создаёт NestJS 12.

**Формат:** методичка [`nestjs.html`](nestjs/nestjs.html) — открывается в браузере, прогресс по чекбоксам сохраняется локально.

**Что внутри (5 сессий):**
- **Сессия 1** — фундамент: TypeScript-минимум для Nest, DI руками (свой мини-контейнер), модули, конфиг с валидацией
- **Сессия 2** — база данных: Docker, Prisma и первая миграция, DTO и `ValidationPipe`, CRUD тикетов, ошибки Prisma в HTTP, транзакции и история изменений
- **Сессия 3** — пользователи и безопасность: регистрация и хэши (argon2), логин и `JwtStrategy`, глобальный guard и `@Public()`/`@CurrentUser()`, refresh-токены с ротацией и reuse-detection, роли и владение (`TicketPolicy`)
- **Сессия 4** — комментарии и внутренние заметки, доменные события, WebSocket-шлюз с комнатами, middleware/interceptors, Swagger, безопасность (CORS, helmet, rate limit)
- **Сессия 5** — unit- и e2e-тесты, свой динамический модуль, health-чеки и graceful shutdown, Docker, "Production Hell" — финальный сценарий без подсказок

Разделы 1–8 методички — теория (разбор задачи, как NestJS устроен внутри, итоговая архитектура, стек и структура, access/refresh-аутентификация, сценарий жизненного цикла тикета, Pipes/Guards/Interceptors/Filters, real-time и доменные события), раздел 9 — пять сессий заданий, разделы 10–13 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 12. GraphQL Lab (`graphql/`)

> **Сложность: высокая.** Проект полностью самостоятельный (свой репозиторий `graphql-lab`), ни от одной другой лабы не зависит — домен другой (каталог фильмов, а не Helpdesk). Из знаний пригодятся основы NestJS (модули, DI, декораторы) и TypeScript на уровне «классы, интерфейсы, async/await» — всё остальное объясняется по ходу.

**О чём:** CineGraph — каталог фильмов, режиссёров и рецензий, спроектированный так, чтобы естественно упереться во все ключевые темы GraphQL: язык запросов и жизненный цикл запроса, N+1 в резолверах и `DataLoader`, JWT и права на уровне полей, интерфейсы и юнионы (фильмография, поиск), курсорная пагинация рецензий (Relay Connection), подписки на живую ленту через Redis, защита от тяжёлых запросов (depth limit + query complexity).

**Стек:** NestJS + `@nestjs/graphql` + Apollo Server (code-first: `@ObjectType`/`@Field`/`@Resolver`), Prisma 7 + PostgreSQL 18, `dataloader` для батчинга, `@nestjs/jwt` + bcryptjs, `graphql-subscriptions`/`graphql-redis-subscriptions` + Redis, `graphql-query-complexity`. Всё в Docker.

**Формат:** методичка [`graphql.html`](graphql/graphql.html) — открывается в браузере, прогресс по чекбоксам сохраняется локально.

**Что внутри (3 сессии):**
- **Сессия 1** — инфраструктура и схема: репозиторий и NestJS, docker-compose (Postgres + Redis), модель данных и seed, первые `ObjectType`/`Query`, резолверы полей наивно, воспроизводим и считаем N+1, input-типы
- **Сессия 2** — DataLoader, мутации, ошибки, права, полиморфизм: DataLoader на каждый запрос, вычисляемые поля, JWT-мутации, мутации рецензий с guard и владением, формат ошибок и маскировка, права на уровне полей и ролей, интерфейсы и юнионы, курсорная пагинация
- **Сессия 3** — подписки, Redis, защита, тесты: живая лента рецензий, два инстанса и Redis Pub/Sub, клиент без библиотек (`fetch` + `graphql-ws`), depth limit и query complexity, unit- и e2e-тесты, "Production Hell" — финальный сценарий без подсказок

Разделы 1–8 методички — теория (типичные заблуждения о GraphQL, как GraphQL устроен внутри, итоговая архитектура, стек и структура, N+1 и DataLoader, сценарий жизни одной рецензии, ошибки и nullability, пагинация/безопасность/кэш), раздел 9 — три сессии заданий, разделы 10–13 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 13. Laravel Lab (`laravel/`)

> **Сложность: высокая.** Нужно перед стартом: базовый Laravel (роутинг, контроллеры, миграции, Blade — даются ссылками на документацию, без разбора), ООП на PHP (см. `php-coffee/`) и общее представление про очереди (см. `rabbitmq/`) — лаба на них ссылается, а не объясняет заново.

**О чём:** Laravel 13 "изнутри" — не "как вызвать", а что происходит на каждом слое фреймворка (~30 компонентов `illuminate/*`, связанных через контейнер), на сквозном таск-трекере **TaskFlow** с воркспейсами, ролями и приглашениями.

**Стек:** Laravel 13 (PHP 8.4) + PostgreSQL 18 + Redis 8 + RabbitMQ 4 + Mailpit + Laravel Reverb; фронт — Vue 3 + Vite (JavaScript, только API-клиент). Всё в Docker.

**Формат:** методичка `laravel.html` — не пройдена, ниже план по оглавлению.

**Что внутри (10 сессий):**
- **Сессия 1** — стенд (Docker, Laravel 13, Sanctum/Reverb/RabbitMQ-драйвер), схема данных и миграции
- **Сессия 2** — Eloquent: связи, pivot, N+1 — разбираем боль по шагам (`hasMany`/`belongsTo`, `belongsToMany` + свой Pivot-класс, `attach`/`sync`/`toggle`, полиморфные связи, `hasManyThrough`)
- **Сессия 3** — коллекции (`groupBy`/`partition`/`reduce`/`keyBy`), API Resources (`whenLoaded`/`whenCounted`), три вида пагинации
- **Сессия 4** — HTTP-слой: Form Requests, своё middleware с параметром, обработка исключений API, полноценный CRUD задач
- **Сессия 5** — Service Container и провайдеры: `build`/`bind`/`call` изнутри, contextual binding (`when`/`needs`/`give`)
- **Сессия 6** — Auth: Sanctum SPA (cookie + CSRF), Gate и Policy, роли, приглашения по токену + минимальный Vue-фронт (логин, доска)
- **Сессия 7** — Observer (жизненный цикл модели), события и Listeners, Job (retry, `ShouldBeUnique`, `failed_jobs`) на RabbitMQ — та же схема, что в RabbitMQ-лабе
- **Сессия 8** — Mailable (markdown-письма, очередь), Notification (mail + database), Scheduler (дайджест задач)
- **Сессия 9** — `Cache::remember` + инвалидация в Observer, `Cache::lock` от гонки, RateLimiter, Broadcasting через Reverb + Echo
- **Сессия 10** — фабрики для всех моделей, feature-тесты (`RefreshDatabase`), fakes/моки (Event/Notification/Mail), финальный прогон

Лаба построена вокруг карты Laravel (`Kernel → Middleware → Router → Controller`, плюс сквозные Container/Events/Auth и менеджеры Database/Cache/Queue/Mail/Broadcasting) и проходит по каждому слою последовательно — от жизненного цикла запроса до тестов.

---

## 14. PostgreSQL Lab (`postgresql/`)

> **Сложность: средняя–высокая.** Проект полностью самостоятельный (свой репозиторий `postgresql-lab`, только SQL-файлы и `docker-compose.yml`), ни от одной другой лабы не зависит — общая с OOP- и PHP-лабами только идея «кофейни». Входной уровень — «умею SELECT/INSERT»; если JOIN пока «тёмный лес», есть вводная сессия 0. Параллели с Laravel/Eloquent даны по ходу, но фреймворк знать не обязательно.

**О чём:** Postgres есть почти в каждой лабе, но везде он был «чёрным ящиком за ORM». Здесь — то, что происходит под ORM, на базе кофейни с реальным объёмом данных (20 кофеен, 100 000 клиентов, 1 000 000 заказов, 2,5 млн позиций, 3 млн событий): устройство Postgres изнутри (процессы, страницы, shared buffers, WAL, планировщик), чтение `EXPLAIN (ANALYZE, BUFFERS)`, индексы под конкретный запрос (B-tree, частичные, функциональные, покрывающие, GIN, BRIN), статистика, N+1 глазами базы, изоляция и аномалии, блокировки и дедлоки, MVCC и VACUUM, партиционирование.

**Стек:** PostgreSQL 18 в Docker + `psql` + `pgbench`; расширения `pg_stat_statements`, `pg_trgm`, `pageinspect`, `btree_gist`. Никакого фреймворка и ORM.

**Формат:** методичка [`postgresql.html`](postgresql/postgresql.html) — методичка готова, прохождение впереди. У каждого шага — «Под капотом» и тренировка с ответами под спойлером; главный артефакт — журнал `NOTES.md` с планами «до/после».

**Что внутри (7 сессий):**
- **Сессия 0** — JOIN с нуля на песочнице из пяти клиентов и семи заказов: INNER/LEFT/RIGHT/FULL, ловушка «условие в WHERE», self-join, anti- и semi-join, JOIN + GROUP BY
- **Сессия 1** — Postgres в Docker с инструментами наблюдения, `psql` как рабочее место, схема кофейни, миллион заказов за минуту, SQL-инструментарий (CTE, оконные функции, FILTER, LATERAL), как таблица лежит на диске
- **Сессия 2** — EXPLAIN и B-tree: от Seq Scan на миллион строк до 20 прочитанных записей, составные индексы, статистика, частичные, функциональные и покрывающие индексы
- **Сессия 3** — алгоритмы JOIN и `work_mem`, GIN и BRIN, расширенная статистика, N+1 через `pg_stat_statements`, пагинация, охота на медленные запросы
- **Сессия 4** — транзакции и изоляция: потерянное обновление через `pgbench`, Read Committed, Repeatable Read, Serializable и write skew, ограничения как последняя линия обороны
- **Сессия 5** — блокировки: `FOR UPDATE`, очередь на `SKIP LOCKED`, дедлок, `pg_blocking_pids()`, миграции без простоя, advisory locks
- **Сессия 6** — MVCC и VACUUM изнутри (`pageinspect`, `xmin`/`xmax`, горизонт, HOT, wraparound), партиционирование журнала событий, "Production Hell" — задания без подсказок

Разделы 1–8 методички — теория (чего не видно из ORM, как PostgreSQL устроен внутри, архитектура и схема данных, стек и структура, индексы, как читать EXPLAIN, транзакции и блокировки, MVCC/VACUUM/партиционирование/N+1), раздел 9 — семь сессий заданий, разделы 10–13 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 15. Nuxt Lab — Help Center (`nuxt/`)

> **Сложность: высокая.** Проект полностью самостоятельный (свой репозиторий `nuxt-lab`), кода из других лаб не берёт. Vue предполагается знакомым на уровне Vue-лабы (`ref`, `computed`, props/emits, Pinia, Router — не объясняются заново), TypeScript — на уровне сессий 1–3 TS-лабы. Логично проходить после Vue и TypeScript.

**О чём:** публичный центр поддержки, где у каждой зоны свой режим рендеринга: база знаний — prerender (SSG), статус сервисов — SWR-кеш, обращения клиента — SSR с сессией, кабинет агента — SPA (`ssr: false`). Всё, что Nuxt добавляет поверх Vue: SSR и гидрация, payload, Nitro, состояние на сервере, `routeRules`, SEO. Почти в каждой сессии — шаг «сначала сломать, потом починить»: двойной запрос, hydration mismatch, потерянная cookie, утечка состояния между пользователями, общий кеш на все запросы.

**Стек:** Nuxt 4.5+ (с пометками про v5), TypeScript strict + `nuxi typecheck`, Nitro server routes, SQLite + Drizzle, Zod-схемы в `shared/`, nuxt-auth-utils, `@pinia/nuxt`, Nuxt Content v3, `@nuxtjs/sitemap` + `@nuxtjs/robots`, Vitest + `@nuxt/test-utils`, Docker Compose.

**Формат:** методичка [`nuxt.html`](nuxt/nuxt.html) — методичка готова, прохождение впереди. У каждого шага: код → «зачем» → команда → ожидаемый результат → «проверь себя».

**Что внутри (6 сессий, ~20,5 ч):**
- **Сессия 1** — стенд и основы: скаффолд Nuxt 4, файловый роутинг, layouts, что генерирует `.nuxt/`, SSR vs SPA руками (`view-source`, `ssr: false`, `ClientOnly`)
- **Сессия 2** — данные и гидрация: server route и тип ответа из хендлера, payload и двойной запрос через `$fetch`, `useFetch` (query, `lazy`, `pick`, `refresh`), ошибки, hydration mismatch
- **Сессия 3** — Nitro и БД: Drizzle + SQLite, `readValidatedBody` + Zod, middleware request-id, одна схема в `shared/` на клиент и сервер, форма обращения
- **Сессия 4** — авторизация и состояние: nuxt-auth-utils и роли, route middleware, cookie при SSR, утечка состояния через модульный `ref` → `useState`/`useCookie`, Pinia + `callOnce`, кабинет агента на `ssr: false`
- **Сессия 5** — контент, кеш, рендеринг: Nuxt Content v3, `defineCachedEventHandler` и ключ кеша, `routeRules` (пререндер, SWR) на prod-сборке, инвалидация
- **Сессия 6** — SEO и продакшн: `useSeoMeta`, sitemap/robots, `runtimeConfig`, тесты (unit, компонент, e2e), `nuxt build` и multi-stage Dockerfile, финал «Vue Lab vs Nuxt Lab»

Разделы 1–10 методички — теория (зачем Nuxt поверх Vue, азбука, рендеринг и гидрация под капотом, режимы рендеринга, данные, Nitro, состояние на SSR, авторизация, контент и SEO, структура проекта), раздел 11 — шесть сессий заданий, разделы 12–15 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 16. Angular Lab — RoomBook (`angular/`)

> **Сложность: высокая.** Проект полностью самостоятельный (свой репозиторий `angular-lab`), кода из других лаб не берёт. TypeScript — на уровне сессий 1–3 TS-лабы; всё специфичное для Angular (декораторы, DI, сигналы) объясняется в самой лабе. Опыт Vue полезен для сравнений, но не обязателен. Во фронтенд-треке идёт последней, после Nuxt: теория начинается с «зачем Angular после Vue и Nuxt».

**О чём:** внутренний сервис бронирования переговорных — каталог комнат, расписание дня, форма брони с проверкой пересечений, «мои брони», живые обновления, админка. Современный Angular — это сигналы + DI: реактивность без zone.js, сервисы и провайдеры, `httpResource`, Signal Forms, guards по ролям и RxJS там, где он правда нужен. Почти в каждой сессии — шаг «сломать → починить»: мутация массива, которую OnPush не видит, гонка ответов поиска, провайдер не на том уровне DI, 409 после проверки «свободно», утечка броней при смене пользователя, накопление SSE-соединений.

**Стек:** Angular 22 (standalone, zoneless, OnPush по умолчанию), Angular CLI + `@angular/build`, `HttpClient` + интерцепторы + `httpResource`, Signal Forms и Reactive Forms, RxJS 7 + rxjs-interop, Vitest через `ng test`; готовый API — `api/server.mjs` на Node 24 без зависимостей; Docker Compose, в проде nginx.

**Формат:** методичка [`angular.html`](angular/angular.html) — методичка готова, прохождение впереди. У каждого шага: код → «зачем» → команда → ожидаемый результат → «проверь себя».

**Что внутри (6 сессий, 26 шагов, ~20,5 ч):**
- **Сессия 1** (~3 ч) — стенд и основы: готовый API и `ng new`, компоненты с `input`/`output` и `@for`, `signal`/`computed`/`model`/`linkedSignal`/`effect`; ломаем OnPush + zoneless мутацией массива (счётчик растёт, а сетка нет)
- **Сессия 2** (~3,5 ч) — DI и HTTP: сервисы, уровни провайдеров и `InjectionToken` (провайдер не на том уровне), `HttpClient` + `toSignal`, `httpResource` с фильтрами на сервере, поиск без гонки ответов (`mergeMap` → `switchMap`), интерцепторы лога и ошибок
- **Сессия 3** (~3 ч) — роутер: маршруты, lazy-загрузка, AppShell, дочерние маршруты расписания (и параметры родителя), resolver и индикатор навигации, query params как состояние
- **Сессия 4** (~4 ч) — формы: Signal Forms (модель и схема), межполевая валидация, `validateHttp` для проверки свободного слота, submit и 409 после «свободно», свой контрол, Reactive Forms в админке
- **Сессия 5** (~3,5 ч) — авторизация, состояние, потоки: AuthStore, вход, токен и 401, guards `canActivate`/`canMatch`/`canDeactivate`, стор на сигналах и утечка броней при смене пользователя, SSE + RxJS и `takeUntilDestroyed`
- **Сессия 6** (~3,5 ч) — качество и продакшн: pipe и `@defer`, тесты (компонент, стор, guard) на Vitest, сборка, runtime-конфиг и nginx, финальная карта и сравнение с Vue/Nuxt

Разделы 1–9 методички — теория (зачем Angular после Vue и Nuxt, азбука, реактивность на сигналах, DI под капотом, RxJS в 2026 году, роутер, формы, HTTP, стек и структура проекта), раздел 10 — шесть сессий заданий, разделы 11–14 — чек-лист, глоссарий, вопросы для собеседования, что дальше.

---

## 17. CSS Lab — FrontFest (`css/`)

> **Сложность: базовая.** Проект самостоятельный, кода из других лаб не берёт. Нужны только HTML и умение открыть страницу в браузере. Во фронтенд-треке идёт первой — до Tailwind и JavaScript.

**О чём:** современный CSS с нуля на сайте фронтенд-конференции: главная, программа-таймлайн, регистрация. Разметка выдаётся готовой, пишутся только стили. Каскад и слои → токены, цвет и темы → Flexbox → Grid и subgrid → адаптив, container queries, `:has()` и формы → позиционирование, анимации, view transitions и сборка.

**Стек:** чистый CSS, без фреймворков и препроцессоров.

**Формат:** методичка [`css.html`](css/css.html) — методичка готова и вычитана (30.09), прохождение впереди.

**Что внутри (6 сессий, ~20 часов):** основы и каскад; токены, цвет, темы, текст; Flexbox; Grid; адаптив, container queries, `:has()`, формы; позиционирование, движение, view transitions, сборка. Разделы 1–9 — теория, раздел 10 — сессии, разделы 11–14 — чек-лист, глоссарий, вопросы, что дальше.

---

## 18. Tailwind Lab — Pulse (`tailwind/`)

> **Сложность: базовая.** Проект самостоятельный, кода из других лаб не берёт. Нужно уверенное знание CSS — удобнее после CSS Lab: Tailwind не заменяет каскад, flex, grid и `:has()`, а записывает их классами. Во фронтенд-треке идёт второй, до JS.

**О чём:** Tailwind CSS v4 с нуля на сервисе аналитики «Pulse»: маркетинговый лендинг, дашборд и страница настроек. Азбука утилит → тема через `@theme` → варианты и состояния → адаптив и container queries → тёмная тема, формы и переиспользование → продакшн. Разметку пишете сами; почти в каждой сессии шаг «сломать → починить» (динамический класс, которого нет в сборке, `peer`, который «не видит» чекбокс, `@apply` с «unknown utility»).

**Стек:** Tailwind CSS 4.3, Vite + `@tailwindcss/vite`, чистый HTML и немного JS; Docker (dev на Vite, prod на nginx).

**Формат:** методичка [`tailwind.html`](tailwind/tailwind.html) — методичка готова и вычитана (30.09), прохождение впереди.

**Что внутри (6 сессий, ~20 ч):** стенд и азбука; тема `@theme`; варианты и состояния; адаптив и container queries; тёмная тема, формы, `@layer components`, typography; продакшн и таблица «CSS-лаба ↔ Tailwind-лаба». Разделы 1–9 — теория, раздел 10 — сессии, 11–14 — чек-лист, глоссарий, вопросы, что дальше.

---

## 19. Inertia Lab — Inkwell (`inertia/`)

> **Сложность: средняя.** Проект самостоятельный (свой репозиторий `inertia-lab`), кода из других лаб не берёт. Предполагается знакомство с Laravel (контроллеры, Eloquent, FormRequest, Policies — уровень Laravel Lab) и с Vue 3 (Composition API — уровень Vue Lab); сам мост Inertia объясняется с нуля. Логичнее всего идёт после Laravel-лабы.

**О чём:** блог-платформа Inkwell на Laravel 13 + Inertia 3 + Vue 3 + TypeScript, собранная без starter kit. Протокол Inertia (объект страницы, XHR-визиты, конфликт версий, 303-редиректы) → props как публичный API (API Resources, `optional`/`defer`/`merge`/`once`) → путь формы и валидации без 422 → SSR и его типичные поломки (hydration mismatch, Pinia-утечка между посетителями). Три роли — reader, author, editor — на `Policies`, без дублирования прав на фронте.

**Стек:** Laravel 13 (PHP 8.4), `inertiajs/inertia-laravel` + `@inertiajs/vue3` 3, Vue 3 (`<script setup lang="ts">`), TypeScript strict, Pinia, Laravel Wayfinder, Tailwind CSS 4, SQLite.

**Формат:** методичка [`inertia.html`](inertia/inertia.html) — методичка готова и вычитана (04.10.2026), прохождение впереди.

**Что внутри (5 сессий, ~16,5 ч):** протокол и фундамент (Inertia руками, лента, layout, Wayfinder); страница поста (SEO, SSR — включаем, ломаем, чиним); пользователи и формы (сессии, flash, Pinia, Policies, редактор); данные и производительность (фильтры, бесконечная лента, deferred props, polling); тесты, сборка, SSR в проде, Production Hell. Разделы 1–8 — теория, раздел 9 — сессии, 10–13 — чек-лист, глоссарий, вопросы, что дальше.

---

## 20. Laravel Performance Lab — CoffeePerf (`laravel-performance/`)

> **Сложность: базовая.** Проект самостоятельный (свой репозиторий `laravel-performance-lab`), кода из других лаб не берёт. Нужен базовый Laravel (маршруты, контроллеры, Eloquent) и Docker Compose на уровне «поднять и посмотреть логи»; всё остальное — k6, профилировщики, OPcache, Octane — объясняется с нуля.

**О чём:** измерять, а не гадать. Приложение Coffee Shop с намеренными проблемами (N+1, тяжёлый отчёт без индекса) и миллионом заказов; каждое изменение подтверждается цифрами «до / после» при одних и тех же условиях прогона.

**Стек:** Laravel 13 (PHP 8.4), PostgreSQL 18, Redis 8, nginx 1.30, k6, Debugbar и Telescope, SPX и Blackfire, OPcache и JIT, Octane + FrankenPHP. Всё в Docker Compose.

**Формат:** методичка [`laravel-performance.html`](laravel-performance/laravel-performance.html) — методичка готова и вычитана (04.10.2026), прохождение впереди.

**Что внутри (9 сессий, ~36 ч):**
- **Сессия 1** — стенд, датасет в 1 млн заказов, приложение с проблемами; перцентили, первый замер curl и ApacheBench
- **Сессия 2** — k6 с нуля: smoke, load, stress, spike, пороги и код возврата; таблица «ДО»
- **Сессия 3** — Debugbar и Telescope; запрет lazy loading и починка N+1; почему Telescope нельзя на прод
- **Сессия 4** — SPX, wall-time против CPU, flamegraph отчёта, правка и замер; Blackfire
- **Сессия 5** — OPcache и его настройки для продакшна, поломка со «старым кодом»; JIT и честный замер
- **Сессия 6** — `optimize` и `route:cache`, `env()` вне конфигов, кеш с тегами в Redis, cache stampede и блокировки, индексы и `EXPLAIN`
- **Сессия 7** — Octane на FrankenPHP: модель, запуск в Docker, сравнение с PHP-FPM на k6, перезагрузка воркеров
- **Сессия 8** — подводные камни Octane: чужие данные между пользователями, scoped-привязка, утечки памяти; итоговое сравнение
- **Сессия 9** — таблица «до → после», бюджет p95 и регрессионный тест k6 в CI, prod-образ, чек-лист «тормозит — что делать»

---

## 21. Algorithms PHP Lab — CoffeeAlgo (`algorithms-php/`)

> **Сложность: базовая.** Проект самостоятельный (свой репозиторий `algorithms-php-lab`), кода из других лаб не берёт. Нужен только синтаксис PHP; первые сессии используют лишь циклы, массивы и функции, сложное нарастает постепенно.

**О чём:** алгоритмы и структуры данных на PHP — от «сколько шагов делает цикл» до задач с собеседований. Каждая тема — на задаче кофейни, с тестом PHPUnit и замером времени; в большинстве тем есть шаг «сломать → починить» (невидимый O(n²), вырожденное дерево, обход без пометки посещённых).

**Стек:** PHP 8.4 CLI, SPL, PHPUnit, Composer (только автозагрузка), Docker.

**Формат:** методичка [`algorithms-php.html`](algorithms-php/algorithms-php.html) — методичка готова и вычитана (04.10.2026), прохождение впереди.

**Что внутри (13 сессий, ~44 ч):** сложность без формул и замер; массивы и строки; хеш-таблицы и множества; стек и очередь; связные списки; рекурсия; бинарный поиск и сортировки (включая устойчивость); два указателя, скользящее окно, префиксные суммы; деревья (BST, обходы); кучи и топ-K; графы (BFS, DFS, Дейкстра); динамическое программирование (размен монет, рюкзак, LCS); разбор собеседований со шаблоном ответа, пятью задачами с замером и шпаргалкой по сложностям.

---

## 22. Caddy Lab — Edge (`caddy/`)

> **Сложность: средняя.** Проект самостоятельный (свой репозиторий `caddy-lab`), кода из других лаб не берёт. Решает ту же задачу, что Traefik Lab (reverse proxy, TLS), но другим инструментом — методичка не требует Traefik Lab как предшественника.

**О чём:** один Caddy перед сайтом, API, WebSocket и PHP — от первого запуска до сборки своих модулей на Go. Проект **Edge**: статический сайт, reverse proxy к Node.js-бэкендам, автоматический HTTPS без единой настройки, балансировка и отказоустойчивость, безопасность, Caddy в Docker, PHP через FastCGI, логи и метрики, продвинутый Caddyfile, Admin API, расширение через `xcaddy`, продакшн — служба, кластер, чек-лист. Все примеры конфигов проверены на Caddy **v2.11.7**.

**Стек:** Caddy 2 (Caddyfile + JSON-конфиг), Docker Compose, PHP-FPM через FastCGI, `xcaddy` для сборки модулей на Go.

**Формат:** методичка [`caddy.html`](caddy/caddy.html) — методичка написана и частично проверена на реальном Caddy (сессии 1–6, 9–11); вычитка проектом и прохождение впереди.

**Что внутри (13 сессий, ~48 ч):** первый запуск и Caddyfile; статический сайт (сжатие, кеш, редиректы, SPA, свои страницы ошибок); reverse proxy (WebSocket и SSE без спецнастроек, заголовки X-Forwarded); автоматический HTTPS (локальный CA, Let's Encrypt, On-Demand TLS); балансировка и отказоустойчивость (политики, health-checks, канарейка); безопасность (basic_auth, forward_auth, лимиты); Caddy в Docker и Compose; PHP и FastCGI; логи, метрики, отладка; продвинутый Caddyfile (матчеры, сниппеты, CEL); Admin API и JSON-конфиг; расширение через `xcaddy` и свой модуль на Go; продакшн — systemd, сеть, кластер, финальный аудит.

---

## Все работы и прогресс (`works/progress.html`)

Одна страница со ссылками на все лабы и общим прогрессом по каждой: отметки разделов и шагов из методичек (хранятся в `localStorage` браузера) складываются в проценты. Кнопка «Все работы» есть в каждой методичке рядом с поиском и переключателем темы, а пункт «прогресс» — в шапке сайта, на страницах лаб и в хронологии. Рядом — страница [«Что чем проверено»](works/verification.html) (`python3 tools/build-verification.py`, собирается из `fixes/common/_verification.md`). Страница прогресса собирается скриптом `python3 tools/build-progress.py` (запускать заново при добавлении лабы), а ссылка и правка шаблона вставляются в методички через `python3 tools/patch-manuals.py`. Прогресс виден, только когда страница и методички открыты с одного адреса (GitHub Pages или `python3 -m http.server`).

---

## Витрина работ (`works/`)

Отдельный сабмодуль [`works-lab`](https://github.com/meeymirita/works-lab) со стилизованными обзорными страницами каждой лабы (дизайн в стилистике аниме-заставки, тот же, что и у [`index.html`](index.html)): что внутри, стек, куда открыть методичку и репозиторий. Там же лежат превью-картинки лаб (`works/images/`), которые использует и главная страница.

Открыть можно прямо по ссылке `works/<ключ-лабы>.html`, например [`works/rabbitmq.html`](works/rabbitmq.html).

---

## Клонирование

Репозиторий использует submodule, поэтому клонировать нужно с флагом `--recurse-submodules`:

```bash
git clone --recurse-submodules https://github.com/meeymirita/anitech-performance.git
```

Если репозиторий уже склонирован без этого флага:

```bash
git submodule update --init --recursive
```

## Добавление новой работы

```bash
git submodule add <url-репозитория-лабы> <папка>
git commit -m "Add <название> lab"
```

## Обновление сабмодуля до последнего коммита

```bash
cd <папка-лабы>
git pull origin main
cd ..
git add <папка-лабы>
git commit -m "Update <папка-лабы> submodule"
```

## Автор

Все лабы веду и прохожу самостоятельно, попутно ведя заметки и методички по каждой теме.
