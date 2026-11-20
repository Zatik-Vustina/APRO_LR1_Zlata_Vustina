"""Build and send the GitHub Actions summary through Telegram Bot API."""

import http.client
import json
import os
import re
import sys
from urllib.parse import urlsplit


RESULTS = {"success", "failure", "cancelled", "skipped"}
HTTP_HELP = {
    400: "Проверьте идентификатор чата и отправьте боту /start.",
    401: "Проверьте TELEGRAM_BOT_TOKEN.",
    403: "Убедитесь, что бот может писать в чат и не заблокирован.",
    429: "Telegram ограничил частоту отправки.",
}


class NotificationError(Exception):
    """A diagnostic that is safe to display in Actions logs."""


def format_message(needs, author, sha, run_url, game_url="", check=False):
    """Use the actual upstream results, then add the run and commit context."""
    states = {job: state.get("result") for job, state in needs.items()}
    if not states or any(state not in RESULTS for state in states.values()):
        raise NotificationError("Не получены корректные результаты всех задач CI.")

    failed = [job for job, state in states.items() if state == "failure"]
    cancelled = [job for job, state in states.items() if state == "cancelled"]
    skipped = [job for job, state in states.items() if state == "skipped"]
    lines = ["Проверка уведомлений ЛР №6. Unity не запускалась."] if check else []
    if failed:
        lines.append("CI завершился с ошибкой.")
        lines.append(f"Ошибки задач: {', '.join(failed)}.")
    elif cancelled:
        lines.append("CI отменён.")
    elif skipped:
        lines.append("CI завершился без выполнения всех задач.")
    else:
        lines.append("Все проверяемые задачи завершились успешно.")
        if game_url:
            lines.append(f"Игра: {game_url}")
    if cancelled:
        lines.append(f"Отменены: {', '.join(cancelled)}.")
    if skipped:
        lines.append(f"Пропущены: {', '.join(skipped)}.")

    author = " ".join(author.split())[:160]
    lines.extend((f"Автор коммита: {author}", f"Коммит: {sha[:12]}", f"Прогон: {run_url}"))
    return "\n".join(lines)


def send_message(connection, token, chat_id, message):
    """Send a UTF-8 JSON POST without logging the URL or response data."""
    payload = json.dumps({"chat_id": chat_id, "text": message}, ensure_ascii=False)
    try:
        connection.request(
            "POST",
            f"/bot{token}/sendMessage",
            body=payload.encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        response = connection.getresponse()
        if response.status != 200:
            help_text = HTTP_HELP.get(response.status, "Проверьте доступность Telegram API.")
            raise NotificationError(f"Telegram вернул HTTP {response.status}. {help_text}")
        try:
            result = json.loads(response.read(65536))
        except (UnicodeError, ValueError):
            raise NotificationError("Telegram вернул некорректный JSON.") from None
        if not isinstance(result, dict) or result.get("ok") is not True:
            raise NotificationError("Telegram API не подтвердил отправку (ok != true).")
    except (OSError, http.client.HTTPException):
        raise NotificationError("Ошибка соединения с Telegram API или истекло время ожидания.") from None
    finally:
        connection.close()


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]+", token):
        raise NotificationError("TELEGRAM_BOT_TOKEN отсутствует или имеет неверный формат.")
    if not re.fullmatch(r"-?[1-9][0-9]{0,18}", chat):
        raise NotificationError("TELEGRAM_CHAT_ID должен содержать числовой идентификатор.")

    game_url = os.getenv("UNITY_GAME_URL", "").strip()
    if game_url:
        try:
            parsed = urlsplit(game_url)
        except ValueError:
            raise NotificationError("Некорректный UNITY_GAME_URL.") from None
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise NotificationError("UNITY_GAME_URL должен быть публичным HTTPS-адресом игры.")

    try:
        needs = json.loads(os.environ["NEEDS_JSON"])
        author = os.getenv("COMMIT_AUTHOR") or os.environ["GITHUB_ACTOR"]
        run_url = (
            f'{os.environ["GITHUB_SERVER_URL"]}/{os.environ["GITHUB_REPOSITORY"]}'
            f'/actions/runs/{os.environ["GITHUB_RUN_ID"]}'
        )
        message = format_message(
            needs, author, os.environ["GITHUB_SHA"], run_url, game_url,
            check=os.getenv("TELEGRAM_CHECK") == "1",
        )
    except (KeyError, AttributeError, TypeError, ValueError):
        raise NotificationError("Контекст GitHub Actions неполон или некорректен.") from None

    send_message(http.client.HTTPSConnection("api.telegram.org", timeout=15), token, int(chat), message)
    print("Telegram API подтвердил отправку.")


if __name__ == "__main__":
    try:
        main()
    except NotificationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
