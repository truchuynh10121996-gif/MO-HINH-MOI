"""
FastAPI Backend cho Credit Risk Assessment System
"""

import os
import io
import base64
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import numpy as np

# Import các modules
from financial_calculator import compute_ratios_from_three_sheets, classify_pd, COMPUTED_COLS
from ai_services import (
    get_ai_analysis,
    chat_with_gemini,
    get_industry_data_from_ai,
    get_macro_data_from_ai,
    get_financial_data_from_ai
)
from ml_models import get_models_instance
from report_generator import generate_word_report
from rss_service import get_all_rss_feeds

# Khởi tạo FastAPI app
app = FastAPI(
    title="Credit Risk Assessment API",
    description="API cho hệ thống đánh giá rủi ro tín dụng doanh nghiệp",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên chỉ định cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Khởi tạo models
models = get_models_instance()
MODELS_DIR = os.path.join(os.path.dirname(__file__), "trained_models")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# API Key từ environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


# ===========================
# Pydantic Models
# ===========================

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class IndustryRequest(BaseModel):
    industry_name: str


# ===========================
# Startup Event
# ===========================

@app.on_event("startup")
async def startup_event():
    """Train hoặc load models khi khởi động"""
    try:
        # Thử load models đã train
        if models.load_models(MODELS_DIR):
            print("✅ Đã load models từ file")
        else:
            # Train mới nếu chưa có
            print("🔄 Đang train models...")
            dataset_path = os.path.join(DATA_DIR, "DATASET.csv")
            if os.path.exists(dataset_path):
                metrics = models.train_models(dataset_path)
                models.save_models(MODELS_DIR)
                print("✅ Train models thành công!")
                print("📊 Metrics:", metrics)
            else:
                print("⚠️ Không tìm thấy dataset để train")
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo models: {e}")


# ===========================
# API Endpoints
# ===========================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Credit Risk Assessment API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_trained": models.is_trained
    }


@app.post("/api/upload-financial-report")
async def upload_financial_report(file: UploadFile = File(...)):
    """
    Upload file Excel báo cáo tài chính và tính toán 14 chỉ số.
    File phải có 3 sheets: CDKT, BCTN, LCTT
    """
    try:
        # Kiểm tra file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File phải là Excel (.xlsx hoặc .xls)")

        # Đọc file
        contents = await file.read()
        excel_file = io.BytesIO(contents)

        # Tính toán 14 chỉ số tài chính
        ratios_df = compute_ratios_from_three_sheets(excel_file)

        # Dự đoán PD với các models
        predictions = models.predict(ratios_df)

        # Chuẩn bị ratios để hiển thị
        ratios_display = ratios_df[COMPUTED_COLS].T
        ratios_display.columns = ['Giá trị']

        # Phân loại PD từ model Stacking
        pd_value = predictions['Stacking']['pd']
        pd_classification = classify_pd(pd_value)

        # Chuyển ratios_display thành dict
        ratios_dict = {}
        for idx, row in ratios_display.iterrows():
            ratios_dict[idx] = float(row['Giá trị']) if pd.notna(row['Giá trị']) else None

        return {
            "success": True,
            "ratios": ratios_dict,
            "predictions": predictions,
            "pd_classification": pd_classification,
            "message": "Tính toán thành công!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý file: {str(e)}")


@app.post("/api/analyze-with-ai")
async def analyze_with_ai(
    ratios: dict,
    predictions: dict,
    api_key: Optional[str] = Form(None)
):
    """
    Phân tích chỉ số tài chính và PD bằng Gemini AI
    """
    try:
        # Sử dụng API key từ request hoặc từ env
        key = api_key or GEMINI_API_KEY
        if not key:
            raise HTTPException(status_code=400, detail="Thiếu Gemini API key")

        # Tạo payload cho AI
        data_payload = {
            "ratios": ratios,
            "predictions": predictions
        }

        # Gọi AI analysis
        analysis = get_ai_analysis(data_payload, key)

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích AI: {str(e)}")


