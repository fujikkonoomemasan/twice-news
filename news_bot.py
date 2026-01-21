import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

DATA_FILE = "news_data.json"

# Googleニュース（RSS）を取得
def fetch_google_news():
    url = "https://news.google.com/rss/search?q=TWICE&hl=ja&gl=JP&ceid=JP:ja"
    news_list = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'xml') # XMLパーサーを使用
        items = soup.find_all('item')
        
        for item in items[:10]: # 最新10件
            pub_date = item.pubDate.text
            # 日付変換（簡易）
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = datetime.now().strftime("%Y-%m-%d")

            news_list.append({
                "source": "News",
                "title": item.title.text,
                "date": date_str,
                "link": item.link.text,
                "summary": "Google News Search Result"
            })
    except Exception as e:
        print(f"Error fetching Google News: {e}")
    return news_list

# 公式サイトを取得
def fetch_official_news():
    url = "https://www.twicejapan.com/news/"
    news_list = []
    try:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # リンク探索
        links = soup.find_all('a', href=True)
        for a in links:
            if '/news/detail/' in a['href']:
                title = a.get_text(strip=True)
                if len(title) > 5:
                    link = a['href']
                    if not link.startswith('http'): link = 'https://www.twicejapan.com' + link
                    
                    news_list.append({
                        "source": "Official",
                        "title": title[:60] + "...",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "link": link,
                        "summary": "Official Site Update"
                    })
    except Exception as e:
        print(f"Error fetching Official: {e}")
    return news_list[:5]

def main():
    # データ収集
    new_data = fetch_official_news() + fetch_google_news()
    
    # 既存データ読み込み
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
        except:
            old_data = []
    else:
        old_data = []

    # 重複削除してマージ
    existing_links = [item['link'] for item in old_data]
    final_data = []
    
    # 新しいデータを先頭に
    for item in new_data:
        if item['link'] not in existing_links:
            final_data.append(item)
    
    # 古いデータも維持（最大30件）
    final_data.extend(old_data)
    final_data = final_data[:30]

    # 保存
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print("Update Complete.")

if __name__ == "__main__":
    main()
