"""
Module tích hợp Gemini AI cho phân tích tín dụng và dữ liệu ngành
"""

import json
import re
from datetime import datetime
from typing import Optional
import pandas as pd

# Import Gemini SDK
try:
    from google import genai
    from google.genai.errors import APIError
    GEMINI_OK = True
except Exception:
    genai = None
    APIError = Exception
    GEMINI_OK = False

MODEL_NAME = "gemini-2.5-flash"


def get_ai_analysis(data_payload: dict, api_key: str) -> str:
    """
    Sử dụng Gemini API để phân tích chỉ số tài chính và đưa ra khuyến nghị cho vay.

    Args:
        data_payload: Dict chứa 14 chỉ số tài chính và PD
        api_key: API key của Gemini

    Returns:
        str: Phân tích từ AI
    """
    if not GEMINI_OK:
        return "Lỗi: Thiếu thư viện google-genai (cần cài đặt: pip install google-genai)."

    client = genai.Client(api_key=api_key)

    sys_prompt = (
        "Bạn là chuyên gia phân tích tín dụng doanh nghiệp tại ngân hàng Việt Nam. "
        "Phân tích toàn diện dựa trên 14 chỉ số tài chính được cung cấp và PD (chủ yếu là PD cuối cùng của mô hình Stacking). "
        "Lưu ý PD trong mô hình này được tính theo bối cảnh doanh nghiệp Việt Nam. "
        "Nêu rõ: (1) Khả năng sinh lời, (2) Thanh khoản, (3) Cơ cấu nợ, (4) Hiệu quả hoạt động. "
        "Kết thúc bằng khuyến nghị in hoa: CHO VAY hoặc KHÔNG CHO VAY, kèm 2–3 điều kiện nếu CHO VAY. "
        "Viết bằng tiếng Việt súc tích, chuyên nghiệp."
    )

    user_prompt = "Bộ chỉ số tài chính và PD cần phân tích:\n" + str(data_payload) + "\n\nHãy phân tích và đưa ra khuyến nghị."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}
            ],
            config={"system_instruction": sys_prompt}
        )
        return response.text
    except APIError as e:
        return f"Lỗi gọi API Gemini: {e}"
    except Exception as e:
        return f"Lỗi không xác định: {e}"


def chat_with_gemini(user_message: str, api_key: str, context_data: dict = None) -> str:
    """
    Chatbot với Gemini AI để trả lời câu hỏi về phân tích tín dụng.

    Args:
        user_message: Câu hỏi từ người dùng
        api_key: API key của Gemini
        context_data: Dữ liệu ngữ cảnh (chỉ số tài chính, PD, phân tích trước đó)

    Returns:
        str: Câu trả lời từ Gemini AI
    """
    if not GEMINI_OK:
        return "Lỗi: Thiếu thư viện google-genai (cần cài đặt: pip install google-genai)."

    client = genai.Client(api_key=api_key)

    sys_prompt = (
        "Bạn là chuyên gia tư vấn tín dụng doanh nghiệp tại ngân hàng. "
        "Nhiệm vụ của bạn là trả lời các câu hỏi của người dùng về phân tích tín dụng một cách chuyên nghiệp, "
        "dựa trên dữ liệu tài chính và phân tích đã được cung cấp. "
        "Trả lời súc tích, rõ ràng, dễ hiểu bằng tiếng Việt. "
        "Nếu cần, đưa ra các khuyến nghị hoặc giải thích chi tiết về các chỉ số tài chính."
    )

    # Tạo context prompt nếu có dữ liệu
    context_prompt = ""
    if context_data:
        context_prompt = "\n\nDữ liệu ngữ cảnh:\n" + str(context_data)

    full_prompt = user_message + context_prompt

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": full_prompt}]}
            ],
            config={"system_instruction": sys_prompt}
        )
        return response.text
    except APIError as e:
        return f"Lỗi gọi API Gemini: {e}"
    except Exception as e:
        return f"Lỗi không xác định: {e}"


