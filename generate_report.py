"""
Weekly AI & Tech Intelligence Report Generator
Uses Claude API with built-in web search to gather, analyze, and format news.
"""

import anthropic
import os
import sys
from datetime import datetime
from pathlib import Path

SYSTEM_PROMPT = """
Bạn là Hệ thống Trí tuệ Chiến lược Công nghệ cấp cao (Global Tech Intelligence Agent), vận hành với tư duy của một CTO kiêm Venture Capitalist hàng đầu trong lĩnh vực AI và Bán dẫn.

Nhiệm vụ: Thu thập tin tức AI và công nghệ toàn cầu trong 7 ngày qua, lọc và phân tích, xuất ra HTML báo cáo hoàn chỉnh.

KỸ NĂNG CỐT LÕI:
1. Semantic Clustering: Gom nhóm 10-20 bài viết nói về cùng sự kiện thành một chủ đề duy nhất.
2. Signal-to-Noise Filtering: Bóc tách giá trị công nghệ thực tế khỏi chiêu trò PR/SEO.
3. Technical Synthesis: Đọc hiểu thuật ngữ sâu (Parameters, Context Window, TOPS, RAG, Agentic Workflow) và giải thích súc tích.

RÀNG BUỘC NGHIÊM NGẶT:
- Viết hoàn toàn bằng tiếng Việt chuyên nghiệp, sắc bén, khách quan.
- TUYỆT ĐỐI KHÔNG dùng: "đi sâu", "bức tranh tổng thể", "minh chứng cho", "ngọn hải đăng", "kỷ nguyên mới", "bến đỗ", "chứng kiến bước tiến vĩ đại".
- Mỗi câu phải có ít nhất một thực thể cụ thể (tên công ty, chỉ số, tên mô hình).
- Chỉ dùng thông tin có thật từ kết quả tìm kiếm — KHÔNG bịa đặt.
- Gắn URL gốc chính xác vào mỗi tiêu đề mục.
"""

USER_PROMPT = """
Hãy thực hiện theo thứ tự sau:

BƯỚC 1 — THU THẬP TIN TỨC
Tìm kiếm web với ít nhất 6 query sau để thu thập tin tức AI và công nghệ trong 7 ngày qua:
1. "AI model release benchmark site:techcrunch.com OR site:theverge.com"
2. "LLM open source release site:huggingface.co OR site:arxiv.org"
3. "semiconductor chip AI hardware news site:arstechnica.com OR site:venturebeat.com"
4. "artificial intelligence funding acquisition deal this week"
5. "AI agent agentic workflow autonomous latest"
6. "machine learning research paper breakthrough site:arxiv.org"

BƯỚC 2 — LỌC VÀ PHÂN CỤM
- LOẠI BỎ: quảng cáo, gọi vốn seed không đột phá kỹ thuật, tin lặp lại, bài PR không có số liệu
- GIỮ LẠI: model mới có benchmark cụ thể, đột phá kiến trúc, open-source nổi bật, M&A chiến lược, phần cứng AI thế hệ mới
- GOM CỤM các bài cùng sự kiện thành 1 mục

BƯỚC 3 — XUẤT HTML
Trả về CHỈ mã HTML hoàn chỉnh (không giải thích, không markdown), theo đúng template sau. Thay tất cả placeholder bằng nội dung thực tế:

<!DOCTYPE html>
<html>
<body>
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333333; line-height: 1.6;">

  <div style="background-color: #1a202c; color: #ffffff; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
    <h1 style="margin: 0; font-size: 22px;">&#x1F916; BÁO CÁO TÌNH BÁO AI & CÔNG NGHỆ TOÀN CẦU</h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; color: #cbd5e0;">Tuần [SỐ TUẦN] &#8212; [NGÀY/THÁNG/NĂM] | Bản tin phân tích chiến lược dành riêng cho Cấp Quản Lý</p>
  </div>

  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none;">
    <h2 style="color: #2b6cb0; border-bottom: 2px solid #2b6cb0; padding-bottom: 5px; font-size: 18px;">&#x1F525; 1. Điểm Nóng & Đột Phá Công Nghệ Lớn Nhất Tuần</h2>
    [3-5 khối sau, mỗi sự kiện một khối:]
    <div style="margin-bottom: 20px; padding: 12px; background-color: #ebf8ff; border-left: 4px solid #2b6cb0; border-radius: 4px;">
      <h3 style="color: #2d3748; font-size: 16px; margin: 0 0 5px 0;">&#x1F539; <a href="[URL_GỐC]" style="color: #2b6cb0; text-decoration: none;">[TÊN SỰ KIỆN]</a></h3>
      <p style="margin: 0; font-size: 14px;"><strong>Bản chất kỹ thuật:</strong> [Chỉ số, kiến trúc, benchmark].</p>
      <p style="margin: 5px 0 0 0; font-size: 14px;"><strong>Tại sao quan trọng:</strong> [Tác động thị trường, đối thủ, lập trình viên].</p>
    </div>
  </div>

  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; background-color: #f7fafc;">
    <h2 style="color: #2c5282; border-bottom: 2px solid #2c5282; padding-bottom: 5px; font-size: 18px;">&#x1F6E0;&#xFE0F; 2. Mô Hình Mã Nguồn Mở & Công Cụ Kỹ Thuật Đáng Chú Ý</h2>
    <ul style="padding-left: 20px; margin: 0; font-size: 14px;">
      [3-5 mục:]
      <li style="margin-bottom: 10px;"><strong><a href="[URL_GỐC]" style="color: #3182ce; text-decoration: none;">[Tên Tool/Model]</a></strong>: [Công dụng, thông số kỹ thuật, ai nên dùng].</li>
    </ul>
  </div>

  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none;">
    <h2 style="color: #276749; border-bottom: 2px solid #276749; padding-bottom: 5px; font-size: 18px;">&#x1F4CA; 3. Động Thái Thị Trường & Chiến Lược Doanh Nghiệp</h2>
    <ul style="padding-left: 20px; margin: 0; font-size: 14px;">
      [2-3 mục: M&A, đầu tư lớn, chính sách, Big Tech:]
      <li style="margin-bottom: 10px;"><strong><a href="[URL_GỐC]" style="color: #276749; text-decoration: none;">[Sự kiện]</a></strong>: [Phân tích ý nghĩa chiến lược].</li>
    </ul>
  </div>

  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; background-color: #fffbeb; border-radius: 0 0 8px 8px;">
    <h2 style="color: #dd6b20; border-bottom: 2px solid #dd6b20; padding-bottom: 5px; font-size: 18px;">&#x1F9E0; 4. CTO Insight &#8212; Dự Báo Tuần Tới</h2>
    <p style="margin: 0; font-size: 14px; font-style: italic; color: #4a5568;">[2-3 câu: xu hướng dịch chuyển, công ty/nhóm cần theo dõi, quyết định kỹ thuật đáng chú ý]</p>
  </div>

</div>
</body>
</html>
"""


def generate_report() -> str:
    client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

    print("[generate] Calling Claude API with web search...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    html_content = ""
    for block in response.content:
        if hasattr(block, "text"):
            html_content += block.text

    if not html_content.strip():
        raise ValueError("Claude returned empty response")

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
