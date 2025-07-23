import asyncio
import time
import os
import glob
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import atexit
import json
import urllib.parse
import tempfile
import aiohttp
import shutil
import threading
from typing import Dict, Set
import uuid
from urllib.parse import unquote
def load_cookies_from_file():
    """Load cookies từ file cookies.txt"""
    try:
        if os.path.exists('cookies.txt'):
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception as e:
        print(f"⚠️ Không thể đọc cookies từ file: {e}")
    
    # Fallback cookies (thay thế với cookies mặc định)
    return '''bcookie="v=2&59055992-45ae-49b7-8b4d-ae989f1e3ce9"; bscookie="v=1&20250716041527f52097cb-1711-4405-80d8-0a25b12140ffAQENpq5_NauUceviY9GMh6JONedfVlmj"; g_state={"i_l":0}; timezone=Asia/Saigon; li_theme=light; li_theme_set=app; dfpfpt=89f805bc88464607a3a64254e4f5209a; li_rm=AQHQZmLNMuwRewAAAZgR8zLuideJKH2oNvztlDNtDpjdR3kzVbKg4i8Ru2-BdwhViSnb8OLeoUc74-NO79qVZPGuTqodkdpZakYX7Dlctl9SZp4z9cMMytoG; visit=v=1&M; JSESSIONID="ajax:0136494058605229705"; li_theme_set=app; AMP_MKTG_5919ff8c0c=JTdCJTdE; li_sugr=0f5df060-f31d-4e35-ab87-763f3484c858; AnalyticsSyncHistory=AQLKOMBN6NIn_QAAAZgteQm9ytee4LgvVTMKJ36HpgXMOEynkEU6BZd8mg0UhC9ygkkn9gnSDsfG53GV0XeI4Q; lms_ads=AQGHNTHmyIzYPQAAAZgteQt7qUFb48oXHhxwp_T2E5VUR6BuPytdOtB9z1yMK7Yrqk-fx6TZMwXn_hoL84BCtm9y6kHp7wsr; lms_analytics=AQGHNTHmyIzYPQAAAZgteQt7qUFb48oXHhxwp_T2E5VUR6BuPytdOtB9z1yMK7Yrqk-fx6TZMwXn_hoL84BCtm9y6kHp7wsr; lang=v=2&lang=vi-vn; fptctx2=taBcrIH61PuCVH7eNCyH0OPzOrGnaCb%252f7mTjN%252fuIW2uYTJGYvlTMBDB09dqxDXxUnrWzQS2Wj2eUUbP4uTlLI%252fopMqjmnNTe5CkvIMqlQqRZs67SGK%252bQqWiPbD4gYk%252bkccCL%252fvSJmHZ%252fkJpNcUXuSzf1W2hLbpocoaCRgsRud36c9aECrfZzdrJiIx2Sq5xWkH07jd2DlwGMWd7feouBvzB%252fEhUZuutnz192fefSgauZdWh3LJ2kacOo2jLRtNcf%252bBl2k9wHA79tBWa2e9CSxBwaNbls0PAHde9kQKTCYwAbMDp0SzHPGy37wQlnA8M0Y99E66WPJJcZ761hO5anP5HrVLnFTkkLa1ZgGx8OiUo%253d; __cf_bm=ucgWBpVhJJ2I7zN1s4cFqC_Oyha3Q.WDNLRFTsfJx_M-1753195923-1.0.1.1-0npEKiwHuA7IJlC3uXHVMcJUBwfn6LdRmghiG_mpTv.siiC47biOuGBz5H4hjqbvtleRFQTHJs6DpooqSOf2A0DQBf_5m9UORSZwd5bCsQI; li_at=AQEDAVwUbPsESvsyAAABmDKe8IwAAAGYVqt0jE4AeyBlGZHPScfvl5Hr3mq3sKQHyi0fCwDiwlfOWxm7hD6HnsMUCX76BfPyz6kACRvpVNF4qWtm-OybbP0TaSq-e3Ys3v0PeKJo0hkz56yLloVmERS2; liap=true; lidc="b=TB91:s=T:r=T:a=T:p=T:g=6092:u=3:x=1:i=1753195934:t=1753196824:v=2:sig=AQGieR1NPeZ6eqd28_bgU2j5s8aqT3ry"; AMP_5919ff8c0c=JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjI1OTcyZTY1ZS0zMDU3LTRkMTctOWMxMy0yYWUwMGMwYTMyY2QlMjIlMkMlMjJzZXNzaW9uSWQlMjIlM0ExNzUzMDc4NDg1NTMyJTJDJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJsYXN0RXZlbnRUaW1lJTIyJTNBMTc1MzA3ODQ4NTczNiUyQyUyMmxhc3RFdmVudElkJTIyJTNBMSU3RA==; UserMatchHistory=AQJ0PSRFRfxhCAAAAZgynv3x50OyQtUST3Ee7GJdzzzckiXrMdCHbEHJAnRXGTn5I0jEN4N1C242X-PT5Fp4mLRSGSVSm1eisBu-zRFbyA7L6i1HcJm79AZge10DpdxzvNE-T0F9GNIp8btPrL0nCobXyEnp8chsixd4o9sEWcW1rQM0RUclVi8FR7-RSn3kiEdho1ONr-XjSOfwWJ7akDoMaE6jPBDoEFnyMZ2fNGbOFhc6pxNgFUiT1yKw9CltvlTPw1WO80FCjdMKWrpb3aA4pZw-3k9cGOtwqhP4cFaE5VBdV85TkW_Wf9afS2jmHVwaLzj9w0f4nvCc6_nI8ewQ7X5N7oNIrjd9SXuiYPpotdgFIA; _dd_s=logs=1&id=e081bf57-cca7-4306-9719-a0ff33e17834&created=1753195923777&expire=1753196836895'''
