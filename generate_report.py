"""
Weekly AI & Tech Intelligence Report Generator
Uses Google Gemini API (free tier) with built-in Google Search.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

SYSTEM_PROMPT = """
Bạn là Hệ thống Trí tuệ Chiến lược Công nghệ cấp cao (Global Tech Intelligence Agent), vận hành với tư duy của một CTO kiêm Venture Capitalist hàng đầu trong lĩnh vực AI và Bán dẫn.

Nhiệm vụ: Thu thập tin tức AI và công nghệ toàn cầu trong 7 ngày qua, lọc và phân tích, xuất ra HTML báo cáo hoàn chỉnh.

KỸ NĂNG CỐT LÕI:
1. Semantic Clustering: Gom nhóm các bài viết nói về cùng sự kiện thành một chủ đề duy nhất.
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
Hãy dùng Google Search để tìm kiếm tin tức AI và công nghệ trong 7 ngày qua từ các nguồn: TechCrunch, The Verge, Ars Technica, VentureBeat, ArXiv, Hugging Face Blog.

Tìm kiếm các chủ đề:
- Mô hình AI mới ra mắt với benchmark cụ thể
- Open source LLM đáng chú ý
- Phần cứng AI / chip bán dẫn thế hệ mới
- M&A, đầu tư lớn trong lĩnh vực AI
- Đột phá kiến trúc mô hình (MoE, context window, agentic)
- Chính sách AI từ EU, Mỹ, Trung Quốc

Sau khi thu thập, lọc bỏ: quảng cáo, gọi vốn seed không đột phá, tin lặp (gom thành 1 mục).

Trả về CHỈ mã HTML hoàn chỉnh (không giải thích, không markdown), theo đúng template sau:

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
      <p style="margin: 0; font-size: 14px;"><strong>Bản chất kỹ thuật:</strong> [Chỉ số, kiến trúc, benchmark cụ thể].</p>
      <p style="margin: 5px 0 0 0; font-size: 14px;"><strong>Tại sao quan trọng:</strong> [Tác động thị trường, đối thủ, lập trình viên].</p>
    </div>
  </div>

  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none; background-color: #f7fafc;">
    <h2 style="color: #2c5282; border-bottom: 2px solid #2c5282; padding-bottom: 5px; font-size: 18px;">&#x1F6E0;&#xFE0F; 2. Mô Hình Mã Nguồn Mở & Công Cụ Kỹ Thuật Đáng Chú Ý</h2>
    <ul style="padding-left: 20px; margin: 0; font-size: 14px;">
      <li style="margin-bottom: 10px;"><strong><a href="[URL_GỐC]" style="color: #3182ce; text-decoration: none;">[Tên Tool/Model]</a></strong>: [Công dụng, thông số kỹ thuật, ai nên dùng].</li>
    </ul>
  </div>

  <div style="padding: 20px; border: 1px solid #e2e8f0; border-top: none;">
    <h2 style="color: #276749; border-bottom: 2px solid #276749; padding-bottom: 5px; font-size: 18px;">&#x1F4CA; 3. Động Thái Thị Trường & Chiến Lược Doanh Nghiệp</h2>
    <ul style="padding-left: 20px; margin: 0; font-size: 14px;">
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
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    print("[generate] Calling Gemini API with Google Search...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=USER_PROMPT,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.3,
        ),
    )

    html_content = response.text
    if not html_content or not html_content.strip():
        raise ValueError("Gemini returned empty response")

    # Strip markdown code fences if model added them
    if html_content.strip().startswith("```"):
        lines = html_content.strip().splitlines()
        html_content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

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
