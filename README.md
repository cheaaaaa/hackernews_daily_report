# Hacker News 每日报告生成器

这是一个自动化工具，用于每天抓取 Hacker News 上的热门信息，使用 AI 生成日报和周报，并将数据存储起来以供后续分析。

## 功能特点

- 自动抓取 Hacker News 上的热门、最新和最佳故事
- 使用 OpenAI API 生成每日技术新闻摘要报告
- 每周日自动生成一份周报，总结一周内的技术趋势和热点
- 将原始数据以 JSON 格式存储，便于后续分析和查询
- 支持定时任务，可设置为每天自动运行

## 目录结构

```
.
├── data/                # 存储每日抓取的原始数据
├── reports/             # 存储生成的日报和周报
├── scraper.py           # 负责抓取 Hacker News 数据的模块
├── analyzer.py          # 负责分析数据并生成报告的模块
├── main.py              # 主程序，用于调度任务
├── requirements.txt     # 项目依赖
└── README.md            # 项目说明文档
```

## 安装与配置

1. 克隆本仓库到本地：

```bash
git clone <仓库地址>
cd heckernews_daily_report
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 设置 OpenAI API 密钥：

```bash
export OPENAI_API_KEY="your_api_key_here"
```
或者在 `config.py` 中设置
## 使用方法

### 立即运行一次

```bash
python main.py --now
```

这将立即执行一次数据抓取和报告生成任务。

### 启动定时任务

```bash
python main.py --schedule
```

这将启动调度器，默认每天凌晨 2:00 自动执行任务。

## 报告示例

### 每日报告

每日报告保存在 `reports/` 目录下，文件名格式为 `YYYY-MM-DD_daily_report.md`。报告内容包括：

- 今日热点概述
- 值得关注的话题
- 技术趋势分析
- 推荐阅读

### 每周报告

每周报告保存在 `reports/` 目录下，文件名格式为 `YYYY-MM-DD_weekly_report.md`。报告内容包括：

- 本周热点概述
- 热门话题分析
- 技术趋势洞察
- 重要项目和工具
- 行业动态
- 推荐阅读

## 自定义配置

如需修改默认配置，可以编辑 `main.py` 和 `config.py` 文件中的相关参数：

- 修改定时任务的执行时间
- 调整抓取的故事数量
- 更改数据和报告的存储路径

## 注意事项

- 请确保有稳定的网络连接以访问 Hacker News API 和 OpenAI API
- 使用 OpenAI API 会产生费用，请注意控制使用量
- 建议将程序部署在服务器上以确保定时任务的可靠执行

## 许可证

MIT