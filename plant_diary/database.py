#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
植物日記 - 數據庫模組
負責數據庫的創建、連接和基本操作
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from pathlib import Path


class PlantDatabase:
    """植物數據庫管理類"""
    
    def __init__(self, db_path="plant_diary.db"):
        """初始化數據庫連接"""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def get_connection(self):
        """獲取數據庫連接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # 使用 Row 工廠以便按列名訪問
        return self.conn
    
    def init_database(self):
        """初始化數據庫表結構"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 創建植物表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chinese_name TEXT NOT NULL,
                scientific_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                notes TEXT
            )
        ''')
        
        # 創建照片記錄表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL,
                photo_path TEXT NOT NULL,
                taken_at TEXT NOT NULL,
                notes TEXT,
                ai_analysis TEXT,
                care_suggestions TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants (id) ON DELETE CASCADE
            )
        ''')
        
        # 創建用戶表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        
        # 初始化管理員帳號（如果不存在）
        self._init_admin_user()
    
    def add_plant(self, chinese_name, scientific_name="", notes=""):
        """添加新植物"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO plants (chinese_name, scientific_name, created_at, updated_at, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (chinese_name, scientific_name, now, now, notes))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_plant(self, plant_id, chinese_name=None, scientific_name=None, notes=None):
        """更新植物信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        updates = []
        values = []
        
        if chinese_name is not None:
            updates.append("chinese_name = ?")
            values.append(chinese_name)
        if scientific_name is not None:
            updates.append("scientific_name = ?")
            values.append(scientific_name)
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)
        
        updates.append("updated_at = ?")
        values.append(now)
        values.append(plant_id)
        
        cursor.execute(f'''
            UPDATE plants 
            SET {', '.join(updates)}
            WHERE id = ?
        ''', values)
        
        conn.commit()
    
    def delete_plant(self, plant_id):
        """刪除植物及其所有照片記錄"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先刪除相關照片
        cursor.execute('DELETE FROM photos WHERE plant_id = ?', (plant_id,))
        # 刪除植物
        cursor.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
        
        conn.commit()
    
    def get_all_plants(self):
        """獲取所有植物列表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plants ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_plant(self, plant_id):
        """獲取單個植物信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plants WHERE id = ?', (plant_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_photo(self, plant_id, photo_path, notes="", ai_analysis="", care_suggestions=""):
        """添加照片記錄"""
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO photos (plant_id, photo_path, taken_at, notes, ai_analysis, care_suggestions)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (plant_id, photo_path, now, notes, ai_analysis, care_suggestions))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_plant_photos(self, plant_id):
        """獲取植物的所有照片記錄"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM photos 
            WHERE plant_id = ? 
            ORDER BY taken_at DESC
        ''', (plant_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_photo_analysis(self, photo_id, ai_analysis, care_suggestions):
        """更新照片的AI分析結果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE photos 
            SET ai_analysis = ?, care_suggestions = ?
            WHERE id = ?
        ''', (ai_analysis, care_suggestions, photo_id))
        
        conn.commit()
    
    def get_photo(self, photo_id):
        """獲取單張照片信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM photos WHERE id = ?', (photo_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def delete_photo(self, photo_id):
        """刪除照片記錄"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM photos WHERE id = ?', (photo_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def _hash_password(self, password):
        """對密碼進行哈希處理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _init_admin_user(self):
        """初始化管理員用戶"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 檢查管理員是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', ('FairyGarden',))
        if cursor.fetchone():
            return
        
        # 創建管理員帳號
        admin_password_hash = self._hash_password('kaoming123')
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO users (username, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?)
        ''', ('FairyGarden', admin_password_hash, 1, now))
        conn.commit()
    
    def create_user(self, username, password):
        """創建新用戶"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 檢查用戶名是否已存在
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return None, "用戶名已存在"
        
        password_hash = self._hash_password(password)
        now = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, is_admin, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, 0, now))
            conn.commit()
            return cursor.lastrowid, None
        except sqlite3.IntegrityError:
            return None, "用戶名已存在"
    
    def verify_user(self, username, password):
        """驗證用戶登入"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self._hash_password(password)
        
        cursor.execute('''
            SELECT id, username, is_admin FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'is_admin': bool(row[2])
            }
        return None
    
    def get_user(self, user_id):
        """獲取用戶信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'is_admin': bool(row[2])
            }
        return None
    
    def close(self):
        """關閉數據庫連接"""
        if self.conn:
            self.conn.close()
            self.conn = None


# 全局數據庫實例
_db_instance = None


def get_db():
    """獲取全局數據庫實例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = PlantDatabase()
    return _db_instance

