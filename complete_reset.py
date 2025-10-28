#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Role
from werkzeug.security import generate_password_hash

def complete_reset():
    """Полный сброс базы данных с правильным хешированием"""
    app = create_app()
    
    with app.app_context():
        print("Полный сброс базы данных...")
        
        try:
            # Удаляем все таблицы
            print("Удаление всех таблиц...")
            db.drop_all()
            
            # Создаем таблицы заново
            print("Создание таблиц...")
            db.create_all()
            
            # Создаем роли
            print("Создание ролей...")
            roles = ['director', 'manager', 'supplier', 'warehouse', 'production', 'accountant']
            for role_name in roles:
                role = Role(name=role_name)
                db.session.add(role)
            
            # Создаем директора с правильным хешированием
            print("Создание директора...")
            director_role = Role.query.filter_by(name='director').first()
            
            director = User(
                username='director',
                email='director@teploresurscrm.uz',
                first_name='Директор',
                last_name='Компании'
            )
            # Используем прямое хеширование для совместимости
            director.password_hash = generate_password_hash('director123', method='pbkdf2:sha256')
            director.roles.append(director_role)
            
            db.session.add(director)
            db.session.commit()
            
            print("База данных полностью сброшена!")
            print("Создан директор: director / director123")
            print("Хеширование: pbkdf2:sha256 (совместимо)")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            db.session.rollback()

if __name__ == '__main__':
    complete_reset()