LINKEDIN_COOKIES =  load_cookies_from_file()
app = FastAPI()

# Global Playwright instances
playwright_instance = None
browser: Browser = None
context: BrowserContext = None
active_tasks: Dict[str, bool] = {}  # Track active tasks by ID
task_pages: Dict[str, Page] = {}  # Map task ID to page
class LinkedInRequest(BaseModel):
    profile_url: str
    password: str
    new_cookie: str    
class TaskManager:
    def __init__(self):
        self.active_tasks: Set[str] = set()
        self.lock = threading.Lock()
    
    def add_task(self, task_id: str) -> bool:
        with self.lock:
            self.active_tasks.add(task_id)
            return True
    
    def remove_task(self, task_id: str):
        with self.lock:
            self.active_tasks.discard(task_id)
    
    def is_busy(self) -> bool:
        with self.lock:
            return len(self.active_tasks) > 0
    
    def get_task_count(self) -> int:
        with self.lock:
            return len(self.active_tasks)

task_manager = TaskManager()

async def setup_playwright():
    """Setup Playwright với persistent context và download directory"""
    global playwright_instance, browser, context
    
    if browser is not None:
        return browser, context
    
    # Tạo thư mục profile riêng
    profile_path = os.path.join(os.getcwd(), "playwright_profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    
    # Tạo thư mục download tạm
    download_path = os.path.join(os.getcwd(), "temp_downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    playwright_instance = await async_playwright().start()
    
    # Launch browser với persistent context
    browser = await playwright_instance.chromium.launch_persistent_context(
        user_data_dir=profile_path,
        headless=True,
        args=[
            '--start-maximized',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor'
        ],
        downloads_path=download_path,
        accept_downloads=True,
        ignore_https_errors=True,
    )
    
    context = browser
    
    # Tạo page đầu tiên để set cookies
    page = await context.new_page()
    
    # Navigate to LinkedIn và set cookies
    await page.goto("https://www.linkedin.com")
    
    # Parse và set cookies
    cookies = []
    for cookie in LINKEDIN_COOKIES.split('; '):
        try:
            name, value = cookie.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.linkedin.com',
                'path': '/'
            })
        except:
            continue
    
    await context.add_cookies(cookies)
    
    # Refresh để apply cookies
    await page.reload()
    
    print("✅ Playwright đã khởi động với cookies LinkedIn và download directory.")
    
    return browser, context

async def cleanup_playwright():
    """Cleanup function để close browser khi server stops"""
    global playwright_instance, browser, context
    
    if browser:
        await browser.close()
        browser = None
        context = None
        
    if playwright_instance:
        await playwright_instance.stop()
        playwright_instance = None
        
    print("✅ Playwright đã được đóng.")

def cleanup_temp_files():
    """Dọn dẹp thư mục temp downloads"""
    download_path = os.path.join(os.getcwd(), "temp_downloads")
    if os.path.exists(download_path):
        try:
            shutil.rmtree(download_path)
            os.makedirs(download_path)
            print("✅ Đã dọn dẹp thư mục temp downloads.")
        except Exception as e:
            print(f"⚠️ Không thể dọn dẹp temp downloads: {e}")

# Setup browser khi server starts
@app.on_event("startup")
async def startup_event():
    await setup_playwright()

