# main.py
import re
from urllib.parse import urljoin
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin
from pathlib import Path
from constants import BASE_DIR, MAIN_DOC_URL
from configs import configure_argument_parser #конфигурация парсера
from outputs import control_output #вывод данных
import logging
# Дополните импорт из файла configs функцией configure_logging().
from configs import configure_argument_parser, configure_logging
from utils import get_response
from utils import find_tag


def whats_new(session):
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    # Загрузка веб-страницы с кешированием.
    #*#session = requests_cache.CachedSession()
    response = get_response(session, whats_new_url) # команда загрузки
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id. Парсеру нужен только 
    # первый элемент, поэтому используется метод find().
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    # Шаг 2-й: поиск внутри main_div следующего тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'}) # здесь хранятся все теги, котор хрнятся в теге <li>
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    
    # добавляем прогресс-бар
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)# Загрузите все страницы со статьями. Используйте кеширующую сессию. 
        if response is None:
            # Если страница не загрузится, программа перейдёт к следующей ссылке.
            continue  
        soup = BeautifulSoup(response.text, features='lxml')  # Сварите "супчик".
        h1 = find_tag(soup, 'h1')  # Найдите в "супе" тег h1.
        dl = find_tag(soup, 'dl')  # Найдите в "супе" тег dl.
        #print(version_link, h1.text, dl.text) # Добавьте в вывод на печать текст из тегов h1 и dl.
        dl_text = dl.text.replace('\n', ' ') # заменим пустые строки \n на пробелы ' '
        # На печать теперь выводится переменная dl_text — без пустых строчек.
        #print(version_link, h1.text, dl_text)
        # Добавьте в список ссылки и текст из тегов h1 и dl в виде кортежа
        results.append((version_link, h1.text, dl_text))
        # Печать списка с данными.
    # for row in results:
    #     # Распаковка каждого кортежа при печати при помощи звездочки.
    #     print(*row)
        return results


def latest_versions(session):
    main_doc_url = urljoin(MAIN_DOC_URL, 'latest_version/')
    response = get_response(session, main_doc_url)# команда загрузки 
    if response is None:
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = find_tag(sidebar,'ul')
    # Перебор в цикле всех найденных списков
    for ul in ul_tags:
    # Проверка, есть ли искомый текст в содержимом тега ul
        if 'All versions' in ul.text:
        # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
        # Остановка перебора списков.
            break
    else:
# Если нужный список не нашёлся,
# вызывается исключение и выполнение программы прерывается.    
        raise Exception('Ничего не нашлось')
#print(a_tags)
    results = [('Ссылка на документацию', 'Версия', 'Статус')] # Список для хранения результатов
# Шаблон для поиска версии и статуса:
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
# Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        link = a_tag['href']# Извлечение ссылки
    # Поиск паттерна в ссылке.
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:  
    # Если строка соответствует паттерну,
    # переменным присваивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:  
    # Если строка не соответствует паттерну,
    # первой переменной присваивается весь текст, второй — пустая строка.
            version, status = a_tag.text, ''  
    # Добавление полученных переменных в список в виде кортежа.
        results.append((link, version, status))

    # # Печать результата.
    # for row in results:
    #     print(*row) 
    return results


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)# команда загрузки 
    if response is None:
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')

    #main_tag = find_tag(soup, 'div', attrs= {'role': 'main'})
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    # Добавьте команду получения нужного тега(найди строку, 
    # которая соответствует регулярному выражению)
    pdf_a4_tag = find_tag(table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    # Сохраните в переменную содержимое атрибута href.
    pdf_a4_link = pdf_a4_tag['href']
    # Получите полную ссылку с помощью функции urljoin.
    archive_url = urljoin(downloads_url, pdf_a4_link)
    #print(archive_url)
    
    #Для того чтобы сохранить файл на диск, 
    # нужно указать программе, с каким именем и куда его сохранять
    #Придумывать новое имя файлу необязательно. 
    # Можно использовать то, которое указано на сайте. 
    # Для ссылки https://docs.python.org/3/archives/python-3.9.7-docs-pdf-a4.zip 
    # это делается так: текст ссылки разбивается на 
    # список по слешам при помощи метода split('/') и берётся последний элемент [-1]. 
    filename = archive_url.split('/')[-1]
    print(filename)

    #указать программе место, куда этот файл сохранять:
    #сначала указать,где на диске хранится сам проект(см.константу выше)

    #Затем сформулируйте путь до новой директории; 
    # к пути до директории с проектом через слеш добавьте путь до новой директории: 
    #И, наконец, создайте директорию
    # Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename
    # Загрузка архива по ссылке.
    response = session.get(archive_url)

    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
    # Полученный ответ записывается в файл.
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}

def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')

    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')
    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря(передаётся и сессия).
    results = MODE_TO_FUNCTION[parser_mode](session)
    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')

if __name__ == '__main__':
    main() 
