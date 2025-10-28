#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для полной настройки CRM системы Тепло Ресурс
Включает создание базы данных, пользователей и примеров данных
"""

from app import create_app
from models import db, User, Role, Company, Resource, Product, ResourceRequest
from load_excel_data import create_sample_data

def setup_complete_system():
    """Полная настройка системы"""
    app = create_app()
    
    with app.app_context():
        print("=== НАСТРОЙКА CRM СИСТЕМЫ ТЕПЛО РЕСУРС ===\n")
        
        try:
            # 1. Создаем таблицы
            print("1. Создание таблиц базы данных...")
            db.create_all()
            print("+ Таблицы созданы\n")
            
            # 2. Создаем роли
            print("2. Создание ролей...")
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
                    role = Role(name=role_info['name'], description=role_info['description'])
                    db.session.add(role)
                    print(f"+ Создана роль: {role_info['name']}")
                else:
                    print(f"+ Роль {role_info['name']} уже существует")
            
            db.session.commit()
            print("+ Роли созданы\n")
            
            # 3. Создаем пользователей
            print("3. Создание пользователей...")
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
                    print(f"+ Создан пользователь: {user_info['username']} ({user_info['first_name']} {user_info['last_name']})")
                else:
                    print(f"+ Пользователь {user_info['username']} уже существует")
            
            db.session.commit()
            print("+ Пользователи созданы\n")
            
            # 4. Создаем примеры данных
            print("4. Создание примеров данных...")
            create_sample_data()
            print("+ Примеры данных созданы\n")
            
            # 5. Создаем несколько запросов на ресурсы для демонстрации
            print("5. Создание запросов на ресурсы...")
            requests_data = [
                {
                    'resource_name': 'Труба стальная 50мм',
                    'quantity': 100,
                    'priority': 'high',
                    'status': 'pending',
                    'requested_by': 'a3'
                },
                {
                    'resource_name': 'Котел газовый 30кВт',
                    'quantity': 5,
                    'priority': 'urgent',
                    'status': 'approved',
                    'requested_by': 'a4'
                },
                {
                    'resource_name': 'Труба медная 25мм',
                    'quantity': 50,
                    'priority': 'medium',
                    'status': 'delivered',
                    'requested_by': 'a3'
                }
            ]
            
            for request_data in requests_data:
                existing_request = ResourceRequest.query.filter_by(
                    resource_name=request_data['resource_name'],
                    requested_by=request_data['requested_by']
                ).first()
                
                if not existing_request:
                    request_obj = ResourceRequest(**request_data)
                    db.session.add(request_obj)
                    print(f"+ Создан запрос: {request_data['resource_name']} от {request_data['requested_by']}")
                else:
                    print(f"+ Запрос {request_data['resource_name']} уже существует")
            
            db.session.commit()
            print("+ Запросы созданы\n")
            
            print("=== НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО! ===\n")
            print("Доступные аккаунты:")
            print("+----------------+----------+---------+")
            print("| Роль           | Логин    | Пароль  |")
            print("+----------------+----------+---------+")
            print("| Директор       | director | 1234    |")
            print("| Менеджер       | a1       | 123     |")
            print("| Поставщик      | a2       | 123     |")
            print("| Склад          | a3       | 123     |")
            print("| Производство   | a4       | 123     |")
            print("| Бухгалтер      | a5       | 123     |")
            print("+----------------+----------+---------+")
            print("\nДля запуска системы выполните: python app.py")
            
        except Exception as e:
            print(f"ERROR: Ошибка при настройке системы: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    setup_complete_system()
