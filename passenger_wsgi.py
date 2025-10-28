#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем приложение
from app import app

# Создаем WSGI приложение
application = app

if __name__ == "__main__":
    application.run()