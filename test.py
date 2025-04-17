import requests

def get_top_stories(limit=10):
    # API 基地址
    base_url = "https://hacker-news.firebaseio.com/v0"
    
    # 获取热门故事 ID 列表
    top_stories_url = f"{base_url}/topstories.json"
    try:
        response = requests.get(top_stories_url)
        response.raise_for_status()  # 检查请求是否成功
        story_ids = response.json()[:limit]  # 取前 limit 个 ID
        
        # 获取每个故事的详情
        stories = []
        for story_id in story_ids:
            story_url = f"{base_url}/item/{story_id}.json"
            response = requests.get(story_url)
            response.raise_for_status()
            story = response.json()
            stories.append({
                "title": story.get("title", "No Title"),
                "url": story.get("url", "No URL"),
                "score": story.get("score", 0)
            })
        
        return stories
    
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# 运行示例
stories = get_top_stories()
print("Hacker News Top Stories:")
for i, story in enumerate(stories, 1):
    print(f"{i}. {story['title']} (Score: {story['score']})")
    print(f"   URL: {story['url']}\n")