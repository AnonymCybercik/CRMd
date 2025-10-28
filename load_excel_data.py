#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from app import create_app
from models import db, Company, Resource, ResourceRequest, Product, InventoryItem
from datetime import datetime
import os

def load_companies_from_excel(file_path):
    """Загрузка компаний-поставщиков из Excel файла"""
    app = create_app()
    
    with app.app_context():
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path)
            
            print(f"Загружаем компании из файла: {file_path}")
            print(f"Найдено записей: {len(df)}")
            
            for index, row in df.iterrows():
                # Создаем компанию
                company = Company(
                    name=row.get('company_name', f'Компания {index + 1}'),
                    address=row.get('address', ''),
                    phone=row.get('phone', ''),
                    email=row.get('email', '')
                )
                
                # Проверяем, не существует ли уже такая компания
                existing = Company.query.filter_by(name=company.name).first()
                if not existing:
                    db.session.add(company)
                    print(f"Добавлена компания: {company.name}")
                else:
                    print(f"Компания {company.name} уже существует")
            
            db.session.commit()
            print("Компании успешно загружены!")
            
        except Exception as e:
            print(f"Ошибка при загрузке компаний: {e}")
            db.session.rollback()

def load_resources_from_excel(file_path):
    """Загрузка ресурсов из Excel файла"""
    app = create_app()
    
    with app.app_context():
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path)
            
            print(f"Загружаем ресурсы из файла: {file_path}")
            print(f"Найдено записей: {len(df)}")
            
            for index, row in df.iterrows():
                # Находим компанию по имени
                company_name = row.get('company_name', '')
                company = Company.query.filter_by(name=company_name).first()
                
                if not company:
                    # Создаем компанию если её нет
                    company = Company(
                        name=company_name,
                        address=row.get('company_address', ''),
                        phone=row.get('company_phone', ''),
                        email=row.get('company_email', '')
                    )
                    db.session.add(company)
                    db.session.flush()  # Получаем ID
                
                # Создаем ресурс
                resource = Resource(
                    name=row.get('resource_name', f'Ресурс {index + 1}'),
                    resource_type=row.get('resource_type', 'material'),
                    quantity=row.get('quantity', 0),
                    unit=row.get('unit', 'шт'),
                    cost_per_unit=row.get('cost_per_unit', 0.0),
                    company_id=company.id
                )
                
                # Проверяем, не существует ли уже такой ресурс
                existing = Resource.query.filter_by(
                    name=resource.name, 
                    company_id=company.id
                ).first()
                
                if not existing:
                    db.session.add(resource)
                    print(f"Добавлен ресурс: {resource.name} от {company.name}")
                else:
                    print(f"Ресурс {resource.name} от {company.name} уже существует")
            
            db.session.commit()
            print("Ресурсы успешно загружены!")
            
        except Exception as e:
            print(f"Ошибка при загрузке ресурсов: {e}")
            db.session.rollback()

def load_products_from_excel(file_path):
    """Загрузка продуктов из Excel файла"""
    app = create_app()
    
    with app.app_context():
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path)
            
            print(f"Загружаем продукты из файла: {file_path}")
            print(f"Найдено записей: {len(df)}")
            
            for index, row in df.iterrows():
                # Создаем продукт
                product = Product(
                    name=row.get('product_name', f'Продукт {index + 1}'),
                    description=row.get('description', ''),
                    price=row.get('price', 0.0),
                    category=row.get('category', 'general'),
                    stock_quantity=row.get('stock_quantity', 0),
                    min_stock_level=row.get('min_stock_level', 10)
                )
                
                # Проверяем, не существует ли уже такой продукт
                existing = Product.query.filter_by(name=product.name).first()
                if not existing:
                    db.session.add(product)
                    print(f"Добавлен продукт: {product.name}")
                else:
                    print(f"Продукт {product.name} уже существует")
            
            db.session.commit()
            print("Продукты успешно загружены!")
            
        except Exception as e:
            print(f"Ошибка при загрузке продуктов: {e}")
            db.session.rollback()

