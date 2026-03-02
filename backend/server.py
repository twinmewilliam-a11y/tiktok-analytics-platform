import os
import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
CORS(app)

# 数据库配置 - Render自动提供DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """获取数据库连接"""
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require' if 'render.com' in DATABASE_URL else None)
    else:
        # 本地开发使用SQLite
        import sqlite3
        conn = sqlite3.connect('../data/local.db')
        conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 创建账号表
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            followers INTEGER DEFAULT 0,
            hearts INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0,
            account_type VARCHAR(20) DEFAULT '未知',
            industry VARCHAR(50) DEFAULT '',
            style VARCHAR(50) DEFAULT '',
            source VARCHAR(50) DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("数据库初始化完成")

@app.route('/')
def index():
    return render_template('index.html')

# 获取所有账号
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        SELECT id, username, followers, hearts, videos, 
               account_type, industry, style, source, created_at
        FROM accounts 
        ORDER BY followers DESC
    ''')
    
    rows = cur.fetchall()
    accounts = []
    for row in rows:
        accounts.append({
            'id': row[0],
            'username': row[1],
            'followers': row[2],
            'hearts': row[3],
            'videos': row[4],
            'account_type': row[5],
            'industry': row[6],
            'style': row[7],
            'source': row[8],
            'created_at': row[9].isoformat() if row[9] else None
        })
    
    cur.close()
    conn.close()
    
    return jsonify(accounts)

# 批量添加账号
@app.route('/api/accounts/batch', methods=['POST'])
def add_accounts_batch():
    data_list = request.json
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    inserted = 0
    for data in data_list:
        try:
            cur.execute('''
                INSERT INTO accounts (username, followers, hearts, videos, 
                                    account_type, industry, style, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            ''', (
                data.get('username'),
                int(data.get('followers', 0)),
                int(data.get('hearts', 0)),
                int(data.get('videos', 0)),
                data.get('account_type', '未知'),
                data.get('industry', ''),
                data.get('style', ''),
                data.get('source', '手动导入')
            ))
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"插入失败 {data.get('username')}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'count': inserted})

# 获取统计信息
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 总数
    cur.execute('SELECT COUNT(*) FROM accounts')
    total = cur.fetchone()[0]
    
    # 按粉丝数分层
    cur.execute('SELECT COUNT(*) FROM accounts WHERE followers > 10000')
    high = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM accounts WHERE followers BETWEEN 1000 AND 10000')
    medium = cur.fetchone()[0]
    
    cur.execute('SELECT COUNT(*) FROM accounts WHERE followers < 1000')
    low = cur.fetchone()[0]
    
    # 按账号类型统计
    cur.execute("SELECT COUNT(*) FROM accounts WHERE account_type = '官方号'")
    official = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM accounts WHERE account_type = 'KOL'")
    kol = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM accounts WHERE account_type = '未知'")
    unknown = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return jsonify({
        'total_accounts': total,
        'high_performers': high,
        'medium_performers': medium,
        'low_performers': low,
        'official_count': official,
        'kol_count': kol,
        'unknown_count': unknown,
        'progress': f"{total}/1000"
    })

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
