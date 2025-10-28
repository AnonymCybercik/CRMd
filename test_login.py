#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User

def test_login():
    """Тестирование входа в систему"""
    app = create_app()
    
    with app.app_context():
        print("Тестирование входа в систему...")
        
        # Тестируем директора
        director = User.query.filter_by(username='director').first()
        if director:
            print(f"Директор найден: {director.username}")
            print(f"Проверка пароля '1234': {director.check_password('1234')}")
            print(f"Проверка пароля 'director123': {director.check_password('director123')}")
        else:
            print("Директор не найден!")
        
        # Тестируем менеджера
        manager = User.query.filter_by(username='a1').first()
        if manager:
            print(f"Менеджер найден: {manager.username}")
            print(f"Проверка пароля '123': {manager.check_password('123')}")
        else:
            print("Менеджер не найден!")

if __name__ == '__main__':
    test_login()



