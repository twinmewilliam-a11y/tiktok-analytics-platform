import json
import csv
import os

DATA_DIR = '../data'
os.makedirs(DATA_DIR, exist_ok=True)
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.json')

# 读取现有数据
accounts = []

# 定义账号类型识别规则
def classify_account(username, followers, industry):
    """根据账号名和特征分类账号类型"""
    username_lower = username.lower()
    
    # 官方号关键词
    official_keywords = ['app', 'official', 'global', 'tv', 'box', 'short', 'reel', 'max', 'es', 'us']
    
    # 检查是否为官方号
    if any(kw in username_lower for kw in official_keywords):
        # 粉丝数超过10万，且名称包含官方关键词
        if followers > 100000:
            return '官方号'
    
    # 其他情况为KOL
    if followers > 100:
        return 'KOL'
    
    return '未知'

# 1. 导入老大提供的历史账号
try:
    with open('/root/.openclaw/workspace/research/account_comparison_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['账号名称']
            followers = int(row['粉丝数']) if row['粉丝数'].isdigit() else 0
            
            # 根据原始类别判断账号类型
            category = row.get('类别', '未知')
            if '官方' in category or '平台' in category:
                account_type = '官方号'
            elif '参考' in category:
                account_type = 'KOL'
            else:
                account_type = classify_account(username, followers, '')
            
            accounts.append({
                'username': username,
                'followers': followers,
                'hearts': int(row['赞数']) if row['赞数'].isdigit() else 0,
                'videos': int(row['视频数']) if row['视频数'].isdigit() else 0,
                'account_type': account_type,
                'industry': '短剧分销',
                'style': category,
                'source': '老大提供',
                'created_at': '2026-03-02'
            })
    print(f"导入 {len(accounts)} 个老大提供账号")
except Exception as e:
    print(f"导入老大账号失败: {e}")

# 2. 导入Exa发现的大号
large_accounts = [
    ('netshortdramas', 3300000, 2100000, 532, '短剧平台', '剧情剪辑', '官方号'),
    ('dreameshort_romance', 1300000, 9000000, 58, '短剧分销', '浪漫爱情', 'KOL'),
    ('dramabox_es', 4700000, 3400000, 1071, '短剧平台', '多语言分发', '官方号'),
    ('dramashorts_movies', 138000, 217300, 218, '短剧分销', '影视剪辑', 'KOL'),
    ('minishorts_lovestory', 25000, 134900, 150, '短剧分销', '甜宠爱情', 'KOL'),
    ('meowarmyvibes', 3000000, 11100000, 153, '动物Drama', '萌宠剧情', 'KOL'),
    ('noveyflix', 813600, 8600000, 108, '动物Drama', '创意剧情', 'KOL'),
    ('catpart2revenge2', 20800, 127300, 135, '动物Drama', '萌宠剧情', 'KOL'),
    ('reelshortapp', 8100000, 25100000, 4951, '短剧平台', '综合', '官方号'),
]

for username, followers, hearts, videos, industry, style, account_type in large_accounts:
    if not any(a['username'] == username for a in accounts):
        accounts.append({
            'username': username,
            'followers': followers,
            'hearts': hearts,
            'videos': videos,
            'account_type': account_type,
            'industry': industry,
            'style': style,
            'source': 'Exa发现',
            'created_at': '2026-03-02'
        })

# 3. 导入批量检查发现的小号
try:
    with open('/root/.openclaw/workspace/research/batch_accounts_check.csv', 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            username = row['账号']
            followers = int(row['粉丝数']) if row['粉丝数'].isdigit() else 0
            
            if followers > 100 and not any(a['username'] == username for a in accounts):
                account_type = classify_account(username, followers, '')
                
                accounts.append({
                    'username': username,
                    'followers': followers,
                    'hearts': int(row['赞数']) if row['赞数'].isdigit() else 0,
                    'videos': int(row['视频数']) if row['视频数'].isdigit() else 0,
                    'account_type': account_type,
                    'industry': '短剧分销',
                    'style': '待分析',
                    'source': '批量检查',
                    'created_at': '2026-03-03'
                })
                count += 1
        print(f"导入 {count} 个批量检查账号")
except Exception as e:
    print(f"导入批量账号失败: {e}")

# 保存数据
with open(ACCOUNTS_FILE, 'w') as f:
    json.dump(accounts, f, indent=2)

print(f"\n总计导入 {len(accounts)} 个账号到平台")

# 统计
official = sum(1 for a in accounts if a['account_type'] == '官方号')
kol = sum(1 for a in accounts if a['account_type'] == 'KOL')
unknown = sum(1 for a in accounts if a['account_type'] == '未知')

high = sum(1 for a in accounts if a['followers'] > 10000)
medium = sum(1 for a in accounts if 1000 <= a['followers'] <= 10000)
low = sum(1 for a in accounts if a['followers'] < 1000)

print(f"账号类型: 官方号{official}个, KOL{kol}个, 未知{unknown}个")
print(f"粉丝分布: 大号{high}个, 中号{medium}个, 小号{low}个")
