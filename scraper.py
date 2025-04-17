import requests
import json
import os
import datetime
import logging
from typing import List, Dict, Any
from config import SCRAPER_CONFIG
import asyncio
import aiohttp

class HackerNewsScraper:
    """爬取Hacker News数据的类"""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def __init__(self, data_dir: str = None):
        """初始化爬虫
        
        Args:
            data_dir: 数据存储目录，默认使用配置文件中的设置
        """
        # 从配置文件获取数据目录，如果未提供
        self.data_dir = data_dir if data_dir else SCRAPER_CONFIG["data_dir"]
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("HackerNewsScraper")
    
    def get_top_stories(self, limit: int = None) -> List[int]:
        """获取热门故事ID列表
        
        Args:
            limit: 获取的故事数量上限，默认使用配置文件中的设置
            
        Returns:
            故事ID列表
        """
        # 如果未提供limit，使用配置文件中的设置
        if limit is None:
            limit = SCRAPER_CONFIG["top_stories_limit"]
            
        url = f"{self.BASE_URL}/topstories.json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            story_ids = response.json()
            self.logger.info(f"成功获取{len(story_ids[:limit])}个热门故事ID")
            return story_ids[:limit]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取热门故事失败: {e}")
            return []
    
    def get_new_stories(self, limit: int = None) -> List[int]:
        """获取最新故事ID列表
        
        Args:
            limit: 获取的故事数量上限，默认使用配置文件中的设置
            
        Returns:
            故事ID列表
        """
        # 如果未提供limit，使用配置文件中的设置
        if limit is None:
            limit = SCRAPER_CONFIG["new_stories_limit"]
            
        url = f"{self.BASE_URL}/newstories.json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            story_ids = response.json()
            self.logger.info(f"成功获取{len(story_ids[:limit])}个最新故事ID")
            return story_ids[:limit]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取最新故事失败: {e}")
            return []
    
    def get_best_stories(self, limit: int = None) -> List[int]:
        """获取最佳故事ID列表
        
        Args:
            limit: 获取的故事数量上限，默认使用配置文件中的设置
            
        Returns:
            故事ID列表
        """
        # 如果未提供limit，使用配置文件中的设置
        if limit is None:
            limit = SCRAPER_CONFIG["best_stories_limit"]
            
        url = f"{self.BASE_URL}/beststories.json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            story_ids = response.json()
            self.logger.info(f"成功获取{len(story_ids[:limit])}个最佳故事ID")
            return story_ids[:limit]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"获取最佳故事失败: {e}")
            return []
    
    async def get_item_details(self, item_id: int, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """异步获取单个项目的详细信息"""
        url = f"{self.BASE_URL}/item/{item_id}.json"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                item = await response.json()
                
                if item and item.get('type') == 'story' and 'kids' in item:
                    self.logger.info(f"开始获取故事 {item_id} 的前3条评论")
                    # 异步获取前3条评论
                    tasks = [self.get_item_details(kid, session) for kid in item['kids'][:3]]
                    item['comments'] = await asyncio.gather(*tasks)
                    self.logger.info(f"成功获取故事 {item_id} 的{len(item['comments'])}条评论")
                
                return item
        except Exception as e:
            self.logger.error(f"获取项目 {item_id} 详情失败: {e}")
            return {}

    async def get_stories_details(self, story_ids: List[int]) -> List[Dict[str, Any]]:
        """异步获取多个故事的详细信息"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_item_details(story_id, session) for story_id in story_ids]
            stories = await asyncio.gather(*tasks)
            return [story for story in stories if story and 'dead' not in story and 'deleted' not in story]

    async def collect_daily_data(self, top_limit: int = None, new_limit: int = None, best_limit: int = None) -> Dict[str, Any]:
        """异步收集每日数据"""
        self.logger.info("开始异步收集每日数据")
        
        # 获取各类故事ID
        top_ids = self.get_top_stories(top_limit)
        new_ids = self.get_new_stories(new_limit)
        best_ids = self.get_best_stories(best_limit)
        
        # 异步获取详细信息
        self.logger.info("开始异步获取故事详情")
        top_stories, new_stories, best_stories = await asyncio.gather(
            self.get_stories_details(top_ids),
            self.get_stories_details(new_ids),
            self.get_stories_details(best_ids)
        )
        
        # 组织数据
        data = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.datetime.now().timestamp(),
            "top_stories": top_stories,
            "new_stories": new_stories,
            "best_stories": best_stories
        }
        
        self.logger.info(f"数据异步收集完成")
        return data

    def save_daily_data(self, data: Dict[str, Any]):
        """将每日收集的数据保存到JSON文件"""
        if not data:
            self.logger.warning("没有数据可保存")
            return
            
        date_str = data.get("date")
        if not date_str:
            self.logger.error("数据中缺少日期信息，无法保存")
            return
            
        file_path = os.path.join(self.data_dir, f"{date_str}.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"数据已成功保存到 {file_path}")
        except IOError as e:
            self.logger.error(f"保存数据到 {file_path} 失败: {e}")
        except TypeError as e:
            self.logger.error(f"数据序列化失败: {e}")

# 测试代码
if __name__ == "__main__":
    async def main():
        # 使用配置文件中的设置初始化爬虫
        scraper = HackerNewsScraper()
        # 测试时使用较小的数量
        data = await scraper.collect_daily_data(10, 10, 10)
        # 调用新添加的保存方法
        scraper.save_daily_data(data)
        print(f"共收集了 {len(data['top_stories'])} 个热门故事，{len(data['new_stories'])} 个最新故事，{len(data['best_stories'])} 个最佳故事")
    
    asyncio.run(main())