def get_industry_data_from_ai(api_key: str, industry_name: str) -> Optional[dict]:
    """
    Lấy dữ liệu ngành cụ thể từ Gemini API.

    Args:
        api_key: API key của Gemini
        industry_name: Tên ngành (VD: "Nông nghiệp", "Sản xuất", "Bất động sản"...)

    Returns:
        dict chứa dữ liệu ngành và phân tích, hoặc None nếu lỗi
    """
    if not GEMINI_OK:
        return None

    try:
        client = genai.Client(api_key=api_key)

        sys_prompt = """Bạn là chuyên gia phân tích kinh tế và dữ liệu ngành tại Việt Nam.
        Nhiệm vụ của bạn là cung cấp dữ liệu thống kê và phân tích về một ngành cụ thể."""

        user_prompt = f"""Hãy cung cấp dữ liệu và phân tích cho ngành **{industry_name}** tại Việt Nam trong 3 năm gần nhất.

        Trả về dữ liệu dưới dạng JSON với cấu trúc sau (CHỈ TRẢ VỀ JSON, KHÔNG GIẢI THÍCH):
        {{
            "industry_name": "{industry_name}",
            "revenue_growth_quarterly": {{
                "quarters": ["Q1-2022", "Q2-2022", ...],
                "growth_rate": [2.5, 3.1, ...]
            }},
            "avg_gross_margin_3y": 25.5,
            "avg_net_profit_margin": 8.3,
            "avg_debt_to_equity": 1.2,
            "pmi_monthly": {{
                "months": ["2024-01", "2024-02", ...],
                "pmi": [52.3, 51.8, ...]
            }},
            "new_vs_closed_businesses": {{
                "quarters": ["Q1-2022", "Q2-2022", ...],
                "new": [1200, 1350, ...],
                "closed": [450, 380, ...]
            }},
            "analysis": "Phân tích sơ bộ về tình hình ngành..."
        }}"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[{"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}],
            config={"system_instruction": sys_prompt}
        )

        response_text = response.text.strip()
        # Parse JSON từ response (có thể chứa markdown code block)
        if "```json" in response_text:
            response_text = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL).group(1)
        elif "```" in response_text:
            response_text = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL).group(1)

        data = json.loads(response_text)
        return data

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu ngành từ AI: {e}")
        return None


def get_macro_data_from_ai(api_key: str) -> Optional[dict]:
    """
    Lấy dữ liệu vĩ mô nền kinh tế Việt Nam từ Gemini API.

    Args:
        api_key: API key của Gemini

    Returns:
        dict chứa dữ liệu vĩ mô và phân tích, hoặc None nếu lỗi
    """
    if not GEMINI_OK:
        return None

    try:
        client = genai.Client(api_key=api_key)

        sys_prompt = """Bạn là chuyên gia kinh tế vĩ mô Việt Nam.
        Nhiệm vụ của bạn là cung cấp dữ liệu vĩ mô quan trọng của nền kinh tế."""

        user_prompt = """Hãy cung cấp dữ liệu vĩ mô nền kinh tế Việt Nam trong 3-5 năm gần nhất.

        Trả về dữ liệu dưới dạng JSON với cấu trúc sau (CHỈ TRẢ VỀ JSON, KHÔNG GIẢI THÍCH):
        {
            "lending_rate_vs_interbank": {
                "quarters": ["Q1-2020", "Q2-2020", ...],
                "lending_rate": [8.5, 8.3, ...],
                "interbank_rate": [4.2, 4.0, ...]
            },
            "gdp_growth": {
                "quarters": ["Q1-2020", "Q2-2020", ...],
                "growth_rate": [3.7, 2.1, 6.7, 7.0, ...]
            },
            "unemployment_rate": {
                "years": ["2020", "2021", "2022", "2023", "2024"],
                "rate": [2.3, 2.5, 2.3, 2.2, 2.1]
            },
            "npl_ratio": {
                "quarters": ["Q1-2022", "Q2-2022", ...],
                "npl_rate": [1.9, 2.0, 2.1, ...],
                "default_rate": [0.5, 0.6, ...]
            },
            "financial_stress_index": {
                "months": ["2023-01", "2023-02", ...],
                "fsi": [0.3, 0.4, 0.2, ...]
            },
            "analysis": "Phân tích tổng quan về tình hình kinh tế vĩ mô..."
        }"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[{"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}],
            config={"system_instruction": sys_prompt}
        )

        response_text = response.text.strip()
        # Parse JSON từ response
        if "```json" in response_text:
            response_text = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL).group(1)
        elif "```" in response_text:
            response_text = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL).group(1)

        data = json.loads(response_text)
        return data

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu vĩ mô từ AI: {e}")
        return None