@app.on_event("shutdown") 
async def shutdown_event():
    await cleanup_playwright()
    cleanup_temp_files()
async def find_pdf_button_with_javascript(page, timeout=5):
    js_script = """
    () => {
        return new Promise(async (resolve) => {
            const selectors = [
                '[aria-label*="PDF"]',
                '[aria-label*="Lưu thành bản PDF"]',
                '[data-tracking-control-name="public_profile_topcard_save_to_pdf"]',
                'button[aria-label*="Save to PDF"]',
                'a[aria-label*="Save to PDF"]',
                '.artdeco-dropdown__item--is-dropdown button',
                '.pv-s-profile-actions button',
                '.pv-top-card-v2-ctas button'
            ];

            let foundButton = null;

            for (let selector of selectors) {
                const elements = document.querySelectorAll(selector);
                for (let element of elements) {
                    const text = element.textContent || element.getAttribute('aria-label') || '';
                    if (text.toLowerCase().includes('pdf') || 
                        text.toLowerCase().includes('save') || 
                        element.getAttribute('data-tracking-control-name') === 'public_profile_topcard_save_to_pdf') {
                        foundButton = element;
                        break;
                    }
                }
                if (foundButton) break;
            }

            if (!foundButton) {
                const moreButton = document.querySelector('[aria-label*="More actions"]') || 
                                  document.querySelector('.artdeco-dropdown__trigger');
                if (moreButton) {
                    moreButton.click();
                    await new Promise(resolve => setTimeout(resolve, 300));
                    const dropdownItems = document.querySelectorAll('.artdeco-dropdown__item button, .artdeco-dropdown__item a');
                    for (let item of dropdownItems) {
                        const text = item.textContent || item.getAttribute('aria-label') || '';
                        if (text.toLowerCase().includes('pdf')) {
                            foundButton = item;
                            break;
                        }
                    }
                }
            }

            if (foundButton) {
                foundButton.style.display = 'block';
                foundButton.style.visibility = 'visible';
                foundButton.style.opacity = '1';
                foundButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
                foundButton.click();
                resolve(true);
            } else {
                resolve(false);
            }
        });
    }
    """

    try:
        result = await asyncio.wait_for(page.evaluate(js_script), timeout=timeout)
        return result
    except asyncio.TimeoutError:
        print("❌ Hết thời gian chờ tìm và click nút PDF")
        return False
    except Exception as e:
        print(f"❌ Lỗi JavaScript: {str(e)}")
        return False


async def wait_for_download_complete(download_path, timeout=20000):
    """Đợi file download hoàn thành"""
    start_time = time.time()
    
    while (time.time() - start_time) * 1000 < timeout:
        # Tìm file PDF mới nhất
        pdf_files = glob.glob(os.path.join(download_path, "*.pdf"))
        
        # Kiểm tra file .crdownload (Chrome downloading)
        temp_files = glob.glob(os.path.join(download_path, "*.crdownload"))
        temp_files.extend(glob.glob(os.path.join(download_path, "*.tmp")))
        
        if pdf_files and not temp_files:
            # Có file PDF và không có file đang download
            latest_file = max(pdf_files, key=os.path.getctime)
            
            # Kiểm tra file size stable
            try:
                size1 = os.path.getsize(latest_file)
                await asyncio.sleep(1)
                size2 = os.path.getsize(latest_file)
                
                if size1 == size2 and size1 > 0:
                    return latest_file
            except:
                pass
        
        await asyncio.sleep(0.5)
    
    return None


def generate_filename_from_url(profile_url):
    """Tạo tên file từ LinkedIn profile URL"""
    try:
        # Extract username/company từ URL
        if '/in/' in profile_url:
            username = profile_url.split('/in/')[-1].split('/')[0]
            return f"linkedin_profile_{username}.pdf"
        elif '/company/' in profile_url:
            company = profile_url.split('/company/')[-1].split('/')[0]
            return f"linkedin_company_{company}.pdf"
        else:
            # Fallback
            import hashlib
            url_hash = hashlib.md5(profile_url.encode()).hexdigest()[:8]
            return f"linkedin_profile_{url_hash}.pdf"
    except:
        return "linkedin_profile.pdf"

