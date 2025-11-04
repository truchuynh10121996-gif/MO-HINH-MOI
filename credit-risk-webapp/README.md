# 🏦 Credit Risk Assessment System - Website Version

Hệ thống đánh giá rủi ro tín dụng doanh nghiệp với AI phân tích chuyên sâu - Phiên bản Website độc lập.

## ✨ Tính Năng

### 🎯 Tính năng chính:
- ✅ **Upload báo cáo tài chính Excel** (3 sheets: CDKT, BCTN, LCTT)
- ✅ **Tính toán tự động 14 chỉ số tài chính**
- ✅ **Dự đoán xác suất vỡ nợ (PD)** với 4 mô hình ML:
  - Logistic Regression
  - Random Forest
  - XGBoost
  - Stacking Ensemble
- ✅ **Phân loại PD theo 5 cấp độ** (AAA-D)
- ✅ **Phân tích AI chuyên sâu** bằng Google Gemini
- ✅ **Chat AI Assistant** - Trợ lý tư vấn tín dụng
- ✅ **Trực quan hóa dữ liệu** (Bar Chart, Radar Chart)
- ✅ **Xuất báo cáo Word** chuyên nghiệp
- ✅ **Dashboard**:
  - Tin tức tài chính từ RSS feeds
  - Dữ liệu vĩ mô nền kinh tế
  - Phân tích ngành chi tiết

### 🚀 Cải tiến so với bản Streamlit:
- ⚡ **Hiệu suất cao hơn** - FastAPI backend với async processing
- 🎨 **Giao diện đẹp và mượt mà** - Bootstrap 5 + Custom CSS
- 📱 **Responsive** - Tương thích mọi thiết bị
- 🔥 **Interactive** - Charts động với Chart.js
- 🌐 **Deploy dễ dàng** - Chạy trên mọi web server

## 📁 Cấu Trúc Project

```
credit-risk-webapp/
├── backend/                    # FastAPI Backend
│   ├── main.py                # API endpoints chính
│   ├── financial_calculator.py # Tính toán 14 chỉ số tài chính
│   ├── ai_services.py         # Gemini AI integration
│   ├── ml_models.py           # Machine Learning models
│   ├── report_generator.py    # Tạo báo cáo Word
│   ├── rss_service.py         # RSS feeds handler
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Frontend
│   ├── index.html             # Trang phân tích chính
│   ├── dashboard.html         # Trang dashboard
│   ├── css/
│   │   └── style.css         # Custom CSS
│   ├── js/
│   │   ├── main.js           # JavaScript chính
│   │   └── dashboard.js      # JavaScript dashboard
│   └── assets/               # Hình ảnh, logo
│
├── data/
│   └── DATASET.csv           # Dữ liệu training
│
└── README.md                  # File này
```

## 🛠️ Cài Đặt & Chạy

### Yêu Cầu Hệ Thống:
- Python 3.8+
- pip
- (Tùy chọn) Virtual environment

### Bước 1: Clone/Navigate to Project
```bash
cd /path/to/credit-risk-webapp
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)
```bash
python -m venv venv

# Trên Linux/Mac:
source venv/bin/activate

# Trên Windows:
venv\Scripts\activate
```

### Bước 3: Cài Đặt Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Bước 4: Cấu Hình API Key (Tùy chọn)

Tạo file `.env` trong thư mục `backend/`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**Lưu ý:** Nếu không cấu hình API key trong file `.env`, bạn có thể nhập trực tiếp trên giao diện web.

### Bước 5: Chạy Server

```bash
# Từ thư mục backend/
python main.py
```

Hoặc dùng uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Bước 6: Truy Cập Website

Mở trình duyệt và truy cập:
- **Trang chính**: http://localhost:8000/static/index.html
- **Dashboard**: http://localhost:8000/static/dashboard.html
- **API Docs**: http://localhost:8000/docs (Swagger UI)

## 📖 Hướng Dẫn Sử Dụng

### 1️⃣ Phân Tích Rủi Ro Tín Dụng

1. **Upload File Excel**:
   - File phải có 3 sheets: `CDKT` (Cân đối kế toán), `BCTN` (Báo cáo thu nhập), `LCTT` (Lưu chuyển tiền tệ)
   - Kéo thả file hoặc click để chọn

2. **Phân Tích**:
   - Click nút **"Phân tích"**
   - Hệ thống tự động:
     - Tính 14 chỉ số tài chính
     - Dự đoán PD với 4 models
     - Hiển thị kết quả và biểu đồ

3. **AI Phân Tích** (Tùy chọn):
   - Click **"AI Phân tích"** để nhận khuyến nghị từ Gemini AI
   - AI sẽ đưa ra khuyến nghị: **CHO VAY** hoặc **KHÔNG CHO VAY**

4. **Tải Báo Cáo**:
   - Click **"Tải Báo Cáo"** để xuất file Word chuyên nghiệp

5. **Chat với AI**:
   - Sử dụng chat box để hỏi thêm về phân tích
   - AI sẽ trả lời dựa trên context của dữ liệu hiện tại

### 2️⃣ Sử Dụng Dashboard

1. **Tin Tức Tài Chính**:
   - Xem tin tức tự động cập nhật từ CafeF, Vietstock, Báo Đầu tư, VNExpress
   - Click **"Làm mới"** để cập nhật

2. **Dữ Liệu Vĩ Mô**:
   - Click **"Lấy Dữ Liệu Vĩ Mô"**
   - Xem các chỉ số: GDP, lãi suất, NPL, thất nghiệp

3. **Phân Tích Ngành**:
   - Chọn ngành từ dropdown
   - Click **"Phân tích"**
   - Xem dữ liệu và biểu đồ ngành

## 🔧 API Endpoints

Backend cung cấp các RESTful API sau:

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/` | GET | Root endpoint |
| `/api/health` | GET | Health check |
| `/api/upload-financial-report` | POST | Upload & phân tích file Excel |
| `/api/analyze-with-ai` | POST | Phân tích bằng AI |
| `/api/chat` | POST | Chat với AI |
| `/api/generate-report` | POST | Tạo báo cáo Word |
| `/api/rss-feeds` | GET | Lấy RSS feeds |
| `/api/industry-data` | POST | Lấy dữ liệu ngành |
| `/api/macro-data` | GET | Lấy dữ liệu vĩ mô |

