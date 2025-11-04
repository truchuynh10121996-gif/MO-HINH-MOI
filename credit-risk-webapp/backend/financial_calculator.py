"""
Module tính toán 14 chỉ số tài chính từ báo cáo tài chính doanh nghiệp
"""

import numpy as np
import pandas as pd
from typing import Tuple

# Tên các chỉ số tài chính (14 chỉ số)
COMPUTED_COLS = [
    "Biên Lợi nhuận Gộp (X1)", "Biên Lợi nhuận Tr.Thuế (X2)", "ROA Tr.Thuế (X3)",
    "ROE Tr.Thuế (X4)", "Tỷ lệ Nợ/TTS (X5)", "Tỷ lệ Nợ/VCSH (X6)",
    "Thanh toán Hiện hành (X7)", "Thanh toán Nhanh (X8)", "Khả năng Trả lãi (X9)",
    "Khả năng Trả nợ Gốc (X10)", "Tỷ lệ Tiền/VCSH (X11)", "Vòng quay HTK (X12)",
    "Kỳ thu tiền BQ (X13)", "Hiệu suất Tài sản (X14)"
]

# Alias các dòng quan trọng trong báo cáo tài chính
ALIAS_IS = {
    "doanh_thu_thuan": ["Doanh thu thuần", "Doanh thu bán hàng", "Doanh thu thuần về bán hàng và cung cấp dịch vụ"],
    "gia_von": ["Giá vốn hàng bán"],
    "loi_nhuan_gop": ["Lợi nhuận gộp"],
    "chi_phi_lai_vay": ["Chi phí lãi vay", "Chi phí tài chính (trong đó: chi phí lãi vay)"],
    "loi_nhuan_truoc_thue": ["Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Lợi nhuận trước thuế thu nhập DN"],
}

ALIAS_BS = {
    "tong_tai_san": ["Tổng tài sản"],
    "von_chu_so_huu": ["Vốn chủ sở hữu", "Vốn CSH"],
    "no_phai_tra": ["Nợ phải trả"],
    "tai_san_ngan_han": ["Tài sản ngắn hạn"],
    "no_ngan_han": ["Nợ ngắn hạn"],
    "hang_ton_kho": ["Hàng tồn kho"],
    "tien_tdt": ["Tiền và các khoản tương đương tiền", "Tiền và tương đương tiền"],
    "phai_thu_kh": ["Phải thu ngắn hạn của khách hàng", "Phải thu khách hàng"],
    "no_dai_han_den_han": ["Nợ dài hạn đến hạn trả", "Nợ dài hạn đến hạn"],
}

ALIAS_CF = {
    "khau_hao": ["Khấu hao TSCĐ", "Khấu hao", "Chi phí khấu hao"],
}


def _pick_year_cols(df: pd.DataFrame) -> Tuple[str, str]:
    """
    Chọn 2 cột năm gần nhất từ sheet (ưu tiên cột có nhãn là năm).

    Returns:
        Tuple của (prev_year_col, current_year_col)
    """
    numeric_years = []
    for c in df.columns[1:]:
        try:
            y = int(float(str(c).strip()))
            if 1990 <= y <= 2100:
                numeric_years.append((y, c))
        except Exception:
            continue

    if numeric_years:
        numeric_years.sort(key=lambda x: x[0])
        return numeric_years[-2][1], numeric_years[-1][1]

    # fallback: 2 cột cuối
    cols = df.columns[-2:]
    return cols[0], cols[1]


def _get_row_vals(df: pd.DataFrame, aliases: list) -> Tuple[float, float]:
    """
    Tìm dòng theo alias và trả về (prev_value, current_value) theo 2 cột năm gần nhất.

    Args:
        df: DataFrame chứa dữ liệu
        aliases: List các alias để tìm kiếm

    Returns:
        Tuple của (previous_year_value, current_year_value)
    """
    label_col = df.columns[0]
    prev_col, cur_col = _pick_year_cols(df)
    mask = False

    for alias in aliases:
        mask = mask | df[label_col].astype(str).str.contains(alias, case=False, na=False)

    rows = df[mask]
    if rows.empty:
        return np.nan, np.nan

    row = rows.iloc[0]

    def to_num(x):
        try:
            # Xóa dấu phẩy, khoảng trắng
            return float(str(x).replace(",", "").replace(" ", ""))
        except Exception:
            return np.nan

    return to_num(row[prev_col]), to_num(row[cur_col])


