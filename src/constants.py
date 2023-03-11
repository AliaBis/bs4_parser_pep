import requests_cache
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from pathlib import Path


BASE_DIR = Path(__file__).parent # добавь константы, где будет храниться путь до директории с текущим файлом
WHATS_NEW_URL = 'https://docs.python.org/3/whatsnew/'
MAIN_DOC_URL = 'https://docs.python.org/3/'
DOWNLOADS_URL = 'https://docs.python.org/3/download.html'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'