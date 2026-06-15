"""
Weekly AI & Tech Intelligence Report Generator
Uses RSS feeds (free) + Groq API (free) to generate the report.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from groq import Groq
import feedparser

RSS_FEEDS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge",     "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Ars Technica",  "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("VentureBeat",   "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ("Hacker News",   "https://news.ycombinator.com/rss"),
    ("ArXiv CS.AI",   "https://rss.arxiv.org/rss/cs.AI"),
    ("ArXiv CS.LG",   "https://rss.arxiv.org/rss/cs.LG"),
]

SYSTEM_PROMPT = """
Bạn là Hệ thống Trí tuệ Chiến lược Công nghệ cấp cao (Global Tech Intelligence Agent), vận hành với tư duy của một CTO kiêm Venture Capitalist hàng đầu trong lĩnh vực AI và Bán dẫn.

RÀNG BUỘC NGHIÊM NGẶT:
- Viết hoàn toàn bằng tiếng Việt chuyên nghiệp, sắc bén, khách quan.
- TUYỆT ĐỐI KHÔNG dùng: "đi sâu", "bức tranh tổng thể", "minh chứng cho", "ngọn hải đăng", "kỷ nguyên mới", "bến đỗ".
- Mỗi câu phải có ít nhất một thực thể cụ thể (tên công ty, chỉ số, tên mô hình).
- Chỉ dùng thông tin có thật từ dữ liệu đầu vào — KHÔNG bịa đặt.
- Gắn URL gốc chính xác vào mỗi tiêu đề mục dưới dạng thẻ <a href="...">.
- Trả về CHỈ mã HTML hoàn chỉnh, không có giải thích hay markdown bọc ngoài.
"""


def fetch_articles(days: int = 7) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    articles = []

    for source, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                if published and published < cutoff:
                    continue
                title = entry.get("title", "").strip()
                link  = entry.get("link", "").strip()
                summary = entry.get("summary", entry.get("description", ""))[:300].strip()
                if title and link:
                    articles.append(f"[{source}] {title}\nURL: {link}\nTóm tắt: {summary}\n")
        except Exception as e:
            print(f"[fetch] Warning: could not fetch {source}: {e}")

    print(f"[fetch] Collected {len(articles)} articles from RSS feeds")
    return "\n---\n".join(articles)


def build_prompt(articles_text: str) -> str:
    now = datetime.now()
    week_num = now.isocalendar()[1]
    date_str = now.strftime("%d/%m/%Y")

    return f"""
Dưới đây là danh sách bài viết thu thập từ RSS feeds trong 7 ngày qua:

{articles_text}

Hãy thực hiện:
1. LỌC: Giữ lại những bài có giá trị kỹ thuật thực sự (model mới, benchmark, kiến trúc, open-source nổi bật, M&A chiến lược, chính sách AI lớn). Loại bỏ quảng cáo, gọi vốn nhỏ không đột phá, tin lặp.
2. PHÂN CỤM: Gom các bài về cùng sự kiện thành 1 mục.
3. XUẤT HTML hoàn chỉnh theo template sau (thay tất cả placeholder bằng nội dung thực, Tuần={week_num}, Ngày={date_str}):

<!DOCTYPE html>
<html>
<body>
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333333; line-height: 1.6;">
  <div style="background-color: #1a202c; color: #ffffff; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
    <h1 style="margin: 0; font-size: 22px;">&#x1F916; BÁO CÁO TÌNH BÁO AI & CÔNG NGHỆ TOÀN CẦU</h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; color: #cbd5e0;">Tuần {week_num} &#8212; {date_str} | Bản tin phân tích chiến lược dành riêng cho Cấp Quản Lý</p>
  </div>
  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none;">
    <h2 style="color: #2b6cb0; border-bottom: 2px solid #2b6cb0; padding-bottom: 5px; font-size: 18px;">&#x1F525; 1. Điểm Nóng & Đột Phá Công Nghệ Lớn Nhất Tuần</h2>
    [3-5 khối sự kiện, mỗi khối:]
    <div style="margin-bottom: 20px; padding: 12px; background-color: #ebf8ff; border-left: 4px solid #2b6cb0; border-radius: 4px;">
      <h3 style="color: #2d3748; font-size: 16px; margin: 0 0 5px 0;">&#x1F539; <a href="URL_GỐC" style="color: #2b6cb0; text-decoration: none;">TÊN SỰ KIỆN</a></h3>
      <p style="margin: 0; font-size: 14px;"><strong>Bản chất kỹ thuật:</strong> chỉ số, kiến trúc, benchmark cụ thể.</p>
      <p style="margin: 5px 0 0 0; font-size: 14px;"><strong>Tại sao quan trọng:</strong> tác động thị trường, đối thủ, lập trình viên.</p>
    </div>
  </div>
  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; background-color: #f7fafc;">
    <h2 style="color: #2c5282; border-bottom: 2px solid #2c5282; padding-bottom: 5px; font-size: 18px;">&#x1F6E0;&#xFE0F; 2. Mô Hình Mã Nguồn Mở & Công Cụ Kỹ Thuật Đáng Chú Ý</h2>
    <ul style="padding-left: 20px; margin: 0; font-size: 14px;">
      [3-5 mục: <li style="margin-bottom:10px;"><strong><a href="URL" style="color:#3182ce;text-decoration:none;">Tên</a></strong>: công dụng, thông số.</li>]
    </ul>
  </div>
  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none;">
    <h2 style="color: #276749; border-bottom: 2px solid #276749; padding-bottom: 5px; font-size: 18px;">&#x1F4CA; 3. Động Thái Thị Trường & Chiến Lược Doanh Nghiệp</h2>
    <ul style="padding-left: 20px; margin: 0; font-size: 14px;">
      [2-3 mục: M&A, đầu tư, chính sách Big Tech]
    </ul>
  </div>
  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; background-color: #fffbeb; border-radius: 0 0 8px 8px;">
    <h2 style="color: #dd6b20; border-bottom: 2px solid #dd6b20; padding-bottom: 5px; font-size: 18px;">&#x1F9E0; 4. CTO Insight &#8212; Dự Báo Tuần Tới</h2>
    <p style="margin: 0; font-size: 14px; font-style: italic; color: #4a5568;">2-3 câu phân tích xu hướng và dự báo.</p>
  </div>
</div>
</body>
</html>
"""


def generate_report() -> str:
    articles = fetch_articles(days=7)
    if not articles:
        raise ValueError("No articles collected from RSS feeds")

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    print("[generate] Calling Groq API (llama-3.3-70b)...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_prompt(articles)},
        ],
        temperature=0.3,
        max_tokens=8000,
    )

    html_content = response.choices[0].message.content.strip()

    # Strip markdown code fences if model added them
    if html_content.startswith("```"):
        lines = html_content.splitlines()
        html_content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    print(f"[generate] Report generated ({len(html_content)} chars)")
    return html_content


def save_report(html_content: str) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"report-{today}.html"
    output_path.write_text(html_content, encoding="utf-8")
    print(f"[generate] Saved to {output_path}")
    return output_path


if __name__ == "__main__":
    html = generate_report()
    report_path = save_report(html)
    print(str(report_path))
