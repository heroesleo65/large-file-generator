import os
import random
import string
import sys

import click
import humanfriendly


DEFAULT_ENCODING = 'utf-8'


def get_size_in_bytes(line: str, encoding=DEFAULT_ENCODING):
    return len(line.encode(encoding))


@click.command()
@click.option('--size', '-s', default='10MB', metavar='<size>',
              help='Размер генерируемого файла. Указывается в байтах, KB, MB, GB, TB')
@click.option('--lines', '-l', default=42, metavar='<lines>', help='Кол-во строк в генерируемом файле')
@click.option('--output', '-o', required=True, metavar='<output>', help='Файл для вывода')
@click.option(
    '--string_choice',
    default=string.ascii_letters + string.digits + ' ',
    metavar='<string_choice>',
    help='Набор символов для генерации'
)
def cli(size: int, lines: int, output: str, string_choice: str):
    """
    Генерируем случайный текст размером <size> с кол-вом строк <lines> в выходной файл <output>.

    Пример использования: large-file-generator -s 10MB -l 42 -o example.txt
    """

    size = humanfriendly.parse_size(size=size, binary=True)
    if size < 0:
        size = 0
    if lines <= 0:
        lines = 1
    string_size = size // lines
    if string_size <= get_size_in_bytes(os.linesep):
        raise click.BadOptionUsage(
            option_name='size',
            message='Указан слишком маленький размер файла. Нельзя сгенерировать данные с указанными условиями',
        )
    if string_size > 1024 * 1024 * 1024:
        raise click.BadOptionUsage(
            option_name='lines',
            message='Указано слишком малое количество строк. Нельзя сгенерировать данные с указанными условиями',
        )
    string_size = string_size - get_size_in_bytes(os.linesep)

    generation_text(max_size=size, lines=lines, string_size=string_size, output=output, string_choice=string_choice)


def generation_text(max_size: int, lines: int, string_size: int, output: str, string_choice: str):
    def write_data(f, data, progressbar):
        f.write(data)
        progressbar.update(get_size_in_bytes(data))

    if not string_choice:
        raise ValueError('string_choice must contains any symbol')

    string_choices = {}
    for c in string_choice:
        size = get_size_in_bytes(c)
        if size in string_choices:
            string_choices[size].append(c)
        else:
            string_choices[size] = [c]

    with open(output, mode='wt', encoding=DEFAULT_ENCODING) as file:
        size = max_size
        with click.progressbar(
                length=max_size, label='Generation file', show_percent=True, show_pos=True
        ) as generation_progress:
            for number in range(lines - 1):
                min_size_for_line = min(string_size * 3 // 4, size)
                max_size_for_line = min(string_size, size)
                line = generation_line(
                    min_size=min_size_for_line, max_size=max_size_for_line, string_choices=string_choices
                ) + os.linesep
                size = size - get_size_in_bytes(line)
                string_size = size // (lines - number - 1)
                write_data(file, line, generation_progress)

            line = generation_line(min_size=size, max_size=size, string_choices=string_choices)
            write_data(file, line, generation_progress)


def generation_line(string_choices: dict, min_size: int = 1, max_size: int = 1):
    if max_size <= 0:
        return ''

    if max_size < min_size:
        raise ValueError('max_size must be greater than or equal to min_size')

    if not string_choices:
        raise ValueError('string_choices must contains any symbol')

    if min_size < 1:
        min_size = 1

    sum_of_size = sum(string_choices.keys())
    count = random.randint(min_size, max_size)
    count_per_size = count // sum_of_size

    result = []
    for choices in string_choices.values():
        result.extend(random.choices(choices, k=count_per_size))

    # Add remain symbols
    remain = count % sum_of_size
    if remain in string_choices:
        result.extend(random.choices(string_choices[remain], k=1))
    else:
        max_size = 0
        for size, choices in string_choices.items():
            if size > 0 and remain % size == 0:
                result.extend(random.choices(choices, k=remain // size))
                return ''.join(result)
            elif max_size < size < remain:
                max_size = size

        if max_size in string_choices:
            result.extend(random.choices(string_choices[max_size], k=remain // max_size))

    return ''.join(result)


if __name__ == '__main__':
    cli(sys.argv[1:])