def get_financial_data_from_ai(api_key: str) -> Optional[pd.DataFrame]:
    """
    Tự động lấy dữ liệu tài chính doanh nghiệp Việt Nam từ Gemini API.

    Args:
        api_key: API key của Gemini

    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu tài chính theo quý, hoặc None nếu lỗi
    """
    if not GEMINI_OK:
        return None

    try:
        client = genai.Client(api_key=api_key)

        # Lấy quý hiện tại
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        current_quarter = (current_month - 1) // 3 + 1

        sys_prompt = """Bạn là chuyên gia kinh tế và dữ liệu thống kê về doanh nghiệp Việt Nam.
        Hãy cung cấp dữ liệu tài chính tổng hợp của khu vực doanh nghiệp Việt Nam theo quý,
        dựa trên các nguồn thống kê đáng tin cậy như GSO (Tổng cục Thống kê Việt Nam),
        Bộ Kế hoạch và Đầu tư, hoặc các báo cáo kinh tế vĩ mô.

        Trả về dữ liệu dưới dạng JSON với cấu trúc sau:
        {
            "quarters": ["Q1-2021", "Q2-2021", ...],
            "revenue": [số liệu doanh thu tỷ VNĐ, ...],
            "assets": [số liệu tổng tài sản tỷ VNĐ, ...],
            "profit": [số liệu lợi nhuận tỷ VNĐ, ...],
            "debt": [số liệu nợ phải trả tỷ VNĐ, ...],
            "equity": [số liệu VCSH tỷ VNĐ, ...]
        }

        Chỉ trả về JSON, không giải thích thêm."""

        user_prompt = f"""Hãy cung cấp dữ liệu tài chính tổng hợp của khu vực doanh nghiệp Việt Nam
        từ quý Q1-2021 đến quý Q{current_quarter}-{current_year}.

        Bao gồm các chỉ số:
        - Doanh thu (Revenue) - tổng doanh thu khu vực doanh nghiệp, đơn vị tỷ VNĐ
        - Tổng tài sản (Total Assets) - tổng tài sản khu vực doanh nghiệp, đơn vị tỷ VNĐ
        - Lợi nhuận (Profit) - lợi nhuận sau thuế, đơn vị tỷ VNĐ
        - Nợ phải trả (Debt) - tổng nợ phải trả, đơn vị tỷ VNĐ
        - Vốn chủ sở hữu (Equity/VCSH) - tổng VCSH, đơn vị tỷ VNĐ

        Dữ liệu phải phản ánh xu hướng tăng trưởng thực tế của nền kinh tế Việt Nam.
        Chỉ trả về JSON thuần, không markdown, không giải thích."""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "user", "parts": [{"text": sys_prompt + "\n\n" + user_prompt}]}
            ],
            config={"system_instruction": sys_prompt}
        )

        response_text = response.text.strip()
        # Parse JSON từ response
        if "```json" in response_text:
            response_text = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL).group(1)
        elif "```" in response_text:
            response_text = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL).group(1)

        data = json.loads(response_text)

        # Chuyển thành DataFrame
        df = pd.DataFrame({
            'Quarter': data['quarters'],
            'Revenue': data['revenue'],
            'Assets': data['assets'],
            'Profit': data['profit'],
            'Debt': data['debt'],
            'Equity': data['equity']
        })

        return df

    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu tài chính từ AI: {e}")
        return None
