# Лабораторная работа № 2. GitHub Actions: проверка Unity-проекта и резервное копирование

## 1. Цель работы

Настроить автоматическую проверку структуры Unity-проекта с помощью GitHub Actions и организовать автоматическое зеркалирование изменений в отдельный резервный репозиторий.

## 2. Используемые средства

- Git и GitHub для управления версиями проекта.
- GitHub Actions для автоматизации проверки и резервного копирования.
- YAML для описания CI workflow.
- Personal Access Token (PAT) для безопасного доступа к резервному репозиторию.

**Основной репозиторий:** [APRO_LR1_Zlata_Vustina](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina)

**Резервный репозиторий:** [APRO_LR1_Zlata_Vustina_backup](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina_backup)

## 3. Ход выполнения работы

### 3.1. Подготовка резервного репозитория

Создан отдельный репозиторий `APRO_LR1_Zlata_Vustina_backup`, предназначенный для хранения резервной копии проекта.

После успешного выполнения workflow в резервном репозитории появились основные каталоги Unity-проекта: `Assets`, `Packages`, `ProjectSettings`, а также файл конфигурации GitHub Actions и история коммитов.

### 3.2. Настройка токена доступа

<img width="862" height="791" alt="image" src="https://github.com/user-attachments/assets/2e128449-960c-4e17-8d58-247dd616df1b" />
<img width="867" height="900" alt="image" src="https://github.com/user-attachments/assets/25ef389b-4183-484c-8549-c97225810908" />
<img width="585" height="213" alt="image" src="https://github.com/user-attachments/assets/9fb53dd7-69cf-46c7-b5db-f80bd3073a44" />
<img width="697" height="409" alt="image" src="https://github.com/user-attachments/assets/a324bc7e-4c6d-44af-a0a2-a164334f9dcb" />

Создан Personal Access Token для предоставления GitHub Actions доступа к резервному репозиторию.

Токен сохранён в настройках Secrets основного репозитория под именем `BACKUP_TOKEN`. Значение токена хранится в секрете и не включается в исходный код workflow.

### 3.3. Создание GitHub Actions workflow

Создан файл `.github/workflows/main.yml`.

<img width="1280" height="690" alt="image" src="https://github.com/user-attachments/assets/c59da5ac-4364-4708-8b9a-81131a664f6d" />
<img width="1142" height="949" alt="image" src="https://github.com/user-attachments/assets/ba4b5148-9b13-4c8f-b865-db1f383cf18f" />


Workflow запускается при отправке изменений в ветку `main` и содержит два задания:

- `sanity_check` — проверка структуры Unity-проекта и поиск C#-скриптов.
- `mirror_repo` — отправка веток и тегов в резервный репозиторий после успешного завершения проверки.

Для организации последовательного выполнения заданий используется зависимость `needs: sanity_check`.

### 3.4. Проверка структуры Unity-проекта

В задании `sanity_check` выполняется проверка наличия каталогов:

- `Assets`;
- `Packages`;
- `ProjectSettings`.

Дополнительно выполняется поиск C#-скриптов, соответствующих шаблонам `*Controller.cs` и `BuildManager.cs`.

### 3.5. Настройка зеркалирования

В задании `mirror_repo` используется `actions/checkout@v4` с параметром `fetch-depth: 0`, чтобы получить полную историю Git.

Для доступа к резервному репозиторию применяется секрет `BACKUP_TOKEN`. Команды Git отправляют все локальные ветки и теги в резервный репозиторий.

Задание зеркалирования запускается только после успешного выполнения `sanity_check`.

### 3.6. Ветвление и объединение изменений

Изменения конфигурации workflow были подготовлены в ветке `LR2`, отправлены в GitHub и оформлены через Pull Request № 2.

<img width="1126" height="816" alt="image" src="https://github.com/user-attachments/assets/669ed219-0e73-45ea-8f10-a64922fbc5b6" />
<img width="1128" height="941" alt="image" src="https://github.com/user-attachments/assets/f2b315aa-6eb6-427f-83f5-5808c08f65e3" />
<img width="1122" height="792" alt="image" src="https://github.com/user-attachments/assets/416faa09-7419-4f14-989a-88fc1d1b0c7c" />
<img width="1212" height="988" alt="image" src="https://github.com/user-attachments/assets/65ced28c-12b9-4542-8554-4aaf168dacf9" />
<img width="1218" height="977" alt="image" src="https://github.com/user-attachments/assets/b195710a-e730-4e2f-b700-a13b30b13c8b" />



После проверки Pull Request был объединён с веткой `main`.

## 4. Результаты работы

В ходе выполнения лабораторной работы получены следующие результаты:

1. Создан резервный репозиторий для Unity-проекта.
2. Настроен секрет `BACKUP_TOKEN`.
3. Создан workflow GitHub Actions для проверки структуры проекта.
4. Настроено автоматическое зеркалирование в резервный репозиторий.
5. Изменения успешно объединены с веткой `main`.
6. Повторный запуск GitHub Actions завершился со статусом `Success`.
7. Оба задания — `Sanity Check` и `Mirror to backup repository` — завершились успешно.
8.
<img width="1218" height="977" alt="image" src="https://github.com/user-attachments/assets/4d87c6ac-81bd-4df9-94b4-859a7999f1e0" />
<img width="1210" height="804" alt="image" src="https://github.com/user-attachments/assets/0195bdac-c17a-48c9-97c0-2a91c81fa798" />


## 5. Контрольные ссылки

- [Основной репозиторий](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina)
- [Резервный репозиторий](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina_backup)
- [Запуски GitHub Actions](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina/actions)
- [Pull Requests](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina/pulls)

## 6. Вывод

В ходе лабораторной работы была настроена автоматизация проверки структуры Unity-проекта и резервного копирования средствами GitHub Actions. Проверка выполняется перед зеркалированием, а доступ к резервному репозиторию организован с использованием секрета GitHub. Успешный запуск workflow подтвердил работоспособность настроенной последовательности заданий.
