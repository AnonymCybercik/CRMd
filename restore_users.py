#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Role

def restore_all_users():
    """Восстановление всех пользователей системы"""
    app = create_app()
    
    with app.app_context():
        print("Восстановление пользователей...")
        
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
                'first_name': 'Александр',
                'last_name': 'Петров',
                'password': 'director123',
                'roles': ['director']
            },
            {
                'username': 'manager',
                'email': 'manager@teploresurscrm.uz',
                'first_name': 'Мария',
                'last_name': 'Иванова',
                'password': 'manager123',
                'roles': ['manager']
            },
            {
                'username': 'supplier',
                'email': 'supplier@teploresurscrm.uz',
                'first_name': 'Дмитрий',
                'last_name': 'Сидоров',
                'password': 'supplier123',
                'roles': ['supplier']
            },
            {
                'username': 'warehouse',
                'email': 'warehouse@teploresurscrm.uz',
                'first_name': 'Елена',
                'last_name': 'Козлова',
                'password': 'warehouse123',
                'roles': ['warehouse']
            },
            {
                'username': 'production',
                'email': 'production@teploresurscrm.uz',
                'first_name': 'Сергей',
                'last_name': 'Морозов',
                'password': 'production123',
                'roles': ['production']
            },
            {
                'username': 'accountant',
                'email': 'accountant@teploresurscrm.uz',
                'first_name': 'Анна',
                'last_name': 'Волкова',
                'password': 'accountant123',
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
        print("\nВсе пользователи восстановлены!")
        print("\nДоступные аккаунты:")
        print("Директор: director / director123")
        print("Менеджер: manager / manager123")
        print("Поставщик: supplier / supplier123")
        print("Склад: warehouse / warehouse123")
        print("Производство: production / production123")
        print("Бухгалтер: accountant / accountant123")

if __name__ == '__main__':
    restore_all_users()