def compute_ratios_from_three_sheets(xlsx_file) -> pd.DataFrame:
    """
    Đọc 3 sheet (CDKT/BCTN/LCTT) từ file Excel và tính toán 14 chỉ số tài chính.

    Args:
        xlsx_file: Path đến file Excel hoặc file-like object

    Returns:
        DataFrame chứa 14 chỉ số tài chính (X1-X14)
    """
    # Đọc 3 sheet từ file Excel
    bs = pd.read_excel(xlsx_file, sheet_name="CDKT", engine="openpyxl")
    is_ = pd.read_excel(xlsx_file, sheet_name="BCTN", engine="openpyxl")
    cf = pd.read_excel(xlsx_file, sheet_name="LCTT", engine="openpyxl")

    # Lấy các giá trị từ báo cáo tài chính
    DTT_prev, DTT_cur = _get_row_vals(is_, ALIAS_IS["doanh_thu_thuan"])
    GVHB_prev, GVHB_cur = _get_row_vals(is_, ALIAS_IS["gia_von"])
    LNG_prev, LNG_cur = _get_row_vals(is_, ALIAS_IS["loi_nhuan_gop"])
    LNTT_prev, LNTT_cur = _get_row_vals(is_, ALIAS_IS["loi_nhuan_truoc_thue"])
    LV_prev, LV_cur = _get_row_vals(is_, ALIAS_IS["chi_phi_lai_vay"])
    TTS_prev, TTS_cur = _get_row_vals(bs, ALIAS_BS["tong_tai_san"])
    VCSH_prev, VCSH_cur = _get_row_vals(bs, ALIAS_BS["von_chu_so_huu"])
    NPT_prev, NPT_cur = _get_row_vals(bs, ALIAS_BS["no_phai_tra"])
    TSNH_prev, TSNH_cur = _get_row_vals(bs, ALIAS_BS["tai_san_ngan_han"])
    NNH_prev, NNH_cur = _get_row_vals(bs, ALIAS_BS["no_ngan_han"])
    HTK_prev, HTK_cur = _get_row_vals(bs, ALIAS_BS["hang_ton_kho"])
    Tien_prev, Tien_cur = _get_row_vals(bs, ALIAS_BS["tien_tdt"])
    KPT_prev, KPT_cur = _get_row_vals(bs, ALIAS_BS["phai_thu_kh"])
    NDH_prev, NDH_cur = _get_row_vals(bs, ALIAS_BS["no_dai_han_den_han"])
    KH_prev, KH_cur = _get_row_vals(cf, ALIAS_CF["khau_hao"])

    # Xử lý giá trị âm (chuyển sang dương)
    if pd.notna(GVHB_cur):
        GVHB_cur = abs(GVHB_cur)
    if pd.notna(LV_cur):
        LV_cur = abs(LV_cur)
    if pd.notna(KH_cur):
        KH_cur = abs(KH_cur)

    # Hàm tính trung bình
    def avg(a, b):
        if pd.isna(a) and pd.isna(b):
            return np.nan
        if pd.isna(a):
            return b
        if pd.isna(b):
            return a
        return (a + b) / 2.0

    TTS_avg = avg(TTS_cur, TTS_prev)
    VCSH_avg = avg(VCSH_cur, VCSH_prev)
    HTK_avg = avg(HTK_cur, HTK_prev)
    KPT_avg = avg(KPT_cur, KPT_prev)

    # Tính EBIT
    EBIT_cur = (LNTT_cur + LV_cur) if (pd.notna(LNTT_cur) and pd.notna(LV_cur)) else np.nan
    NDH_cur = 0.0 if pd.isna(NDH_cur) else NDH_cur

    # Hàm chia an toàn
    def div(a, b):
        return np.nan if (b is None or pd.isna(b) or b == 0) else a / b

    # ==== TÍNH 14 CHỈ SỐ TÀI CHÍNH (X1-X14) ====
    X1 = div(LNG_cur, DTT_cur)  # Biên lợi nhuận gộp
    X2 = div(LNTT_cur, DTT_cur)  # Biên lợi nhuận trước thuế
    X3 = div(LNTT_cur, TTS_avg)  # ROA trước thuế
    X4 = div(LNTT_cur, VCSH_avg)  # ROE trước thuế
    X5 = div(NPT_cur, TTS_cur)  # Tỷ lệ nợ/Tổng tài sản
    X6 = div(NPT_cur, VCSH_cur)  # Tỷ lệ nợ/VCSH
    X7 = div(TSNH_cur, NNH_cur)  # Thanh toán hiện hành
    X8 = div((TSNH_cur - HTK_cur) if pd.notna(TSNH_cur) and pd.notna(HTK_cur) else np.nan, NNH_cur)  # Thanh toán nhanh
    X9 = div(EBIT_cur, LV_cur)  # Khả năng trả lãi
    X10 = div((EBIT_cur + (KH_cur if pd.notna(KH_cur) else 0.0)), (LV_cur + NDH_cur) if pd.notna(LV_cur) else np.nan)  # Khả năng trả nợ gốc
    X11 = div(Tien_cur, VCSH_cur)  # Tỷ lệ tiền/VCSH
    X12 = div(GVHB_cur, HTK_avg)  # Vòng quay hàng tồn kho
    turnover = div(DTT_cur, KPT_avg)
    X13 = div(365.0, turnover) if pd.notna(turnover) and turnover != 0 else np.nan  # Kỳ thu tiền bình quân
    X14 = div(DTT_cur, TTS_avg)  # Hiệu suất tài sản

    # Tạo DataFrame kết quả
    ratios = pd.DataFrame(
        [[X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11, X12, X13, X14]],
        columns=COMPUTED_COLS
    )

    # Thêm cột X_1..X_14 để phục vụ mô hình ML
    ratios[[f"X_{i}" for i in range(1, 15)]] = ratios.values

    return ratios


