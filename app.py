from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

# ============================================
# Flask Todo App
# Day 36 — 120 Days of Code | NIT Rourkela
# ============================================

app = Flask(__name__)
DB = "todos.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/todos', methods=['GET'])
def get_todos():
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')

    query = 'SELECT * FROM todos WHERE 1=1'
    params = []

    if status == 'active':
        query += ' AND completed = 0'
    elif status == 'completed':
        query += ' AND completed = 1'

    if priority != 'all':
        query += ' AND priority = ?'
        params.append(priority)

    query += ' ORDER BY completed ASC, CASE priority WHEN "high" THEN 1 WHEN "medium" THEN 2 WHEN "low" THEN 3 END, created_at DESC'

    with get_db() as conn:
        todos = conn.execute(query, params).fetchall()
        return jsonify([dict(t) for t in todos])

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    with get_db() as conn:
        cursor = conn.execute(
            'INSERT INTO todos (title, description, priority, due_date) VALUES (?, ?, ?, ?)',
            (title, data.get('description', ''), data.get('priority', 'medium'), data.get('due_date', ''))
        )
        conn.commit()
        todo = conn.execute('SELECT * FROM todos WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(dict(todo)), 201

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    with get_db() as conn:
        if 'completed' in data:
            conn.execute('UPDATE todos SET completed = ? WHERE id = ?',
                        (1 if data['completed'] else 0, todo_id))
        if 'title' in data:
            conn.execute('UPDATE todos SET title = ? WHERE id = ?',
                        (data['title'], todo_id))
        conn.commit()
        todo = conn.execute('SELECT * FROM todos WHERE id = ?', (todo_id,)).fetchone()
        if not todo:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(dict(todo))

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    with get_db() as conn:
        conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    with get_db() as conn:
        total = conn.execute('SELECT COUNT(*) FROM todos').fetchone()[0]
        completed = conn.execute('SELECT COUNT(*) FROM todos WHERE completed=1').fetchone()[0]
        high = conn.execute('SELECT COUNT(*) FROM todos WHERE priority="high" AND completed=0').fetchone()[0]
        return jsonify({'total': total, 'completed': completed, 'active': total - completed, 'high_priority': high})

if __name__ == '__main__':
    init_db()
    print("\n🚀 Flask Todo App running!")
    print("   Open http://localhost:5000 in your browser\n")
    app.run(debug=True)