async def process_single_linkedin(page: Page, profile_url: str, task_id: str, download_path: str):
    """Xử lý một LinkedIn profile duy nhất với page đã có sẵn"""
    try:
        print(f"🔍 [Task {task_id}] Truy cập: {profile_url}")
        await page.goto(profile_url, timeout=30000)
   
        print(f"⏳ [Task {task_id}] Đang tìm & click nút PDF...")

        clicked = False
        for i in range(20):  # Thử tối đa 20 lần, mỗi lần cách nhau 250ms
            clicked = await find_pdf_button_with_javascript(page, timeout=5)
            if clicked:
                print(f"✅ [Task {task_id}] Click nút PDF thành công ở lần thử thứ {i + 1}")
                break
            else:
                print(f"🔁 [Task {task_id}] Thử click lần {i + 1} không thành công, chờ 250ms...")
                await page.wait_for_timeout(250)

        if not clicked:
            raise HTTPException(status_code=404, detail="Không tìm thấy hoặc không click được nút PDF sau nhiều lần thử.")

        # Chờ sự kiện download xảy ra
        try:
            download = await page.wait_for_event("download", timeout=15000)
        except:
            raise HTTPException(status_code=408, detail="Không có file nào được tải xuống.")

        # Tạo tên file và lưu
        timestamp = int(time.time() * 1000)
        filename = f"linkedin_{task_id}_{timestamp}.pdf"
        file_path = os.path.join(download_path, filename)

        await download.save_as(file_path)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="File PDF không tồn tại sau khi tải.")

        print(f"✅ [Task {task_id}] Tải thành công: {file_path}")
        return file_path

    except Exception as e:
        print(f"❌ [Task {task_id}] Lỗi: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")

async def process_linkedin_pdf(profile_url: str, task_id: str):
    """Quản lý việc xử lý LinkedIn PDF với tab chờ sẵn để tối ưu hiệu suất"""
    global context
    download_path = os.path.join(os.getcwd(), "temp_downloads")
    os.makedirs(download_path, exist_ok=True)

    page = None

    try:
        if context is None:
            await setup_playwright()

        # Tạo page mới cho task này
        page = await context.new_page()
        task_pages[task_id] = page

        # Xử lý LinkedIn profile
        file_path = await process_single_linkedin(page, profile_url, task_id, download_path)
        
        return file_path

    except Exception as e:
        print(f"❌ [Task {task_id}] Lỗi process_linkedin_pdf: {str(e)}")
        raise e

    finally:
        # Đóng tab của task này nhưng giữ lại context và browser
        if page and not page.is_closed():
            await page.close()
            print(f"🗂️ [Task {task_id}] Đã đóng tab, giữ lại browser để tái sử dụng")
        
        # Xóa task khỏi danh sách pages
        if task_id in task_pages:
            del task_pages[task_id]