def classify_pd(pd_value: float) -> dict:
    """
    Phân loại xác suất vỡ nợ (PD) theo 5 cấp độ với rating và màu sắc.

    Args:
        pd_value: Xác suất vỡ nợ (0-1)

    Returns:
        dict chứa thông tin phân loại PD
    """
    if pd.isna(pd_value):
        return {
            'range': 'N/A',
            'classification': 'Không xác định',
            'rating': 'N/A',
            'meaning': 'Thiếu dữ liệu',
            'color': '#6c757d',
            'gradient_color': 'linear-gradient(135deg, #6c757d 0%, #95a5a6 100%)'
        }

    pd_percent = pd_value * 100  # Chuyển sang phần trăm

    if pd_percent < 2:
        return {
            'range': '< 2%',
            'classification': 'Rất thấp',
            'rating': 'AAA-AA',
            'meaning': 'Doanh nghiệp xuất sắc',
            'color': '#28a745',  # Green
            'gradient_color': 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
        }
    elif pd_percent < 5:
        return {
            'range': '2-5%',
            'classification': 'Thấp',
            'rating': 'A-BBB',
            'meaning': 'Doanh nghiệp tốt',
            'color': '#5cb85c',  # Light green
            'gradient_color': 'linear-gradient(135deg, #5cb85c 0%, #4cae4c 100%)'
        }
    elif pd_percent < 10:
        return {
            'range': '5-10%',
            'classification': 'Trung bình',
            'rating': 'BB',
            'meaning': 'Cần theo dõi',
            'color': '#ffc107',  # Yellow/Warning
            'gradient_color': 'linear-gradient(135deg, #ffc107 0%, #ffca2c 100%)'
        }
    elif pd_percent < 20:
        return {
            'range': '10-20%',
            'classification': 'Cao',
            'rating': 'B',
            'meaning': 'Rủi ro đáng kể',
            'color': '#fd7e14',  # Orange
            'gradient_color': 'linear-gradient(135deg, #fd7e14 0%, #ff851b 100%)'
        }
    else:  # >= 20%
        return {
            'range': '> 20%',
            'classification': 'Rất cao',
            'rating': 'CCC-D',
            'meaning': 'Nguy cơ vỡ nợ cao',
            'color': '#dc3545',  # Red
            'gradient_color': 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)'
        }
