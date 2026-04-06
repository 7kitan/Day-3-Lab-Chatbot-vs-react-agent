# 🎬 Movie Booking Agent - Setup Guide

## Tổng quan
Đây là ReAct Agent giúp người dùng tìm kiếm vé xem phim dựa trên:
- **Tên phim** (search by title)
- **Loại phim** (search by genre)
- **Ngày phát hành** (search by release date)

Agent sẽ xử lý request thông qua TheMovieDB API.

---

## Thiết lập môi trường

### 1. Chuẩn bị API Key
Agent hỗ trợ 2 provider LLM:

#### **OpenAI (Recommended)**
- Lấy API key từ: https://platform.openai.com/api-keys
- Set vào `.env`:
  ```
  OPENAI_API_KEY=your_openai_api_key_here
  ```

#### **Google Gemini**
- Lấy API key từ: https://makersuite.google.com/app/apikey
- Set vào `.env`:
  ```
  GEMINI_API_KEY=your_gemini_api_key_here
  ```

### 2. Cấu hình .env
Copy từ `.env.example` hoặc tạo `.env` mới:
```bash
# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Optional: Local model path
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
```

### 3. Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

---

## Cấu trúc Code

### `src/core/movie_api.py`
- **MovieAPI class**: Wrapper cho TheMovieDB API
- **Phương thức chính**:
  - `search_movies(query, year)`: Tìm phim theo tên
  - `get_movies_by_genre(genre_id, release_date)`: Tìm phim theo thể loại
  - `get_movie_details(movie_id)`: Lấy chi tiết phim

### `src/agent/agent.py`
- **ReActAgent class**: Agent chính theo mô hình ReAct
- **Vòng lặp logic**:
  1. Nhận user input
  2. Gọi LLM để sinh ra Thought + Action
  3. Parse Action string
  4. Gọi tool tương ứng
  5. Append kết quả (Observation) vào prompt
  6. Lặp lại cho đến khi có Final Answer

### `tests/test_movie_agent.py`
- Test script demo với 3 câu query mẫu

---

## Sử dụng

### Chạy Demo
```bash
python tests/test_movie_agent.py
```

**Output mong đợi**:
```
🎬 Movie Booking Agent - Demo

User: Find me a scary movie released on 2024-01-15
------
Agent: [Thought process]
[Action: search_movies(...)]
[Observation: list of horror movies]
Final Answer: Based on your request, here are some great horror movies...
```

### Sử dụng trong Code
```python
from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent

# Initialize provider
llm = OpenAIProvider(api_key="your_key")

# Define tools
tools = [
    {
        "name": "search_movies",
        "description": "Search movies by title"
    },
    {
        "name": "find_by_genre",
        "description": "Find movies by genre"
    },
    {
        "name": "get_details",
        "description": "Get movie details"
    }
]

# Create agent
agent = ReActAgent(llm=llm, tools=tools, max_steps=5)

# Run with user input
result = agent.run("Find me a romantic movie from 2024")
print(result)
```

---

## TheMovieDB API Details

### Endpoints được sử dụng
1. **Search**: `GET /3/search/movie`
   - Params: `query`, `year` (optional)

2. **Discover**: `GET /3/discover/movie`
   - Params: `with_genres`, `primary_release_date.gte/lte`

3. **Movie Details**: `GET /3/movie/{movie_id}`
   - Trả về chi tiết phim, rating, runtime, etc.

### API Key
- Key được cấu hình: `79eb5f868743610d9bddd40d274eb15d`
- Lưu ý: Không bao giờ commit API key vào git!

---

## ReAct Loop Flow

```
┌─────────────────────────────────────┐
│   User Input (search request)       │
└────────────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────────┐
        │  LLM Generate      │
    ┌─▶ │ (System Prompt) ◀──┤
    │   └─────────────────────┘
    │            │
    │            ▼
    │   ┌──────────────────────┐
    │   │ Parse Thought/Action │
    │   └──────────────────────┘
    │            │
    │            ▼
    │   ┌──────────────────────┐
    │   │  Execute Tool        │
    │   │  (API Call)          │
    │   └──────────────────────┘
    │            │
    │            ▼
    │   ┌──────────────────────┐
    │   │  Observation         │
    │   │  (Tool Result)       │
    │   └──────────────────────┘
    │            │
    │   ┌────────┴──────────┐
    │   │                   │
    └───┤ Final Answer?     │
        │ (No → Loop back)  │
        │ (Yes → Exit)      │
        └─────────┬─────────┘
                  │
                  ▼
          ┌──────────────────┐
          │  Return Answer   │
          │  to User         │
          └──────────────────┘
```

---

## Khắc phục sự cố

### ❌ "OPENAI_API_KEY not found"
- Kiểm tra file `.env` có tồn tại và có đúng key không
- Chắc chắn key không bị expire

### ❌ "No module named requests"
- Chạy: `pip install requests`

### ❌ "MovieAPI - Connection error"
- Kiểm tra internet connection
- Kiểm tra TheMovieDB API có hoạt động không

### ❌ "LLM returned invalid action"
- Điều chỉnh system prompt trong `agent.py`
- Cân nhắc sử dụng model khác (gpt-4o tốt hơn gpt-3.5)

---

## Mở rộng Agent

### Thêm Tool mới
1. Thêm phương thức trong `MovieAPI` class
2. Thêm case mới trong `_execute_tool()`
3. Cập nhật tools list trong test/main script

### Ví dụ - Thêm "Book Ticket" tool
```python
# Trong movie_api.py
def book_ticket(self, movie_id: int, date: str, time: str, seats: int):
    # Integration với booking system
    pass

# Trong agent.py _execute_tool()
elif tool_name == "book_ticket":
    # Parse arguments và gọi movie_api.book_ticket()
    pass
```

---

**Tác giả**: AI Assistant  
**Ngày**: 2026-04-06  
**Version**: 1.0
