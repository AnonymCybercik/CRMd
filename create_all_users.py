#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Role

def create_all_users():
    """Создание всех пользователей системы"""
    app = create_app()
    
    with app.app_context():
        print("Создание всех пользователей...")
        
        try:
            # Создаем роли если их нет
            roles_data = [
                {'name': 'director', 'description': 'Директор'},
                {'name': 'manager', 'description': 'Менеджер'},
                {'name': 'supplier', 'description': 'Поставщик'},
                {'name': 'warehouse', 'description': 'Склад'},
                {'name': 'production', 'description': 'Производство'},
                {'name': 'accountant', 'description': 'Бухгалтер'}
            ]
            
            for role_info in roles_data:
                existing_role = Role.query.filter_by(name=role_info['name']).first()
                if not existing_role:
                    role = Role(name=role_info['name'])
                    db.session.add(role)
                    print(f"Создана роль: {role_info['name']}")
            
            # Создаем пользователей
            users_data = [
                {
                    'username': 'director',
                    'email': 'director@teploresurscrm.uz',
                    'first_name': 'Директор',
                    'last_name': 'Компании',
                    'password': '1234',
                    'roles': ['director']
                },
                {
                    'username': 'a1',
                    'email': 'manager@teploresurscrm.uz',
                    'first_name': 'Менеджер',
                    'last_name': 'A1',
                    'password': '123',
                    'roles': ['manager']
                },
                {
                    'username': 'a2',
                    'email': 'supplier@teploresurscrm.uz',
                    'first_name': 'Поставщик',
                    'last_name': 'A2',
                    'password': '123',
                    'roles': ['supplier']
                },
                {
                    'username': 'a3',
                    'email': 'warehouse@teploresurscrm.uz',
                    'first_name': 'Склад',
                    'last_name': 'A3',
                    'password': '123',
                    'roles': ['warehouse']
                },
                {
                    'username': 'a4',
                    'email': 'production@teploresurscrm.uz',
                    'first_name': 'Производство',
                    'last_name': 'A4',
                    'password': '123',
                    'roles': ['production']
                },
                {
                    'username': 'a5',
                    'email': 'accountant@teploresurscrm.uz',
                    'first_name': 'Бухгалтер',
                    'last_name': 'A5',
                    'password': '123',
                    'roles': ['accountant']
                }
            ]
            
            for user_info in users_data:
                existing_user = User.query.filter_by(username=user_info['username']).first()
                if not existing_user:
                    user = User(
                        username=user_info['username'],
                        email=user_info['email'],
                        first_name=user_info['first_name'],
                        last_name=user_info['last_name']
                    )
                    user.set_password(user_info['password'])
                    
                    # Назначаем роли
                    for role_name in user_info['roles']:
                        role = Role.query.filter_by(name=role_name).first()
                        if role:
                            user.roles.append(role)
                    
                    db.session.add(user)
                    print(f"Создан пользователь: {user_info['username']} ({user_info['first_name']} {user_info['last_name']})")
                else:
                    print(f"Пользователь {user_info['username']} уже существует")
            
            db.session.commit()
            print("\nВсе пользователи созданы!")
            print("\nДоступные аккаунты:")
            print("Директор: director / 1234")
            print("Менеджер: a1 / 123")
            print("Поставщик: a2 / 123")
            print("Склад: a3 / 123")
            print("Производство: a4 / 123")
            print("Бухгалтер: a5 / 123")
            
        except Exception as e:
            print(f"Ошибка: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_all_users()



