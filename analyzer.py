import json
import os
import datetime
from typing import List, Dict, Any
import openai
import re

class HackerNewsAnalyzer:
    """分析Hacker News数据并生成报告的类"""
    
    def __init__(self, data_dir: str = None, reports_dir: str = None, api_key: str = None):
        """初始化分析器
        
        Args:
            data_dir: 数据存储目录，默认使用配置文件中的设置
            reports_dir: 报告存储目录，默认使用配置文件中的设置
            api_key: OpenAI API密钥，默认使用配置文件中的设置
        """
        from config import ANALYZER_CONFIG
        
        # 从配置文件获取设置，如果未提供
        self.data_dir = data_dir if data_dir else ANALYZER_CONFIG["data_dir"]
        self.reports_dir = reports_dir if reports_dir else ANALYZER_CONFIG["reports_dir"]
        self.model = ANALYZER_CONFIG["model"]  # 存储模型名称
        self.api_base_url = ANALYZER_CONFIG["api_base_url"]  # 存储API地址
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 设置OpenAI API密钥
        self.api_key = api_key if api_key else ANALYZER_CONFIG.get("api_key")
        if not self.api_key:
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("需要提供OpenAI API密钥(通过参数、配置文件或环境变量)")
    
    def load_daily_data(self, date_str: str = None) -> Dict[str, Any]:
        """加载指定日期的数据
        
        Args:
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            
        Returns:
            加载的数据字典
        """
        if date_str is None:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        file_path = os.path.join(self.data_dir, f"{date_str}.json")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"找不到{date_str}的数据文件")
            return None
    
    def get_last_n_days_data(self, n: int = 7) -> List[Dict[str, Any]]:
        """获取最近n天的数据
        
        Args:
            n: 天数
            
        Returns:
            数据列表，按日期排序
        """
        data_list = []
        today = datetime.datetime.now()
        
        for i in range(n):
            date = today - datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            data = self.load_daily_data(date_str)
            if data:
                data_list.append(data)
        
        # 按日期排序
        data_list.sort(key=lambda x: x["date"])
        return data_list
    
    def generate_daily_report(self, date_str: str = None) -> str:
        """生成每日报告
        
        Args:
            date_str: 日期字符串，格式为YYYY-MM-DD，默认为今天
            
        Returns:
            生成的报告文本
        """
        if date_str is None:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 加载数据
        data = self.load_daily_data(date_str)
        if not data:
            return f"无法生成{date_str}的报告：找不到数据"
        
        # 准备提示
        prompt = self._prepare_daily_prompt(data)
        
        # 调用AI生成报告 (更新为v1.0.0+ API)
        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base_url  # 使用实例变量中的API地址
            )
            response = client.chat.completions.create(
                model=self.model,  # 使用实例变量中的模型名称
                messages=[
                    {"role": "system", "content": "你是一个专业的技术新闻分析师..."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            report = response.choices[0].message.content
        except Exception as e:
            report = f"生成报告时出错：{str(e)}"
        
        # 保存报告
        self._save_report(report, date_str, "daily")
        
        return report
    
    def generate_weekly_report(self) -> str:
        """生成每周报告
        
        Returns:
            生成的报告文本
        """
        # 获取过去7天的数据
        data_list = self.get_last_n_days_data(7)
        if not data_list:
            return "无法生成周报：找不到数据"
        
        # 准备提示
        prompt = self._prepare_weekly_prompt(data_list)
        
        # 调用AI生成报告 (更新为v1.0.0+ API)
        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base_url  # 使用实例变量中的API地址
            )
            response = client.chat.completions.create(
                model=self.model,  # 使用实例变量中的模型名称
                messages=[
                    {"role": "system", "content": "你是一个专业的技术新闻分析师..."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            report = response.choices[0].message.content
        except Exception as e:
            report = f"生成周报时出错：{str(e)}"
        
        # 获取本周结束日期
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # 保存报告
        self._save_report(report, end_date, "weekly")
        
        return report
    
    def _prepare_daily_prompt(self, data: Dict[str, Any]) -> str:
        """准备每日报告的提示
        
        Args:
            data: 当日数据
            
        Returns:
            提示文本
        """
        date = data["date"]
        top_stories = data["top_stories"]
        new_stories = data["new_stories"]
        best_stories = data["best_stories"]
        
        # 提取最重要的信息
        top_10 = sorted(top_stories, key=lambda x: x.get("score", 0), reverse=True)[:10]
        
        prompt = f"""请根据以下Hacker News数据，生成{date}的每日技术新闻摘要报告。

今日热门故事TOP 10：
"""
        
        for i, story in enumerate(top_10, 1):
            title = story.get("title", "无标题")
            url = story.get("url", "")
            score = story.get("score", 0)
            comments = story.get("descendants", 0)
            prompt += f"{i}. {title} (得分: {score}, 评论: {comments})\n   链接: {url}\n\n"
        
        prompt += """请提供以下内容：
1. 今日热点概述：简要总结今天Hacker News上的主要热点和趋势。
2. 值得关注的话题：挑选3-5个最值得关注的话题，并解释为什么它们重要。
3. 技术趋势分析：基于今天的热门话题，分析当前的技术趋势。
4. 推荐阅读：推荐1-2篇最值得深入阅读的文章，并简要说明理由。

请以清晰、专业的语言撰写报告，面向技术从业者。报告应当简洁明了，突出重点，避免冗长。"""
        
        return prompt
    
    def _prepare_weekly_prompt(self, data_list: List[Dict[str, Any]]) -> str:
        """准备每周报告的提示
        
        Args:
            data_list: 一周的数据列表
            
        Returns:
            提示文本
        """
        start_date = data_list[0]["date"]
        end_date = data_list[-1]["date"]
        
        # 合并所有故事
        all_stories = []
        for data in data_list:
            all_stories.extend(data["top_stories"])
            all_stories.extend(data["best_stories"])
        
        # 去重（按ID）
        unique_stories = {}
        for story in all_stories:
            if "id" in story and story["id"] not in unique_stories:
                unique_stories[story["id"]] = story
        
        # 按得分排序取前20
        top_20 = sorted(unique_stories.values(), key=lambda x: x.get("score", 0), reverse=True)[:20]
        
        prompt = f"""请根据以下Hacker News数据，生成{start_date}至{end_date}的每周技术新闻摘要报告。

本周热门故事TOP 20：
"""
        
        for i, story in enumerate(top_20, 1):
            title = story.get("title", "无标题")
            url = story.get("url", "")
            score = story.get("score", 0)
            comments = story.get("descendants", 0)
            prompt += f"{i}. {title} (得分: {score}, 评论: {comments})\n   链接: {url}\n\n"
        
        prompt += """请提供以下内容：
1. 本周热点概述：简要总结本周Hacker News上的主要热点和趋势。
2. 热门话题分析：分析本周最受关注的3-5个技术话题，并解释它们为什么重要。
3. 技术趋势洞察：基于本周的热门话题，分析当前的技术趋势和可能的发展方向。
4. 重要项目和工具：介绍本周出现的值得关注的开源项目、工具或服务。
5. 行业动态：总结本周技术行业的重要动态和变化。
6. 推荐阅读：推荐2-3篇本周最值得深入阅读的文章，并简要说明理由。

请以清晰、专业的语言撰写报告，面向技术从业者。报告应当全面但不冗长，突出重点，提供有价值的洞察。"""
        
        return prompt
    
    def _save_report(self, report: str, date_str: str, report_type: str):
        """保存报告
        
        Args:
            report: 报告文本
            date_str: 日期字符串
            report_type: 报告类型（daily或weekly）
        """
        file_name = f"{date_str}_{report_type}_report.md"
        file_path = os.path.join(self.reports_dir, file_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"报告已保存到 {file_path}")

# 测试代码
if __name__ == "__main__":
    # 注意：实际使用时需要提供API密钥
    analyzer = HackerNewsAnalyzer()
    
    # 假设已经有当天的数据
    try:
        daily_report = analyzer.generate_daily_report()
        print("\n每日报告预览:\n" + daily_report[:300] + "...")
    except Exception as e:
        print(f"生成每日报告时出错: {e}")
    
    # 假设已经有一周的数据
    try:
        weekly_report = analyzer.generate_weekly_report()
        print("\n每周报告预览:\n" + weekly_report[:300] + "...")
    except Exception as e:
        print(f"生成每周报告时出错: {e}")