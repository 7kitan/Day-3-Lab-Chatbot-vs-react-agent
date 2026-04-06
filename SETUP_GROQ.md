# 🚀 Cấu hình Groq LLM Provider

## Tổng quan
Groq là dịch vụ LLM serverless nhanh và chi phí thấp. Dự án của bạn đã được cấu hình để chạy bằng Groq provider.

---

## Bước 1: Tạo Groq API Key

### 1.1 Truy cập Groq Console
- Vào: https://console.groq.com/
- Đăng ký hoặc đăng nhập tài khoản

### 1.2 Lấy API Key
- Truy cập phần **API Keys**
- Nhấp **Create API Key**
- Copy API key (bắt đầu với `gsk_...`)

---

## Bước 2: Cấu hình File `.env`

Mở file `.env` ở root project và cập nhật:

```env
# GROQ SETTINGS
GROQ_API_KEY=gsk_your_api_key_here  # Thay thế bằng API key của bạn

# LAB CONFIG
DEFAULT_PROVIDER=groq              # Provider mặc định
DEFAULT_MODEL=qwen/qwen3-32b       # Model sử dụng
```

**Các model được hỗ trợ bởi Groq:**
- `qwen/qwen3-32b` (Recommended - nhanh, tốt)
- `mixtral-8x7b-32768`
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant` (nhỏ, nhanh hơn)

---

## Bước 3: Kiểm tra Cấu hình

### 3.1 Xác nhận .env được load
```bash
# Mở PowerShell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'GROQ_API_KEY: {os.getenv(\"GROQ_API_KEY\")}')"
```

### 3.2 Test Groq Provider trực tiếp
```bash
python -c "
from dotenv import load_dotenv
from src.core.groq_provider import GroqProvider
import os

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
llm = GroqProvider(api_key=api_key)
print(f'✅ GroqProvider initialized: {llm.model_name}')
result = llm.generate('Hello, what is 2+2?')
print(f'Response: {result[\"content\"]}')
"
```

---

## Bước 4: Chạy Movie Booking Agent

### Chạy test mặc định (dùng Groq)
```bash
python tests/test_movie_agent.py
```

**Output mong đợi:**
```
🎬 Movie Booking Agent - Demo

Using provider: GROQ
(agent sẽ xử lý movie search requests)
```

### Chạy với provider khác (tuỳ chọn)
```bash
# Sử dụng OpenAI thay vì Groq
python -c "
import sys; sys.path.insert(0, '.')
from tests.test_movie_agent import test_movie_agent, create_movie_agent
from dotenv import load_dotenv

load_dotenv()
import os
os.environ['DEFAULT_PROVIDER'] = 'openai'

test_movie_agent()
"
```

---

## Cấu trúc Code Groq

### GroqProvider (`src/core/groq_provider.py`)

**Khởi tạo:**
```python
from src.core.groq_provider import GroqProvider

llm = GroqProvider(
    model_name="qwen/qwen3-32b",
    api_key="your_groq_api_key"
)
```

**Gọi non-streaming:**
```python
result = llm.generate(
    prompt="Find me an action movie",
    system_prompt="You are a movie assistant"
)

print(result["content"])        # Response text
print(result["usage"])          # Token usage
print(result["latency_ms"])     # Request time
print(result["provider"])       # "groq"
```

**Gọi streaming:**
```python
for chunk in llm.stream(prompt="Find me movies..."):
    print(chunk, end="", flush=True)
```

### Kích thước đầu vào/đầu ra
- **Max input tokens**: 127,000
- **Max output tokens**: 4,096
- **Context window**: 127k

---

## Khắc phục Sự Cố

### ❌ "GROQ_API_KEY not set correctly"
**Giải pháp:**
1. Kiểm tra file `.env` có cấu hình `GROQ_API_KEY=gsk_...` chưa
2. Đảm bảo API key bắt đầu với `gsk_` (không phải `your_`)
3. Không có khoảng trắng thừa xung quanh giá trị

### ❌ "Groq API error: Rate limit exceeded"
**Giải pháp:**
- Groq có giới hạn request (free tier: ~30 request/1 phút)
- Chờ vài giây rồi thử lại
- Hoặc upgrade tài khoản Groq

### ❌ "Model not found: qwen/qwen3-32b"
**Giải pháp:**
- Kiểm tra danh sách model hiện có
- Thử model khác: `mixtral-8x7b-32768` hoặc `llama-3.1-8b-instant`
- Cập nhật `DEFAULT_MODEL` trong `.env`

### ❌ "StreamingError" khi dùng stream()
**Giải pháp:**
- Groq streaming có thể chậm khi model bận
- Thử dùng `generate()` thay vì `stream()`
- Hoặc chuyển sang model nhỏ hơn (8b thay vì 32b)

---

## So Sánh Providers

| Provider | Model | Chi phí | Tốc độ | Hỗ trợ |
|----------|-------|---------|--------|--------|
| **Groq** | Qwen/Llama/Mixtral | Rẻ | 🚀 Nhanh nhất | Tốt |
| **OpenAI** | GPT-4o | Trung bình | Trung bình | Tuyệt vời |
| **Gemini** | Gemini 1.5 | Rẻ | Trung bình | Tốt |
| **Local** | Phi-3 | Free | Chậm | Basic |

**Khuyến nghị**: Sử dụng **Groq** cho: 
- Development & testing (nhanh, rẻ)
- MVP (Minimum Viable Product)

---

## Ví dụ Chạy Groq Agent

### Full Example
```python
from dotenv import load_dotenv
from src.core.groq_provider import GroqProvider
from src.agent.agent import ReActAgent
import os

load_dotenv()

# Initialize Groq
llm = GroqProvider(
    model_name=os.getenv("DEFAULT_MODEL"),
    api_key=os.getenv("GROQ_API_KEY")
)

# Create agent with movie tools
tools = [
    {
        "name": "search_movies",
        "description": "Search movies by title"
    },
    {
        "name": "find_by_genre",
        "description": "Find movies by genre and date"
    },
    {
        "name": "get_details",
        "description": "Get movie details"
    }
]

agent = ReActAgent(llm=llm, tools=tools, max_steps=5)

# Run agent
user_request = "Find me an action movie from 2024"
response = agent.run(user_request)
print(response)
```

---

## Bổ sung: Giới hạn Groq Free Tier

- **Rate limit**: ~30 requests per minute
- **Max tokens per minute**: ~10,000
- **Prompts per day**: Không giới hạn
- **Max input**: 127,000 tokens
- **Latency**: <1s (thường 200-500ms)

Nếu vượt giới hạn, hãy:
1. Đợi 1 phút rồi thử lại
2. Giảm query complexity
3. Upgrade tài khoản

---

## References

- **Groq Docs**: https://console.groq.com/docs
- **Groq Models**: https://console.groq.com/docs/models
- **API Reference**: https://groq.com/

---

**Thành công!** 🎉 Groq đã được cấu hình đầy đủ cho dự án của bạn.
