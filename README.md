# Лабораторная работа №1. Автоматизация сборки 2D игры через командную строку (CLI)

* **Дисциплина:** Автоматизация разработки программного обеспечения (АРПО)
* **Выполнила:** Студентка группы 23-СТ Вустина З.Д.
* **Проверил:** Старший преподаватель кафедры ВСиС Бровко Н.В.
* **Учреждение:** УО «Полоцкий государственный университет имени Евфросинии Полоцкой», Факультет информационных технологий

---

## Цель работы
Освоить автоматизацию сборки Unity-проекта через интерфейс командной строки (CLI): написать Editor-скрипт на основе `BuildPipeline`, выполнить компиляцию WebGL-версии 2D-игры в фоновом режиме (`batchmode`), проанализировать лог сборки проекта и организовать рабочий процесс в системе контроля версий Git (работа с ветками, фиксация изменений, создание Pull Request и организация процесса Peer Review).

---

## Ход выполнения работы

### Шаг 1. Инициализация проекта
<img width="475" height="336" alt="image" src="https://github.com/user-attachments/assets/02a3b3d8-01f3-47ff-aaec-8da873743438" />
<img width="450" height="336" alt="image" src="https://github.com/user-attachments/assets/07c5b17f-ee74-4c31-a98c-94bdd07e895e" />
<img width="956" height="605" alt="image" src="https://github.com/user-attachments/assets/c05fff19-66cd-4cd4-a7a1-1fe47c326a19" />


В Unity Hub был развернут новый проект на базе стандартного шаблона **2D Platformer Microgame**. В окне настроек проекта была проверена и подключена основная игровая сцена.

### Шаг 2. Создание скрипта сборщика
<img width="488" height="475" alt="image" src="https://github.com/user-attachments/assets/e6245f9b-68f2-4b08-aaec-97a652a30b9e" />
<img width="526" height="475" alt="image" src="https://github.com/user-attachments/assets/52513ae2-5462-482c-8c29-58c1857b024c" />

Внутри каталога `Assets` была создана специализированная служебная папка `Editor`, код в которой выполняется исключительно внутри редактора Unity. Внутри неё размещён C#-скрипт `BuildManager.cs`, автоматизирующий сборку игры под WebGL с помощью вызова `BuildPipeline.BuildPlayer()`.

### Шаг 3. Настройка параметров публикации WebGL
<img width="487" height="475" alt="image" src="https://github.com/user-attachments/assets/d5f37d69-082b-4fb3-b4b5-dcb0607b7d88" />

В окне `Project Settings -> Player -> Publishing Settings` формат сжатия проекта (`Compression Format`) был переведён в режим **Disabled**. Данное действие необходимо для возможности проведения локального тестирования собранного веб-пакета без конфликтов политик безопасности.

### Шаг 4. Автоматическая сборка проекта из терминала (CLI)
Редактор Unity был закрыт для освобождения ресурсов и блокировок файлов проекта. В терминале Windows PowerShell, открытом в корневом каталоге проекта, была запущена команда компиляции в фоновом режиме без инициализации графической оболочки:
```powershell
& "C:\Program Files\Unity\Hub\Editor\6000.3.11f1\Editor\Unity.exe" -batchmode -nographics -executeMethod BuildManager.BuildWebGL -quit -logFile build_webgl.log
```

### Шаг 5. Анализ результатов сборки и логов
<img width="844" height="313" alt="image" src="https://github.com/user-attachments/assets/ab3cae85-f12f-4052-8a92-749bc580b6fb" />

После завершения фонового процесса в корне проекта сформировался файл `build_webgl.log`. В его финальной части была успешно зафиксирована запись `[CI/CD] УСПЕХ! WebGL билд успешно создан.`. В папке `Builds/WebGL` сгенерировался готовый набор файлов: `index.html`, каталоги `Build` и `StreamingAssets`.

### Шаг 6. Локальная проверка работоспособности игры
Каталог `Builds/WebGL` был открыт в редакторе Visual Studio Code, где с помощью локального сервера расширения **Live Server** проект был запущен по адресу `http://127.0.0.1:5500`. Микроигра загрузилась и функционирует корректно.
<img width="844" height="343" alt="image" src="https://github.com/user-attachments/assets/e0449150-684a-4303-84e2-c232d373a9b4" />
<img width="844" height="460" alt="image" src="https://github.com/user-attachments/assets/3c3e21a1-6f4c-42de-832c-8dcf757641dd" />

### Шаг 7. Организация проекта в системе контроля версий Git
<img width="844" height="453" alt="image" src="https://github.com/user-attachments/assets/efe79a6b-1f72-4623-870a-65d53301bdf6" />

В корневой папке был сконфигурирован файл `.gitignore` для исключения тяжеловесных временных файлов движка (`Library/`, `Temp/` и др.). Код был последовательно зафиксирован в репозитории: базовая структура опубликована в ветке `main`, а автоматизированный код и скриншоты — в отдельной целевой ветке `LR1`. На GitHub сформирован Pull Request на слияние веток.

---

## Исходный C# код скрипта автоматизации

