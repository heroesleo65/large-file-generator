import os
import random
import string

import click
import humanfriendly

string_random_choice = string.ascii_letters + string.digits + ' '


@click.command()
@click.option('--size', '-s', default='10MB', metavar='<size>',
              help='Размер генерируемого файла. Указывается в байтах, KB, MB, GB, TB')
@click.option('--lines', '-l', default=42, metavar='<lines>', help='Кол-во строк в генерируемом файле')
@click.option('--output', '-o', required=True, metavar='<output>', help='Файл для вывода')
def cli(size: int, lines: int, output: str):
    """
    Генерируем случайный текст размером <size> с кол-вом строк <lines> в стандартный поток.

    Пример использования: large-file-generator -s 10MB -l 42 -o example.txt
    """

    size = humanfriendly.parse_size(size=size, binary=True)
    if size < 0:
        size = 0
    if lines <= 0:
        lines = 1
    string_size = size // lines
    if string_size < len(os.linesep):
        raise click.BadOptionUsage(
            option_name='size',
            message='Указан слишком маленький размер файла. Нельзя сгенерировать данные с указанными условиями',
        )
    if string_size > 1024 * 1024 * 1024:
        raise click.BadOptionUsage(
            option_name='lines',
            message='Указано слишком малое количество строк. Нельзя сгенерировать данные с указанными условиями',
        )
    string_size = string_size - len(os.linesep)

    generation_text(max_size=size, lines=lines, string_size=string_size, output=output)


def generation_text(max_size: int, lines: int, string_size: int, output: str):
    def write_data(f, data, progressbar):
        f.write(data)
        progressbar.update(len(data))

    with open(output, 'wt') as file:
        size = max_size
        balance = max_size % lines
        with click.progressbar(
                length=max_size, label='Generation file', show_percent=True, show_pos=True
        ) as generation_progress:
            for number in range(lines - 1):
                min_size_for_line = min(balance, size)
                max_size_for_line = min(balance + string_size, size)
                line = generation_line(min_size=min_size_for_line, max_size=max_size_for_line)
                balance = balance + (string_size - len(line))
                line = line + os.linesep
                size = size - len(line)
                write_data(file, line, generation_progress)

            line = generation_line(min_size=size, max_size=size)
            write_data(file, line, generation_progress)


def generation_line(min_size: int = 1, max_size: int = 1):
    if max_size <= 0:
        return ''

    if max_size < min_size:
        raise ValueError('max_size must be greater than or equal to min_size')

    if min_size < 1:
        min_size = 1

    count = random.randint(min_size, max_size)
    return ''.join(random.choices(string_random_choice, k=count))
