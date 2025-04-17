# Hacker News 每日报告生成器配置文件

# 爬虫配置
SCRAPER_CONFIG = {
    # 每天抓取的故事数量
    "top_stories_limit": 10,    # 热门故事数量
    "new_stories_limit": 10,    # 最新故事数量
    "best_stories_limit": 100,   # 最佳故事数量
    'comments_limit': 3,
    # 数据存储目录
    "data_dir": "data"
}

# 分析器配置
ANALYZER_CONFIG = {
    # 数据目录
    "data_dir": "data",
    
    # 报告存储目录
    "reports_dir": "reports",
    
    # OpenAI模型配置
    "model": "deepseek-chat",           # 使用的模型
    "daily_max_tokens": 2000,   # 每日报告最大token数
    "weekly_max_tokens": 3000,  # 每周报告最大token数
    "temperature": 0.7,         # 生成文本的创造性程度
    "api_base_url": "https://api.deepseek.com/v1",  # DeepSeek API地址
    "api_key": "your_api_key"  # 新增API密钥配置
}

# 调度器配置
SCHEDULER_CONFIG = {
    # 每日任务执行时间（24小时制）
    "daily_run_time": "02:00",
    
    # 是否在周日生成周报
    "generate_weekly_report": True,
    
    # 调度器检查间隔（秒）
    "scheduler_interval": 60
}