@app.post("/get-linkedin-pdf")
async def get_linkedin_pdf(request: LinkedInRequest, background_tasks: BackgroundTasks):
    """Main endpoint để lấy LinkedIn PDF với multi-tab support"""
    
    # Tạo task ID unique
    task_id = str(uuid.uuid4())[:8]
    
    try:
        # Add task to manager
        task_manager.add_task(task_id)
        
        print(f"🚀 [Task {task_id}] Bắt đầu xử lý LinkedIn PDF")
        print(f"📊 Số task đang chạy: {task_manager.get_task_count()}")
        
        # Process PDF
        downloaded_file = await process_linkedin_pdf(request.profile_url, task_id)
        
        # Tạo tên file phù hợp từ URL
        suggested_filename = generate_filename_from_url(request.profile_url)
        
        # Schedule cleanup task
        def cleanup_file():
            try:
                time.sleep(3)  # Wait a bit before cleanup
                if os.path.exists(downloaded_file):
                    os.remove(downloaded_file)
                    print(f"✅ [Task {task_id}] Đã xóa file tạm: {downloaded_file}")
            except Exception as e:
                print(f"⚠️ [Task {task_id}] Không thể xóa file tạm: {e}")
            finally:
                task_manager.remove_task(task_id)
        
        background_tasks.add_task(cleanup_file)
        
        # Trả về file
        return FileResponse(
            path=downloaded_file,
            filename=suggested_filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        task_manager.remove_task(task_id)
        raise
    except Exception as e:
        task_manager.remove_task(task_id)
        print(f"❌ [Task {task_id}] Lỗi: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")

@app.post("/restart-browser/{admin_key}")
async def restart_browser(admin_key: str):
    """
    Cập nhật cookie từ URL raw và khởi động lại trình duyệt
    """
    global LINKEDIN_COOKIES, browser, context
    ADMIN_PASSWORD = "dungsigma"
    if admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="❌ Sai mật khẩu admin")

    raw_cookie_url = "https://raw.githubusercontent.com/dungviet224/dungviet224/refs/heads/main/cc"

    try:
        # Tải cookie từ link GitHub
        async with aiohttp.ClientSession() as session:
            async with session.get(raw_cookie_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=500, detail="❌ Không thể tải cookie từ GitHub")

                new_cookie = await response.text()
                new_cookie = new_cookie.strip()

        # Ghi vào file
        with open("cookies.txt", "w", encoding="utf-8") as f:
            f.write(new_cookie)

        # Cập nhật biến toàn cục
        LINKEDIN_COOKIES = new_cookie

        # Đóng browser cũ
        if browser:
            await browser.close()
            browser = None
            context = None

        # Khởi động lại
        await setup_playwright()

        return {"message": "✅ Cookie đã được cập nhật từ GitHub và Chrome đã khởi động lại"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Lỗi khi restart: {str(e)}")
@app.get("/")
async def root():
    return {
        "message": "LinkedIn PDF API với Playwright đang chạy", 
        "status": "Multi-tab + Auto cleanup + Optimized performance", 
        "features": [
            "Sử dụng Playwright thay vì Selenium",
            "Chạy song song nhiều task với tabs riêng biệt",
            "Tự động download PDF file",
            "Trả về file PDF trực tiếp",
            "Tự động xóa file tạm sau khi gửi",
            "Support tên file từ LinkedIn URL",
            "Tối ưu tốc độ phản hồi và hiệu suất"
        ],
        "current_tasks": task_manager.get_task_count(),
        "usage": "POST /get-linkedin-pdf với profile_url", 
        "docs": "/docs"
    }

@app.get("/get-linkedin-pdf/{profile_url:path}")
async def get_linkedin_pdf_get(profile_url: str, background_tasks: BackgroundTasks):
    """GET endpoint cho tiện - decode URL"""
    decoded_url = urllib.parse.unquote(profile_url)
    if not decoded_url.startswith('http'):
        decoded_url = 'https://' + decoded_url
    
    request = LinkedInRequest(profile_url=decoded_url)
    return await get_linkedin_pdf(request, background_tasks)

@app.post("/test-pdf-button")
async def test_pdf_button(request: LinkedInRequest):
    """Test endpoint để kiểm tra các JavaScript functions"""
    global context
    task_id = str(uuid.uuid4())[:8]
    
    try:
        if context is None:
            await setup_playwright()
        
        page = await context.new_page()
        await page.goto(request.profile_url, wait_until="networkidle")
        await page.wait_for_timeout(1500)
        
        button = await find_pdf_button_with_javascript(page)
        
        if button:
            # Get button info using JavaScript
            button_info = await page.evaluate("""
                () => {
                    const selectors = [
                        '[aria-label*="PDF"]',
                        '[data-tracking-control-name="public_profile_topcard_save_to_pdf"]'
                    ];
                    
                    for (let selector of selectors) {
                        const button = document.querySelector(selector);
                        if (button) {
                            return {
                                tagName: button.tagName,
                                text: button.textContent,
                                ariaLabel: button.getAttribute('aria-label'),
                                className: button.className,
                                visible: button.offsetParent !== null,
                                style: button.style.cssText
                            };
                        }
                    }
                    return null;
                }
            """)
            
            await page.close()
            
            return {
                "found": True,
                "button_info": button_info,
                "message": "Đã tìm thấy nút PDF bằng JavaScript",
                "task_id": task_id
            }
        else:
            await page.close()
            return {
                "found": False,
                "message": "Không tìm thấy nút PDF",
                "task_id": task_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi test: {str(e)}")

@app.get("/status")
async def get_status():
    """Endpoint để kiểm tra status của các task đang chạy"""
    return {
        "active_tasks": task_manager.get_task_count(),
        "is_busy": task_manager.is_busy(),
        "browser_ready": browser is not None,
        "context_ready": context is not None,
        "active_pages": len(task_pages)
    }

@app.get("/cleanup")
async def manual_cleanup():
    """Endpoint để dọn dẹp thủ công"""
    download_path = os.path.join(os.getcwd(), "temp_downloads")
    cleaned_files = 0
    
    try:
        if os.path.exists(download_path):
            for file_path in glob.glob(os.path.join(download_path, "*")):
                try:
                    os.remove(file_path)
                    cleaned_files += 1
                except Exception as e:
                    print(f"Không thể xóa {file_path}: {e}")
        
        return {
            "message": f"Đã dọn dẹp {cleaned_files} file(s)",
            "download_path": download_path,
            "active_tasks_after_cleanup": task_manager.get_task_count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cleanup: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Setup cleanup khi script ends
    def cleanup_on_exit():
        asyncio.run(cleanup_playwright())
        cleanup_temp_files()
    
    atexit.register(cleanup_on_exit)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
