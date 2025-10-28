#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, Role

def init_database():
    """Инициализация базы данных"""
    app = create_app()
    
    with app.app_context():
        print("Создание таблиц базы данных...")
        db.create_all()
        
        print("Создание ролей...")
        roles = ['director', 'manager', 'supplier', 'warehouse', 'production', 'accountant']
        
        for role_name in roles:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                role = Role(name=role_name)
                db.session.add(role)
                print(f"Создана роль: {role_name}")
            else:
                print(f"Роль {role_name} уже существует")
        
        db.session.commit()
        print("База данных успешно инициализирована!")

if __name__ == '__main__':
    init_database()