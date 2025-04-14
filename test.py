import asyncio
import httpx
import time

# آدرس‌های API
FASTAPI_URL = "http://127.0.0.1:8000/api/auth/login/"
DRF_URL = "http://127.0.0.1:8000/api/login/"

# تعداد درخواست‌ها
NUM_REQUESTS = 40 # تعداد درخواست‌ها را بیشتر کنیم برای تست بار بیشتر

# داده تستی
test_data = {
    "phone_or_email": "test@example.com",
    "password": "Test1234"
}

# تابع ارسال درخواست به صورت غیرهمزمان
async def send_request_async(client, url):
    start_time = time.time()
    response = await client.post(url, json=test_data)
    elapsed_time = time.time() - start_time
    return elapsed_time, response.status_code

# تابع benchmark برای تست FastAPI به صورت غیرهمزمان
async def benchmark_async(url):
    async with httpx.AsyncClient(timeout=httpx.Timeout(2000.0)) as client:  # تایم‌اوت 30 ثانیه
        tasks = [send_request_async(client, url) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)  # ارسال درخواست‌ها همزمان
    
    response_times = [res[0] for res in results]
    avg_time = sum(response_times) / NUM_REQUESTS
    success_count = sum(1 for _, status in results if status == 200)

    return avg_time, success_count

# تابع benchmark برای تست DRF به صورت غیرهمزمان
async def benchmark_drf_async(url):
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:  # تایم‌اوت 30 ثانیه
        tasks = [send_request_async(client, url) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
    
    response_times = [res[0] for res in results]
    avg_time = sum(response_times) / NUM_REQUESTS
    success_count = sum(1 for _, status in results if status == 200)

    return avg_time, success_count

async def main():
    print("Testing FastAPI (Ninja - Async)...")
    fastapi_time, fastapi_success = await benchmark_async(FASTAPI_URL)
    print(f"FastAPI Avg Response Time: {fastapi_time:.4f}s, Success: {fastapi_success}/{NUM_REQUESTS}")

    print("\nTesting DRF (Async)...")  # تغییر نام به DRF Async
    drf_time, drf_success = await benchmark_drf_async(DRF_URL)  # استفاده از benchmark_drf_async
    print(f"DRF Avg Response Time: {drf_time:.4f}s, Success: {drf_success}/{NUM_REQUESTS}")

    print("\nComparison:")
    if fastapi_time < drf_time:
        print(f"FastAPI is {drf_time / fastapi_time:.2f}x faster than DRF")
    else:
        print(f"DRF is {fastapi_time / drf_time:.2f}x faster than FastAPI")

# اجرای main
asyncio.run(main())
