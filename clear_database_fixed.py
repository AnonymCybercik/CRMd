#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Order, Product, ProductionTask, FinancialTransaction, InventoryItem, SupplierOrder, Notification, Company, Resource, ResourceRequest, CustomOrder, OrderItem, SalaryPayment, PaymentMethod, Client, Contract, ExpenseCategory, Budget, InventoryTransaction, QualityControl, MaintenanceRecord, Report

def clear_database():
    """Очистка базы данных от тестовых данных"""
    app = create_app()
    
    with app.app_context():
        print("Очистка базы данных...")
        
        try:
            # Удаляем все связанные данные
            print("Удаление заказов...")
            db.session.query(Order).delete()
            db.session.query(CustomOrder).delete()
            db.session.query(OrderItem).delete()
            
            print("Удаление производственных задач...")
            db.session.query(ProductionTask).delete()
            
            print("Удаление финансовых транзакций...")
            db.session.query(FinancialTransaction).delete()
            
            print("Удаление складских данных...")
            db.session.query(InventoryItem).delete()
            db.session.query(InventoryTransaction).delete()
            
            print("Удаление заказов поставщиков...")
            db.session.query(SupplierOrder).delete()
            
            print("Удаление уведомлений...")
            db.session.query(Notification).delete()
            
            print("Удаление ресурсов...")
            db.session.query(Resource).delete()
            db.session.query(ResourceRequest).delete()
            
            print("Удаление платежей...")
            db.session.query(SalaryPayment).delete()
            db.session.query(PaymentMethod).delete()
            
            print("Удаление клиентов и контрактов...")
            db.session.query(Client).delete()
            db.session.query(Contract).delete()
            
            print("Удаление бюджетов...")
            db.session.query(ExpenseCategory).delete()
            db.session.query(Budget).delete()
            
            print("Удаление контроля качества...")
            db.session.query(QualityControl).delete()
            db.session.query(MaintenanceRecord).delete()
            
            print("Удаление отчетов...")
            db.session.query(Report).delete()
            
            print("Удаление компаний...")
            db.session.query(Company).delete()
            
            print("Удаление продуктов...")
            db.session.query(Product).delete()
            
            # Удаляем всех пользователей кроме директора
            print("Удаление пользователей (кроме директора)...")
            users_to_delete = User.query.filter(User.username != 'director').all()
            for user in users_to_delete:
                # Сначала удаляем связи с ролями
                user.roles.clear()
                db.session.delete(user)
            
            db.session.commit()
            print("База данных успешно очищена!")
            print("Оставлен только директор с логином: director, пароль: director123")
            
        except Exception as e:
            print(f"Ошибка при очистке базы данных: {e}")
            db.session.rollback()

if __name__ == '__main__':
    clear_database()



