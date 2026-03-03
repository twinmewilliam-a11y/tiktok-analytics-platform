import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend/static')
CORS(app)

# 数据库配置
def get_db_connection():
    """获取数据库连接 - 优先PostgreSQL，失败则用SQLite"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        try:
            # 使用 pg8000 (纯Python PostgreSQL驱动)
            import pg8000
            # Render的DATABASE_URL格式: postgres://user:pass@host:port/dbname
            # 需要转换为 pg8000 格式
            conn = pg8000.dbapi.connect(DATABASE_URL)
            return conn, 'postgresql'
        except Exception as e:
            print(f"PostgreSQL连接失败: {e}, 使用SQLite")
    
    # 回退到SQLite
    import sqlite3
    conn = sqlite3.connect('/tmp/local.db')
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'

def init_db():
    """初始化数据库表"""
    conn, db_type = get_db_connection()
    cur = conn.cursor()
    
    if db_type == 'postgresql':
        # PostgreSQL语法
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
    else:
        # SQLite语法
        cur.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                followers INTEGER DEFAULT 0,
                hearts INTEGER DEFAULT 0,
                videos INTEGER DEFAULT 0,
                account_type TEXT DEFAULT '未知',
                industry TEXT DEFAULT '',
                style TEXT DEFAULT '',
                source TEXT DEFAULT '',
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
    conn, db_type = get_db_connection()
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
            'followers': row[2] or 0,
            'hearts': row[3] or 0,
            'videos': row[4] or 0,
            'account_type': row[5] or '未知',
            'industry': row[6] or '',
            'style': row[7] or '',
            'source': row[8] or '',
            'created_at': str(row[9]) if row[9] else None
        })
    
    cur.close()
    conn.close()
    
    return jsonify(accounts)

# 批量添加账号
@app.route('/api/accounts/batch', methods=['POST'])
def add_accounts_batch():
    data_list = request.json
    if not isinstance(data_list, list):
        return jsonify({'success': False, 'error': 'Expected array'}), 400
    
    conn, db_type = get_db_connection()
    cur = conn.cursor()
    
    inserted = 0
    errors = []
    for data in data_list:
        try:
            # 确保必要字段存在
            username = data.get('username')
            if not username:
                continue
                
            followers = int(data.get('followers', 0) or 0)
            hearts = int(data.get('hearts', 0) or 0)
            videos = int(data.get('videos', 0) or 0)
            account_type = data.get('account_type', '未知') or '未知'
            industry = data.get('industry', '') or ''
            style = data.get('style', '') or ''
            source = data.get('source', '手动导入') or '手动导入'
            
            if db_type == 'postgresql':
                cur.execute('''
                    INSERT INTO accounts (username, followers, hearts, videos, 
                                        account_type, industry, style, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                ''', (username, followers, hearts, videos, account_type, industry, style, source))
            else:
                cur.execute('''
                    INSERT OR IGNORE INTO accounts 
                    (username, followers, hearts, videos, account_type, industry, style, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (username, followers, hearts, videos, account_type, industry, style, source))
            
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            errors.append(f"{data.get('username')}: {e}")
            print(f"插入失败 {data.get('username')}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'count': inserted, 'errors': errors[:5]})

# 获取统计信息
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn, db_type = get_db_connection()
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
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            'total_accounts': 0,
            'high_performers': 0,
            'medium_performers': 0,
            'low_performers': 0,
            'official_count': 0,
            'kol_count': 0,
            'unknown_count': 0,
            'progress': "0/1000",
            'error': str(e)
        }), 500

# 健康检查
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