**Xem API docs đầy đủ tại**: http://localhost:8000/docs

## 🧪 Testing

Test các endpoints:
```bash
# Health check
curl http://localhost:8000/api/health

# Get RSS feeds
curl http://localhost:8000/api/rss-feeds
```

## 🚀 Deploy Production

### Sử dụng Gunicorn (Khuyến nghị cho production):
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000
```

### Sử dụng Docker:
```dockerfile
FROM python:3.9

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Sử dụng Nginx reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/credit-risk-webapp/frontend;
    }
}
```

## 📊 14 Chỉ Số Tài Chính

| Chỉ số | Ký hiệu | Công thức |
|--------|---------|-----------|
| Biên Lợi nhuận Gộp | X1 | LNG / DTT |
| Biên Lợi nhuận Tr.Thuế | X2 | LNTT / DTT |
| ROA Tr.Thuế | X3 | LNTT / TTS_avg |
| ROE Tr.Thuế | X4 | LNTT / VCSH_avg |
| Tỷ lệ Nợ/TTS | X5 | NPT / TTS |
| Tỷ lệ Nợ/VCSH | X6 | NPT / VCSH |
| Thanh toán Hiện hành | X7 | TSNH / NNH |
| Thanh toán Nhanh | X8 | (TSNH - HTK) / NNH |
| Khả năng Trả lãi | X9 | EBIT / LV |
| Khả năng Trả nợ Gốc | X10 | (EBIT + KH) / (LV + NDH) |
| Tỷ lệ Tiền/VCSH | X11 | Tiền / VCSH |
| Vòng quay HTK | X12 | GVHB / HTK_avg |
| Kỳ thu tiền BQ | X13 | 365 / (DTT / KPT_avg) |
| Hiệu suất Tài sản | X14 | DTT / TTS_avg |

## 🤖 Công Nghệ Sử Dụng

### Backend:
- **FastAPI** - Modern Python web framework
- **Scikit-learn** - Machine Learning
- **XGBoost** - Gradient Boosting
- **Google Gemini AI** - AI analysis
- **python-docx** - Word report generation
- **feedparser** - RSS feeds
- **pandas, numpy** - Data processing

### Frontend:
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive charts
- **Font Awesome** - Icons

## 📝 Lưu Ý Quan Trọng

1. **Gemini API Key**:
   - Cần API key từ Google AI Studio: https://makersuite.google.com/app/apikey
   - Có thể cấu hình trong file `.env` hoặc nhập trên UI

2. **Dữ liệu Training**:
   - File `DATASET.csv` cần có sẵn trong thư mục `data/`
   - Models sẽ tự động train khi khởi động lần đầu

3. **Format File Excel**:
   - Phải có đủ 3 sheets: CDKT, BCTN, LCTT
   - Định dạng giống file mẫu của bản Streamlit

4. **CORS**:
   - Trong production, nên cấu hình `allow_origins` cụ thể thay vì `"*"`

## 🆘 Troubleshooting

### Lỗi khi cài đặt dependencies:
```bash
# Nâng cấp pip
pip install --upgrade pip

# Cài từng package nếu có lỗi
pip install fastapi uvicorn pandas scikit-learn xgboost google-genai
```

### Models không train được:
- Kiểm tra file `DATASET.csv` có tồn tại
- Kiểm tra file có đủ cột `default` và `X_1` đến `X_14`

### Gemini API không hoạt động:
- Kiểm tra API key đúng
- Kiểm tra kết nối internet
- Kiểm tra quota API key

### Port 8000 đã được sử dụng:
```bash
# Chạy trên port khác
uvicorn main:app --port 8080
```

## 📧 Liên Hệ & Hỗ Trợ

- **Email**: support@creditrisk.com
- **GitHub Issues**: [Link to issues]
- **Documentation**: http://localhost:8000/docs

## 📜 License

Copyright © 2024 Credit Risk Assessment System. All rights reserved.

---

**Phát triển bởi**: Nhóm Ánh Sáng Số
**Phiên bản**: 2.0.0 Premium
**Ngày cập nhật**: 2024

🎉 **Chúc bạn sử dụng hệ thống thành công!**
