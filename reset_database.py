#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Role

def reset_database():
    """Полный сброс базы данных"""
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
            
            # Создаем только директора
            print("Создание директора...")
            director_role = Role.query.filter_by(name='director').first()
            
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
            
            print("База данных сброшена!")
            print("Создан только директор: director / director123")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            db.session.rollback()

if __name__ == '__main__':
    reset_database()



