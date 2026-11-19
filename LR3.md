# Лабораторная работа №3. Контейнеризация WebGL

Unity 6000.3.10f1. В параметрах платформы Web выбраны Gzip и выключенный Decompression Fallback. Для локального Docker-образа нужен настоящий результат сборки `BuildManager.BuildWebGL` в `Builds/WebGL/`.

```powershell
docker build -t apro-lr3-webgl:local .
docker run -d --name apro-lr3-webgl -p 127.0.0.1:8080:80 apro-lr3-webgl:local
docker exec apro-lr3-webgl nginx -t
curl.exe -I http://localhost:8080/Build/WebGL.wasm.gz
```

Игра загружается на http://localhost:8080. В локальной проверке запросы JavaScript, WASM и игровых данных вернули 200 и `Content-Encoding: gzip`. Для WASM сервер вернул `Content-Type: application/wasm`. Запрос отсутствующего WASM вернул 404. Изображение игры и журналы сохранены среди материалов дисциплины.

Workflow запускает Sanity Check и проверку контейнерной сборки для PR в `main`. Пуш в `main` основного репозитория запускает зеркалирование и публикацию образа в GHCR. На GitHub раннер подставляет gzip-заглушки для проверки упаковки. Облачный образ ЛР №3 предназначен для проверки контейнерного пайплайна.

- [GitHub Actions](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina/actions)
- [Пакет platformer-game](https://github.com/Zatik-Vustina/APRO_LR1_Zlata_Vustina/pkgs/container/platformer-game)
