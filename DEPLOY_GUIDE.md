# TikTok 短剧行业数据分析平台 - Render.com 部署指南

## 🚀 快速部署步骤

### 步骤1: 创建GitHub仓库
1. 登录 https://github.com
2. 创建新仓库: `tiktok-analytics-platform`
3. 设置为 Public 或 Private

### 步骤2: 上传代码
在本地执行以下命令:

```bash
# 克隆空仓库
git clone https://github.com/YOUR_USERNAME/tiktok-analytics-platform.git
cd tiktok-analytics-platform

# 或者直接将我准备的代码复制到仓库
# (我已经准备好了完整的代码)
```

**代码已准备好在**: `/root/.openclaw/workspace/tiktok-analytics-platform`

### 步骤3: 连接Render.com
1. 登录 https://render.com (可用GitHub账号登录)
2. 点击 "New +" → "Web Service"
3. 选择 GitHub 仓库: `tiktok-analytics-platform`
4. 配置如下:
   - **Name**: tiktok-analytics-platform
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn server:app`
   - **Plan**: Free

5. 点击 "Create Web Service"

### 步骤4: 创建PostgreSQL数据库
1. 在Render Dashboard点击 "New +" → "PostgreSQL"
2. 配置:
   - **Name**: tiktok-analytics-db
   - **Database**: tiktok_analytics
   - **User**: render_user
   - **Plan**: Free
3. 创建后，Render会自动提供 `DATABASE_URL` 环境变量给Web Service

### 步骤5: 配置环境变量 (如需要)
在Web Service → Environment 中添加:
```
FLASK_ENV=production
```

### 步骤6: 部署完成
- 自动部署约需3-5分钟
- 访问地址: `https://tiktok-analytics-platform.onrender.com`

---

## 📁 代码结构

```
tiktok-analytics-platform/
├── backend/
│   ├── server.py           # Flask后端主程序
│   ├── import_data.py      # 数据导入脚本
│   └── import_existing_data.py
├── frontend/
│   └── index.html          # Web前端界面
├── index.html              # 根目录入口
├── requirements.txt        # Python依赖
├── Procfile               # Render启动命令
├── render.yaml            # Render配置
└── README.md
```

---

## 🔧 技术栈

- **Backend**: Flask 3.0 + PostgreSQL + Gunicorn
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **Database**: PostgreSQL 15 (Render托管)
- **Hosting**: Render.com (免费套餐)

---

## 📊 当前数据

已预置 **47个核心账号**:
- 官方号: 4个 (ReelShort, DramaBox ES, NetShortDramas)
- KOL: 40个 (含动物Drama参考账号)
- 未知: 3个

---

## 🆓 免费额度

| 服务 | 免费额度 | 备注 |
|------|---------|------|
| Web Service | 100GB/月带宽 | 15分钟无访问自动休眠 |
| PostgreSQL | 1GB存储 | 90天无活动暂停 |

---

## 🔒 安全性

- ✅ 自动HTTPS (SSL证书)
- ✅ PostgreSQL内网连接
- ✅ 环境变量加密存储
- ✅ 无服务器管理负担

---

## 📞 需要帮助？

如部署遇到问题，可:
1. 检查Render.com日志 (Dashboard → Logs)
2. 确认环境变量已正确设置
3. 联系T.W协助调试

---

**部署完成后访问地址**: 
`https://tiktok-analytics-platform.onrender.com`
