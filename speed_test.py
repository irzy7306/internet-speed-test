"""Измерение скорости скачивания по десяти последовательным HTTP-запросам."""

import argparse
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT_SECONDS = 30


def download(url: str) -> tuple[int, float]:
    """Скачать ответ целиком и вернуть его размер в байтах и время в секундах."""
    request = Request(
        url,
        headers={"User-Agent": "internet-speed-test/1.0", "Accept-Encoding": "identity"},
    )
    start = time.perf_counter()
    total_bytes = 0

    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        while chunk := response.read(CHUNK_SIZE):
            total_bytes += len(chunk)

    elapsed = time.perf_counter() - start
    return total_bytes, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Скачать файл по URL 10 раз последовательно и измерить скорость.",
        usage="%(prog)s [-h] URL",
    )
    parser.add_argument("url", metavar="URL", help="Ссылка на файл (http:// или https://)")
    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        parser.error("ссылка должна начинаться с http:// или https://")

    total_bytes = 0
    total_seconds = 0.0

    for number in range(1, REQUEST_COUNT + 1):
        try:
            size, seconds = download(args.url)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            print(f"Запрос {number}/{REQUEST_COUNT} завершился ошибкой: {error}", file=sys.stderr)
            return 1

        total_bytes += size
        total_seconds += seconds
        print(f"Запрос {number}/{REQUEST_COUNT}: {size} байт за {seconds:.3f} с")

    average_seconds = total_seconds / REQUEST_COUNT
    speed_mbps = (total_bytes * 8) / total_seconds / 1_000_000 if total_seconds else 0.0

    print(f"\nСреднее время запроса: {average_seconds:.3f} с")
    print(f"Всего скачано: {total_bytes} байт ({total_bytes / 1_000_000:.2f} МБ)")
    print(f"Средняя скорость скачивания: {speed_mbps:.2f} Мбит/с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
