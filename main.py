import os
import time
import datetime
import argparse
import schedule
from scraper import HackerNewsScraper
from analyzer import HackerNewsAnalyzer
import asyncio

def setup_directories():
    """设置必要的目录结构"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    print("目录结构已创建")

async def collect_data():
    """收集当天的Hacker News数据"""
    print(f"开始收集数据 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    scraper = HackerNewsScraper()
    data = await scraper.collect_daily_data()  # 添加await
    scraper.collect_daily_data(data)
    print(f"数据收集完成 - 共收集了 {len(data['top_stories'])} 个热门故事，{len(data['new_stories'])} 个最新故事，{len(data['best_stories'])} 个最佳故事")
    return True

async def run_daily_tasks_async():
    """异步运行每日任务"""
    success = await collect_data()
    if success:
        generate_daily_report()
    generate_weekly_report()

def run_daily_tasks():
    """同步包装器用于调度器"""
    asyncio.run(run_daily_tasks_async())

def run_scheduler():
    """运行调度器"""
    print("启动调度器...")
    # 设置每天凌晨2点运行任务（避开高峰期）
    schedule.every().day.at("02:00").do(run_daily_tasks)  # 使用同步包装器
    
    print(f"调度器已启动，将在每天02:00执行任务")
    print(f"下次执行时间: {schedule.next_run()}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

def run_once():
    """立即运行一次任务"""
    setup_directories()
    # 直接运行异步任务
    asyncio.run(run_daily_tasks_async())

def generate_daily_report():
    """生成每日报告"""
    print(f"开始生成每日报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analyzer = HackerNewsAnalyzer()
    report = analyzer.generate_daily_report()
    print("每日报告生成完成")
    return True

def generate_weekly_report():
    """生成每周报告"""
    # 检查今天是否为周日
    if datetime.datetime.now().weekday() != 6:  # 0是周一，6是周日
        print("今天不是周日，跳过生成周报")
        return False
    
    print(f"开始生成每周报告 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analyzer = HackerNewsAnalyzer(api_key=api_key)
    report = analyzer.generate_weekly_report()
    print("每周报告生成完成")
    return True

# 删除这个错误的 run_daily_tasks 定义
# def run_daily_tasks():
#     """运行每日任务"""
#     success = collect_data() # <--- 错误在这里，没有 await
#     if success:
#         generate_daily_report()
#     generate_weekly_report()  # 会自动检查是否为周日

def run_scheduler():
    """运行调度器"""
    print("启动调度器...")
    # 设置每天凌晨2点运行任务（避开高峰期）
    schedule.every().day.at("02:00").do(run_daily_tasks)
    
    print(f"调度器已启动，将在每天02:00执行任务")
    print(f"下次执行时间: {schedule.next_run()}")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

def run_once():
    """立即运行一次任务"""
    setup_directories()
    run_daily_tasks()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Hacker News 每日报告生成器")
    parser.add_argument("--now", action="store_true", help="立即运行一次任务")
    parser.add_argument("--schedule", action="store_true", help="启动调度器")
    
    args = parser.parse_args()
    
    setup_directories()
    
    if args.now:
        run_once()
    elif args.schedule:
        run_scheduler()
    else:
        # 默认行为：立即运行一次任务
        print("未指定运行模式，默认立即运行一次任务")
        run_once()

if __name__ == "__main__":
    main()