@app.post("/api/chat")
async def chat(request: ChatRequest, api_key: Optional[str] = Form(None)):
    """Chatbot với Gemini AI"""
    try:
        key = api_key or GEMINI_API_KEY
        if not key:
            raise HTTPException(status_code=400, detail="Thiếu Gemini API key")

        response = chat_with_gemini(request.message, key, request.context)

        return {
            "success": True,
            "response": response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi chat: {str(e)}")


@app.post("/api/generate-report")
async def generate_report(
    ratios: dict,
    pd_value: float,
    pd_label: str,
    ai_analysis: str = "",
    company_name: str = "KHÁCH HÀNG DOANH NGHIỆP"
):
    """
    Tạo báo cáo Word từ kết quả phân tích
    """
    try:
        # Chuyển ratios dict thành DataFrame
        ratios_display = pd.DataFrame.from_dict(ratios, orient='index', columns=['Giá trị'])

        # Tạo visualizations
        fig_bar, fig_radar = create_visualizations(ratios)

        # Generate Word report
        buffer = generate_word_report(
            ratios_display=ratios_display,
            pd_value=pd_value,
            pd_label=pd_label,
            ai_analysis=ai_analysis,
            fig_bar=fig_bar,
            fig_radar=fig_radar,
            company_name=company_name,
            logo_path=os.path.join(FRONTEND_DIR, "assets", "logo-agribank.jpg")
        )

        # Close figures
        plt.close(fig_bar)
        plt.close(fig_radar)

        # Return as downloadable file
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=Credit_Risk_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo báo cáo: {str(e)}")


@app.get("/api/rss-feeds")
async def get_rss_feeds():
    """Lấy RSS feeds từ các nguồn tin tài chính"""
    try:
        feeds = get_all_rss_feeds()
        return {
            "success": True,
            "feeds": feeds,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy RSS feeds: {str(e)}")


@app.post("/api/industry-data")
async def get_industry_data(request: IndustryRequest, api_key: Optional[str] = Form(None)):
    """Lấy dữ liệu ngành từ Gemini AI"""
    try:
        key = api_key or GEMINI_API_KEY
        if not key:
            raise HTTPException(status_code=400, detail="Thiếu Gemini API key")

        data = get_industry_data_from_ai(key, request.industry_name)

        if data is None:
            raise HTTPException(status_code=500, detail="Không thể lấy dữ liệu ngành")

        return {
            "success": True,
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu ngành: {str(e)}")


@app.get("/api/macro-data")
async def get_macro_data(api_key: Optional[str] = None):
    """Lấy dữ liệu vĩ mô từ Gemini AI"""
    try:
        key = api_key or GEMINI_API_KEY
        if not key:
            raise HTTPException(status_code=400, detail="Thiếu Gemini API key")

        data = get_macro_data_from_ai(key)

        if data is None:
            raise HTTPException(status_code=500, detail="Không thể lấy dữ liệu vĩ mô")

        return {
            "success": True,
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy dữ liệu vĩ mô: {str(e)}")


@app.get("/api/visualizations")
async def get_visualizations(ratios: dict):
    """Tạo và trả về visualizations dưới dạng base64"""
    try:
        fig_bar, fig_radar = create_visualizations(ratios)

        # Convert to base64
        bar_buffer = io.BytesIO()
        fig_bar.savefig(bar_buffer, format='png', dpi=100, bbox_inches='tight')
        bar_buffer.seek(0)
        bar_base64 = base64.b64encode(bar_buffer.read()).decode()

        radar_buffer = io.BytesIO()
        fig_radar.savefig(radar_buffer, format='png', dpi=100, bbox_inches='tight')
        radar_buffer.seek(0)
        radar_base64 = base64.b64encode(radar_buffer.read()).decode()

        plt.close(fig_bar)
        plt.close(fig_radar)

        return {
            "success": True,
            "bar_chart": f"data:image/png;base64,{bar_base64}",
            "radar_chart": f"data:image/png;base64,{radar_base64}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo visualizations: {str(e)}")


# ===========================
# Helper Functions
# ===========================

def create_visualizations(ratios: dict):
    """Tạo bar chart và radar chart từ ratios"""

    # Bar Chart
    fig_bar, ax_bar = plt.subplots(figsize=(12, 6))
    fig_bar.patch.set_facecolor('#fff5f7')
    ax_bar.set_facecolor('#ffffff')

    labels = list(ratios.keys())
    values = [v if v is not None else 0 for v in ratios.values()]

    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(labels)))
    bars = ax_bar.bar(labels, values, color=colors, edgecolor='black', linewidth=0.8)

    ax_bar.set_xlabel('Chỉ số Tài chính', fontsize=14, fontweight='bold')
    ax_bar.set_ylabel('Giá trị', fontsize=14, fontweight='bold')
    ax_bar.set_title('Biểu đồ Cột - 14 Chỉ số Tài chính', fontsize=16, fontweight='bold', color='#c2185b')
    ax_bar.grid(True, alpha=0.3, linestyle='--', axis='y')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    # Radar Chart
    fig_radar = plt.figure(figsize=(10, 10))
    fig_radar.patch.set_facecolor('#fff5f7')
    ax_radar = fig_radar.add_subplot(111, polar=True)

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values_radar = values + [values[0]]  # Close the loop
    angles += angles[:1]

    ax_radar.plot(angles, values_radar, 'o-', linewidth=2, color='#ff6b9d', label='Giá trị')
    ax_radar.fill(angles, values_radar, alpha=0.25, color='#ff6b9d')
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(labels, fontsize=10)
    ax_radar.set_title('Biểu đồ Radar - Phân tích Đa chiều', fontsize=16, fontweight='bold', color='#c2185b', pad=20)
    ax_radar.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    plt.tight_layout()

    return fig_bar, fig_radar


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