```csharp
using System;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

public static class BuildManager
{
    private static readonly string WebGLBuildPath = "Builds/WebGL";

    public static void BuildWebGL()
    {
        Debug.Log("[CI/CD] Запущен автоматический процесс сборки WebGL...");
        string[] levels = GetScenes();

        if (levels.Length == 0)
        {
            Debug.LogError("[CI/CD] Ошибка: В Настройках Сборки (Build Settings) не найдено ни одной активной сцены!");
            ExitWithCode(1);
            return;
        }

        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions
        {
            scenes = levels,
            locationPathName = WebGLBuildPath,
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        };

        BuildReport report = BuildPipeline.BuildPlayer(buildPlayerOptions);
        BuildSummary summary = report.summary;

        if (summary.result == BuildResult.Succeeded)
        {
            Debug.Log($"[CI/CD] УСПЕХ! WebGL билд успешно создан.");
            Debug.Log($"[CI/CD] Время сборки: {summary.totalTime.TotalSeconds:F2} сек. Размер: {summary.totalSize} байт.");
            ExitWithCode(0);
        }
        else
        {
            Debug.LogError($"[CI/CD] ОШИБКА СБОРКИ! Количество ошибок: {summary.totalErrors}");
            ExitWithCode(1);
        }
    }

    private static string[] GetScenes()
    {
        var editorScenes = EditorBuildSettings.scenes;
        int activeCount = 0;
        foreach (var scene in editorScenes)
        {
            if (scene.enabled) activeCount++;
        }

        string[] scenePaths = new string[activeCount];
        int index = 0;
        foreach (var scene in editorScenes)
        {
            if (scene.enabled)
            {
                scenePaths[index] = scene.path;
                index++;
            }
        }
        return scenePaths;
    }

    private static void ExitWithCode(int code)
    {
        if (Environment.CommandLine.Contains("-batchmode"))
        {
            EditorApplication.Exit(code);
        }
    }
}
```

---
<img width="974" height="524" alt="image" src="https://github.com/user-attachments/assets/87df73e6-e530-4735-9c6f-16ec3ac68cbe" />
<img width="974" height="595" alt="image" src="https://github.com/user-attachments/assets/1cd26ef7-4462-4bc4-81b7-d3bdfee808d8" />
<img width="563" height="475" alt="image" src="https://github.com/user-attachments/assets/96655762-f97b-47e6-943a-c5019ac3e8b0" />
<img width="458" height="390" alt="image" src="https://github.com/user-attachments/assets/e7220de9-60dd-4bde-aecf-2b1dacea61ae" />
<img width="473" height="396" alt="image" src="https://github.com/user-attachments/assets/b3a08a07-59bc-4ec2-bd0c-ff6d6948cb65" />


## Вывод по работе
В ходе лабораторной работы были изучены ключевые принципы DevOps-практик в геймдеве, в частности — автоматизация рутинных процессов компиляции игр. Был разработан кастомный статический класс для взаимодействия с `UnityEditor.API`, осуществлен запуск автономной сборки проекта через консольные флаги `-batchmode` и `-nographics`, а также успешно настроена локальная CORS-безопасная среда тестирования WebGL-приложений. Полученные навыки работы с ветвлением в Git и рецензированием кода закладывают фундамент для построения комплексных конвейеров непрерывной интеграции (CI/CD) на удаленных серверах.

---

## Ответы на контрольные вопросы

1. **Зачем в команде запуска CLI использовать флаг `-nographics` и какую роль он сыграет, когда мы перенесем пайплайн на удаленный сервер в облако?**
Флаг `-nographics` блокирует запуск графической подсистемы Unity и не пытается инициализировать видеокарту. Это критически важно при переносе сборки в облачные инфраструктуры (например, GitHub Actions, GitLab CI), функционирующие на базе Headless Linux-серверов. Без данного флага среда сборки завершится критическим сбоем, так как на удаленных агентах отсутствуют мониторы, дисплейные сервера (X11/Wayland) и дискретные графические адаптеры.

2. **Что произойдет, если запустить консольную сборку проекта, в настройках Build Settings которого не выбрана ни одна сцена игры? Какая строка нашего кода обрабатывает эту ситуацию?**
Если в настройках `Build Settings` проекта отсутствуют активные сцены, внутренняя компиляция Unity не сможет быть запущена, так как билд-системе будет нечего собирать. В разработанном скрипте данное исключение обрабатывается явной проверкой массива сцен: `if (levels.Length == 0)`. Скрипт записывает сообщение об ошибке в лог-файл, прерывает операцию сборки и корректно завершает работу всей программы Unity с кодом возврата `1`, сигнализирующим внешней автоматизированной системе о провале операции.

3. **Почему класс `BuildManager` и его методы обязательно должны быть объявлены как `public static`?**
Управляющий флаг запуска командной строки `-executeMethod` вызывает внешнюю программную точку входа по строковому шаблону `ИмяКласса.ИмяМетода`. На момент инициализации этого вызова проект только открывается, в памяти отсутствуют инициализированные игровые объекты сцены или компоненты типа `MonoBehaviour`. Вызов статического метода (`static`) позволяет выполнить код напрямую без создания экземпляра класса в памяти. Модификатор доступа `public` обязателен для того, чтобы внутренняя билд-система ядра Unity имела права увидеть и вызвать этот метод из внешней командной строки.
