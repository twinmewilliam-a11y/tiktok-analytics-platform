import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import get_db_connection, init_db

def import_initial_data():
    """导入初始账号数据"""
    init_db()
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 导入核心账号数据
    accounts = [
        # 官方号
        ('reelshortapp', 8100000, 25100000, 4951, '官方号', '短剧平台', '综合', '分析导入'),
        ('dramabox_es', 4700000, 3400000, 1071, '官方号', '短剧平台', '多语言分发', '分析导入'),
        ('netshortdramas', 3300000, 2100000, 532, '官方号', '短剧平台', '剧情剪辑', '分析导入'),
        
        # KOL大号
        ('meowarmyvibes', 3000000, 11100000, 153, 'KOL', '动物Drama', '萌宠剧情', '分析导入'),
        ('dreameshort_romance', 1300000, 9000000, 58, 'KOL', '短剧分销', '浪漫爱情', '分析导入'),
        ('noveyflix', 813600, 8600000, 108, 'KOL', '动物Drama', '创意剧情', '分析导入'),
        ('dramashorts_movies', 138000, 217300, 218, 'KOL', '短剧分销', '影视剪辑', '分析导入'),
        ('minishorts_lovestory', 25000, 134900, 150, 'KOL', '短剧分销', '甜宠爱情', '分析导入'),
        ('catpart2revenge2', 20800, 127300, 135, 'KOL', '动物Drama', '萌宠剧情', '分析导入'),
        
        # 老大提供的高播放账号
        ('janepiercef699', 3684, 18700, 201, 'KOL', '短剧分销', '高播放', '老大提供'),
        ('felicityhunt7884', 273, 5951, 180, 'KOL', '短剧分销', '高播放', '老大提供'),
        ('nelliebrown86dd', 174, 2314, 176, 'KOL', '短剧分销', '高播放', '老大提供'),
        ('paulthompsonb49a', 157, 1954, 167, 'KOL', '短剧分销', '高播放', '老大提供'),
        
        # 老大提供的低播放账号
        ('dorothywright8160', 1087, 3252, 284, 'KOL', '短剧分销', '低播放', '老大提供'),
        ('dustinclarka9a2', 1670, 5866, 202, 'KOL', '短剧分销', '低播放', '老大提供'),
        ('emmamendozaa78d', 1157, 3239, 218, 'KOL', '短剧分销', '低播放', '老大提供'),
    ]
    
    inserted = 0
    for acc in accounts:
        try:
            cur.execute('''
                INSERT INTO accounts (username, followers, hearts, videos, 
                                    account_type, industry, style, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            ''', acc)
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"插入失败 {acc[0]}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"成功导入 {inserted} 个账号")

if __name__ == '__main__':
    import_initial_data()
