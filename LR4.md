
# Лабораторная работа №4. Автоматизация тестирования Unity

**Вариант 3.** Метод `Health.Die()` из `Assets/Scripts/Mechanics/Health.cs` при начальных 3 HP доводит HP до 0 и переводит `IsAlive` в `false`.

- EditMode `EditMode_PlayerTag_IsCorrect` проверяет сцену `SampleScene`, тег Player и компоненты PlayerController и Health.
- PlayMode `PlayMode_PlayerTakesDamage_HealthDecreases` проверяет три вызова Decrement с начальным здоровьем 3.
- PlayMode `PlayMode_Variant3_Die_SetsHealthToZero` проверяет индивидуальный вариант. Для проверки точного HP тест считывает закрытое поле `currentHP` без изменения игрового API.

Локальный Unity Test Framework на Unity `6000.3.10f1` подтвердил один пройденный EditMode-тест и два пройденных PlayMode-теста. Тестовые asmdef ссылаются на `GameAssembly`.

В [GitHub Actions](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina/actions) после Sanity Check запускается GameCI CLI `v0.1.72` с обоими режимами. Ошибка задачи `run_tests` блокирует Docker-сборку и зеркалирование. Артефакт `test-results` сохраняет результаты или диагностику неудачного запуска. Unity Personal на раннере использует секреты `UNITY_LICENSE`, `UNITY_EMAIL` и `UNITY_PASSWORD`.
