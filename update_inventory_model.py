#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app, db
from models import InventoryItem

def update_inventory_model():
    """Добавляем недостающие поля в InventoryItem"""
    
    with app.app_context():
        try:
            # Добавляем поле min_stock если его нет
            try:
                db.engine.execute("ALTER TABLE inventory_item ADD COLUMN min_stock INTEGER DEFAULT 10")
                print("✅ Добавлено поле min_stock")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️ Поле min_stock уже существует")
                else:
                    print(f"⚠️ Ошибка при добавлении min_stock: {e}")
            
            # Добавляем поле price_per_unit если его нет
            try:
                db.engine.execute("ALTER TABLE inventory_item ADD COLUMN price_per_unit FLOAT DEFAULT 0.0")
                print("✅ Добавлено поле price_per_unit")
            except Exception as e:
                if "duplicate column name" in str(e).lower():
                    print("ℹ️ Поле price_per_unit уже существует")
                else:
                    print(f"⚠️ Ошибка при добавлении price_per_unit: {e}")
            
            # Обновляем существующие записи
            items = InventoryItem.query.all()
            for item in items:
                if item.min_stock is None:
                    item.min_stock = 10
                if item.price_per_unit is None:
                    item.price_per_unit = 0.0
            
            db.session.commit()
            print("✅ База данных обновлена успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении базы данных: {e}")
            db.session.rollback()

if __name__ == "__main__":
    update_inventory_model()



