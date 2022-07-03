# Stage1st 《不补可惜哦》投票可视化统计

将 S1 《不补可惜哦》系列帖子的数据进行抓取和可视化。

## 使用

```bash
# 创建 venv 环境
python3 -m venv venv && \
    source venv/bin/active && \
    python3 -m pip install -r requirements.txt
# 运行爬虫
python3 main.py
cp data/data.db public/data.db
# 前端库安装，项目构建
npm install
npm run build
```

## 项目架构

```plaintext
~/d/w/s/s1_vote > tree --gitignore
.
├── data             # 数据
├── main.py          # 爬虫主程序
├── package.json
├── package-lock.json
├── public           # 可视化 css/html，相关的代码
│   ├── index.css
│   └── index.html
├── README.md
├── requirements.txt
├── spider           # 爬虫代码
│   ├── exchange.py
│   ├── item.py
│   ├── pipeline.py
│   ├── query.py
│   ├── spider.py
│   ├── test_all.py
│   └── update.py
├── visualizer       # 可视化相关代码
│   └── index.js
└── vite.config.js
```
