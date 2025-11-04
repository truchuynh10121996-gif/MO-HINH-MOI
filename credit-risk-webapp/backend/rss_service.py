"""
Module xử lý RSS Feed từ các nguồn tin tài chính
"""

from typing import List, Dict
from datetime import datetime

try:
    import feedparser
    from dateutil import parser as date_parser
    FEEDPARSER_OK = True
except Exception:
    feedparser = None
    FEEDPARSER_OK = False


def fetch_rss_feed(url: str, source_name: str) -> List[Dict]:
    """
    Đọc RSS feed từ URL và trả về 5 bài mới nhất.

    Args:
        url: Đường dẫn RSS feed
        source_name: Tên nguồn tin

    Returns:
        List[Dict]: List các bài viết với {title, link, published}
    """
    if not FEEDPARSER_OK:
        return [{"title": "⚠️ Thiếu thư viện feedparser", "link": "#", "published": ""}]

    try:
        feed = feedparser.parse(url)
        articles = []

        # Lấy 5 bài mới nhất
        for entry in feed.entries[:5]:
            title = entry.get('title', 'Không có tiêu đề')
            link = entry.get('link', '#')

            # Xử lý thời gian
            published = entry.get('published', '')
            if not published:
                published = entry.get('updated', '')

            # Format thời gian nếu có
            if published:
                try:
                    dt = date_parser.parse(published)
                    published = dt.strftime('%d/%m/%Y %H:%M')
                except Exception:
                    pass

            articles.append({
                'title': title,
                'link': link,
                'published': published
            })

        return articles

    except Exception as e:
        return [{
            "title": f"❌ Lỗi khi tải RSS từ {source_name}",
            "link": "#",
            "published": str(e)
        }]


def get_all_rss_feeds() -> Dict[str, List[Dict]]:
    """
    Lấy tất cả RSS feeds từ các nguồn tin tài chính Việt Nam.

    Returns:
        Dict với key là tên nguồn, value là list các bài viết
    """
    rss_sources = {
        "CafeF": "https://cafef.vn/thi-truong-chung-khoan.rss",
        "Vietstock": "https://vietstock.vn/rss/tai-chinh.rss",
        "Báo Đầu tư": "https://baodautu.vn/rss/kinh-doanh.rss",
        "VNExpress": "https://vnexpress.net/rss/kinh-doanh.rss"
    }

    feeds = {}
    for source_name, url in rss_sources.items():
        feeds[source_name] = fetch_rss_feed(url, source_name)

    return feeds
