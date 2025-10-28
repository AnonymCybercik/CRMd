#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models import db, User, Order, Product, ProductionTask, FinancialTransaction, InventoryItem, SupplierOrder, Notification, Company, Resource, ResourceRequest, CustomOrder, OrderItem, SalaryPayment, PaymentMethod, Client, Contract, ExpenseCategory, Budget, InventoryTransaction, QualityControl, MaintenanceRecord, Report

def clear_database():
    """Очистка базы данных от тестовых данных"""
    app = create_app()
    
    with app.app_context():
        print("Очистка базы данных...")
        
        # Удаляем все тестовые данные, кроме ролей и директора
        try:
            # Удаляем все заказы и связанные данные
            db.session.query(Order).delete()
            db.session.query(CustomOrder).delete()
            db.session.query(OrderItem).delete()
            db.session.query(ProductionTask).delete()
            db.session.query(FinancialTransaction).delete()
            db.session.query(InventoryItem).delete()
            db.session.query(SupplierOrder).delete()
            db.session.query(Notification).delete()
            db.session.query(Resource).delete()
            db.session.query(ResourceRequest).delete()
            db.session.query(SalaryPayment).delete()
            db.session.query(PaymentMethod).delete()
            db.session.query(Client).delete()
            db.session.query(Contract).delete()
            db.session.query(ExpenseCategory).delete()
            db.session.query(Budget).delete()
            db.session.query(InventoryTransaction).delete()
            db.session.query(QualityControl).delete()
            db.session.query(MaintenanceRecord).delete()
            db.session.query(Report).delete()
            
            # Удаляем всех пользователей кроме директора
            users_to_delete = User.query.filter(User.username != 'director').all()
            for user in users_to_delete:
                db.session.delete(user)
            
            # Удаляем компании
            db.session.query(Company).delete()
            
            db.session.commit()
            print("База данных успешно очищена!")
            print("Оставлен только директор с логином: director, пароль: director123")
            
        except Exception as e:
            print(f"Ошибка при очистке базы данных: {e}")
            db.session.rollback()

if __name__ == '__main__':
    clear_database()
