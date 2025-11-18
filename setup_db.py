from flask import Flask
from app import mysql
import MySQLdb.cursors

def get_cursor():
    return mysql.connection.cursor()

def commit():
    mysql.connection.commit()

def setup_database():
    cursor = get_cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS todo_users(
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   username VARCHAR(100) NOT NULL UNIQUE,
                   password VARCHAR(255) NOT NULL,
                   profilepic VARCHAR(255) DEFAULT 'default_profile.png',
                   darkmode VARCHAR(10) DEFAULT 'disabled')
""")
    
    cursor.execute("""
CREATE TABLE IF NOT EXISTS todo_tasks(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    task_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at VARCHAR(50) DEFAULT 'still_pending',
                    status VARCHAR(20) DEFAULT 'pending',
                    FOREIGN KEY (user_id) REFERENCES todo_users(id) ON DELETE CASCADE)
""")
    
    cursor.execute("""                                                                                                                                    
CREATE TABLE IF NOT EXISTS todo_feedback(
                   feedback MEDIUMTEXT NOT NULL)
""")
    
    cursor.execute("""
CREATE TABLE IF NOT EXISTS todo_history(
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   user_id INT NOT NULL,
                   task_text TEXT NOT NULL,
                   status VARCHAR(20) DEFAULT 'pending',
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (user_id) REFERENCES todo_users(id) ON DELETE CASCADE)
""")
    
    cursor.execute("""
CREATE TABLE IF NOT EXISTS todo_trash(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    task_text TEXT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    completed_at VARCHAR(100) DEFAULT 'still_pending',
                    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES todo_users(id) ON DELETE CASCADE)
                    
""")
    commit()
    cursor.close()


