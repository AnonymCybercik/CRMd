#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Role

def create_director():
    """Создание директора"""
    app = create_app()
    
    with app.app_context():
        # Проверяем, существует ли уже директор
        existing_director = User.query.filter_by(username='director').first()
        if existing_director:
            print("Директор уже существует!")
            return
        
        # Получаем роль директора
        director_role = Role.query.filter_by(name='director').first()
        if not director_role:
            print("Ошибка: Роль 'director' не найдена. Сначала запустите init_db.py")
            return
        
        # Создаем директора
        director = User(
            username='director',
            email='director@teploresurscrm.uz',
            first_name='Директор',
            last_name='Компании'
        )
        director.set_password('director123')
        director.roles.append(director_role)
        
        db.session.add(director)
        db.session.commit()
        
        print("Директор успешно создан!")
        print("Логин: director")
        print("Пароль: director123")

if __name__ == '__main__':
    create_director()