def create_sample_data():
    """Создание примеров данных для демонстрации"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Создаем примеры данных...")
            
            # Создаем компании-поставщики
            companies_data = [
                {
                    'name': 'ООО "Теплоресурс"',
                    'address': 'г. Ташкент, ул. Тепловая, 15',
                    'phone': '+998 71 123-45-67',
                    'email': 'info@teploresurs.uz'
                },
                {
                    'name': 'ИП "МеталлСервис"',
                    'address': 'г. Ташкент, ул. Металлическая, 25',
                    'phone': '+998 71 234-56-78',
                    'email': 'metal@metallservice.uz'
                },
                {
                    'name': 'ООО "ГазКомплект"',
                    'address': 'г. Ташкент, ул. Газовая, 10',
                    'phone': '+998 71 345-67-89',
                    'email': 'gas@gazkomplekt.uz'
                },
                {
                    'name': 'ИП "ТрубоМастер"',
                    'address': 'г. Ташкент, ул. Трубная, 5',
                    'phone': '+998 71 456-78-90',
                    'email': 'tubes@trubomaster.uz'
                }
            ]
            
            for company_data in companies_data:
                existing = Company.query.filter_by(name=company_data['name']).first()
                if not existing:
                    company = Company(**company_data)
                    db.session.add(company)
                    print(f"Создана компания: {company.name}")
            
            db.session.flush()  # Получаем ID компаний
            
            # Создаем ресурсы
            resources_data = [
                # Теплоресурс
                {'name': 'Труба стальная 50мм', 'resource_type': 'material', 'quantity': 1000, 'unit': 'м', 'cost_per_unit': 15000, 'company_name': 'ООО "Теплоресурс"'},
                {'name': 'Труба стальная 100мм', 'resource_type': 'material', 'quantity': 500, 'unit': 'м', 'cost_per_unit': 25000, 'company_name': 'ООО "Теплоресурс"'},
                {'name': 'Котел газовый 30кВт', 'resource_type': 'equipment', 'quantity': 20, 'unit': 'шт', 'cost_per_unit': 2500000, 'company_name': 'ООО "Теплоресурс"'},
                {'name': 'Котел газовый 50кВт', 'resource_type': 'equipment', 'quantity': 15, 'unit': 'шт', 'cost_per_unit': 3500000, 'company_name': 'ООО "Теплоресурс"'},
                
                # МеталлСервис
                {'name': 'Труба медная 25мм', 'resource_type': 'material', 'quantity': 200, 'unit': 'м', 'cost_per_unit': 45000, 'company_name': 'ИП "МеталлСервис"'},
                {'name': 'Труба медная 32мм', 'resource_type': 'material', 'quantity': 150, 'unit': 'м', 'cost_per_unit': 55000, 'company_name': 'ИП "МеталлСервис"'},
                {'name': 'Фитинг медный 25мм', 'resource_type': 'component', 'quantity': 100, 'unit': 'шт', 'cost_per_unit': 15000, 'company_name': 'ИП "МеталлСервис"'},
                
                # ГазКомплект
                {'name': 'Газовый счетчик G4', 'resource_type': 'equipment', 'quantity': 50, 'unit': 'шт', 'cost_per_unit': 180000, 'company_name': 'ООО "ГазКомплект"'},
                {'name': 'Газовый счетчик G6', 'resource_type': 'equipment', 'quantity': 30, 'unit': 'шт', 'cost_per_unit': 220000, 'company_name': 'ООО "ГазКомплект"'},
                {'name': 'Газовый редуктор', 'resource_type': 'component', 'quantity': 80, 'unit': 'шт', 'cost_per_unit': 45000, 'company_name': 'ООО "ГазКомплект"'},
                
                # ТрубоМастер
                {'name': 'Труба ПНД 32мм', 'resource_type': 'material', 'quantity': 300, 'unit': 'м', 'cost_per_unit': 12000, 'company_name': 'ИП "ТрубоМастер"'},
                {'name': 'Труба ПНД 50мм', 'resource_type': 'material', 'quantity': 200, 'unit': 'м', 'cost_per_unit': 18000, 'company_name': 'ИП "ТрубоМастер"'},
                {'name': 'Муфта ПНД 32мм', 'resource_type': 'component', 'quantity': 150, 'unit': 'шт', 'cost_per_unit': 8000, 'company_name': 'ИП "ТрубоМастер"'},
            ]
            
            for resource_data in resources_data:
                company_name = resource_data.pop('company_name')
                company = Company.query.filter_by(name=company_name).first()
                
                if company:
                    resource_data['company_id'] = company.id
                    existing = Resource.query.filter_by(
                        name=resource_data['name'], 
                        company_id=company.id
                    ).first()
                    
                    if not existing:
                        resource = Resource(**resource_data)
                        db.session.add(resource)
                        print(f"Создан ресурс: {resource.name} от {company.name}")
            
            # Создаем продукты
            products_data = [
                {'name': 'Система отопления 2-комн', 'description': 'Полная система отопления для 2-комнатной квартиры', 'price': 2500000, 'category': 'heating_system', 'stock_quantity': 5, 'min_stock_level': 2},
                {'name': 'Система отопления 3-комн', 'description': 'Полная система отопления для 3-комнатной квартиры', 'price': 3500000, 'category': 'heating_system', 'stock_quantity': 3, 'min_stock_level': 2},
                {'name': 'Газовое подключение', 'description': 'Подключение к газовой сети', 'price': 800000, 'category': 'gas_connection', 'stock_quantity': 10, 'min_stock_level': 5},
                {'name': 'Водоснабжение', 'description': 'Система водоснабжения', 'price': 1200000, 'category': 'water_supply', 'stock_quantity': 8, 'min_stock_level': 3},
            ]
            
            for product_data in products_data:
                existing = Product.query.filter_by(name=product_data['name']).first()
                if not existing:
                    product = Product(**product_data)
                    db.session.add(product)
                    print(f"Создан продукт: {product.name}")
            
            db.session.commit()
            print("\nПримеры данных успешно созданы!")
            
        except Exception as e:
            print(f"Ошибка при создании примеров данных: {e}")
            db.session.rollback()

def main():
    """Главная функция для загрузки данных"""
    print("=== Загрузка данных в CRM Тепло Ресурс ===\n")
    
    # Создаем примеры данных
    create_sample_data()
    
    # Если есть Excel файлы, загружаем их
    excel_files = {
        'companies.xlsx': load_companies_from_excel,
        'resources.xlsx': load_resources_from_excel,
        'products.xlsx': load_products_from_excel
    }
    
    for filename, load_function in excel_files.items():
        if os.path.exists(filename):
            print(f"\nНайден файл: {filename}")
            load_function(filename)
        else:
            print(f"Файл {filename} не найден, пропускаем...")
    
    print("\n=== Загрузка завершена ===")

if __name__ == '__main__':
    main()

