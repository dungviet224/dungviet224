import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
import time
import json
import threading
from datetime import datetime
import os
import random
import pandas as pd
import re
from urllib.parse import parse_qs, urlparse

CHROME_ARGUMENTS = [
    "-no-first-run",
    "-force-color-profile=srgb",
    "-metrics-recording-only",
    "-password-store=basic",
    "-use-mock-keychain",
    "-export-tagged-pdf",
    "-no-default-browser-check",
    "-disable-background-mode",
    "-enable-features=NetworkService,NetworkServiceInProcess",
    "-disable-features=FlashDeprecationWarning",
    "-deny-permission-prompts",
    "-disable-gpu",
    "-accept-lang=en-US",
    "--disable-usage-stats",
    "--disable-crash-reporter",
    "--no-sandbox"
]



class LinkedInScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LinkedIn Profile Scraper - Tìm kiếm Profile LinkedIn")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.driver = None
        self.drission_driver = None
        self.recaptcha_solver = None
        self.is_scraping = False
        self.results = []
        self.found_links = set()  # Set để lưu các link đã tìm thấy, tránh trùng lặp
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="LinkedIn Profile Scraper", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input fields frame
        input_frame = ttk.LabelFrame(main_frame, text="Cài đặt tìm kiếm", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Search URL
        ttk.Label(input_frame, text="Search URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.search_url_var = tk.StringVar(value='https://www.google.com/search?q="Java Developer" -intitle:"profiles" -inurl:"dir/+" site:vn.linkedin.com/in/ OR site:vn.linkedin.com/pub/')
        self.search_url_entry = ttk.Entry(input_frame, textvariable=self.search_url_var, width=80)
        self.search_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Delay
        ttk.Label(input_frame, text="Delay (giây):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.delay_var = tk.StringVar(value="3")
        delay_entry = ttk.Entry(input_frame, textvariable=self.delay_var, width=10)
        delay_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Number of links
        ttk.Label(input_frame, text="Số link cần tìm:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.max_links_var = tk.StringVar(value="50")
        max_links_entry = ttk.Entry(input_frame, textvariable=self.max_links_var, width=10)
        max_links_entry.grid(row=2, column=1, sticky=tk.W, pady=(10, 0))
        
        # Headless checkbox
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(input_frame, text="Chạy ẩn (Headless) (lỗi giải capcha) ", variable=self.headless_var)
        headless_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Bắt đầu tìm kiếm", 
                                      command=self.start_scraping, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Dừng lại", 
                                     command=self.stop_scraping, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="Xuất JSON", 
                                       command=self.export_json)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # New Excel export button
        self.export_excel_button = ttk.Button(button_frame, text="Xuất Excel", 
                                             command=self.export_excel)
        self.export_excel_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Xóa kết quả", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Sẵn sàng để bắt đầu...")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        main_frame.rowconfigure(5, weight=1)
        
        # Log area
        log_frame = ttk.LabelFrame(results_frame, text="Log hoạt động", padding="5")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=40)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results table
        table_frame = ttk.LabelFrame(results_frame, text="Kết quả tìm kiếm", padding="5")
        table_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview for results
        columns = ('STT', 'Tên', 'Link')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.results_tree.heading('STT', text='STT')
        self.results_tree.heading('Tên', text='Tên')
        self.results_tree.heading('Link', text='Link LinkedIn')
        
        # Configure column widths
        self.results_tree.column('STT', width=50, anchor='center')
        self.results_tree.column('Tên', width=200)
        self.results_tree.column('Link', width=300)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double click to copy link
        self.results_tree.bind('<Double-1>', self.copy_link)
        
        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    def generate_excel_filename(self, search_keyword=""):
        """Tạo tên file Excel từ từ khóa tìm kiếm"""
        if search_keyword:
            # Trích xuất từ khóa từ search URL
            keyword = self.extract_keyword_from_url(search_keyword)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            return f"LinkedIn_{keyword}_{timestamp}.xlsx"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            return f"LinkedIn_Profiles_{timestamp}.xlsx"
    
    def extract_keyword_from_url(self, url):
        """Trích xuất từ khóa từ URL tìm kiếm"""
        try:
            # Parse URL để lấy query parameters
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            if 'q' in query_params:
                query = query_params['q'][0]
                # Tìm từ khóa trong dấu ngoặc kép
                match = re.search(r'"([^"]*)"', query)
                if match:
                    keyword = match.group(1)
                    # Làm sạch tên file
                    keyword = re.sub(r'[^\w\s-]', '', keyword)
                    keyword = re.sub(r'[-\s]+', '_', keyword)
                    return keyword
            
            return "Search"
        except:
            return "Search"

    def export_excel(self):
        """Export results to Excel file directly"""
        if not self.results:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        # Generate filename from search keyword
        search_keyword = self.search_url_var.get()
        default_filename = self.generate_excel_filename(search_keyword)
            
        file_path = filedialog.asksaveasfilename(
            initialfilename=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Lưu file Excel"
        )
        
        if file_path:
            try:
                df = pd.DataFrame(self.results)
                df.index = df.index + 1  # Bắt đầu từ 1
                df.index.name = 'STT'
                
                # Đổi tên cột
                df.columns = ['Tên', 'Link LinkedIn']
                
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='LinkedIn Profiles', index=True)
                    
                    # Format worksheet
                    worksheet = writer.sheets['LinkedIn Profiles']
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                self.log_message(f"Đã xuất {len(self.results)} kết quả ra file Excel: {file_path}")
                messagebox.showinfo("Thành công", f"Đã xuất {len(self.results)} kết quả ra file Excel")
                
            except Exception as e:
                self.log_message(f"Lỗi khi xuất file Excel: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể xuất file Excel: {str(e)}")        
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Update status bar and progress label"""
        self.status_var.set(message)
        self.progress_var.set(message)
        self.root.update_idletasks()
        
    def add_result_to_table(self, name, link):
        """Add a result to the table"""
        index = len(self.results) + 1
        self.results_tree.insert('', tk.END, values=(index, name, link))
        self.results.append({"name": name, "link": link})
        
    def copy_link(self, event):
        """Copy selected link to clipboard"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            link = item['values'][2]  # Link is in column 2
            self.root.clipboard_clear()
            self.root.clipboard_append(link)
            self.log_message(f"Đã copy link: {link}")
    
    def setup_stealth_options(self):
        """Cài đặt các option để tránh bị phát hiện"""
        options = uc.ChromeOptions()
        
        # Các option cơ bản
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        
        # Thêm các option để tránh captcha
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # Headless mode
        if self.headless_var.get():
            options.add_argument("--headless")
        
        # User agent ngẫu nhiên
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        return options
    
    def setup_drission_options(self):
        """Setup DrissionPage options"""
        options = ChromiumOptions()
        
        # Add arguments from CHROME_ARGUMENTS
        for argument in CHROME_ARGUMENTS:
            options.set_argument(argument)
            
        # Headless mode
        if self.headless_var.get():
            options.set_argument("--headless")
            
        return options
    
    def get_random_delay(self, base_delay):
        """Tạo delay ngẫu nhiên để tránh bị phát hiện"""
        return base_delay + random.uniform(1, 3)
    
    def handle_captcha(self):
        """Handle captcha trực tiếp trên session hiện tại"""
        try:
            self.log_message("Phát hiện captcha, đang giải...")
            self.update_status("Đang giải captcha...")
            
            # Tạo DrissionPage driver kết nối với session hiện tại
            if not self.drission_driver:
                # Lấy thông tin debug port từ selenium driver
                chrome_options = self.driver.options
                debug_port = None
                
                # Tìm debug port trong chrome options
                for arg in chrome_options.arguments:
                    if arg.startswith('--remote-debugging-port='):
                        debug_port = arg.split('=')[1]
                        break
                
                # Nếu không có debug port, sử dụng cách khác
                if not debug_port:
                    debug_port = "9222"  # Port mặc định
                
                # Kết nối DrissionPage với Chrome instance hiện tại
                options = ChromiumOptions()
                options.set_local_port(int(debug_port))
                
                try:
                    self.drission_driver = ChromiumPage(addr_or_opts=options)
                    # Điều hướng đến cùng URL với selenium driver
                    self.drission_driver.get(self.driver.current_url)
                    self.recaptcha_solver = RecaptchaSolver(self.drission_driver)
                except Exception as e:
                    self.log_message(f"Không thể kết nối DrissionPage: {str(e)}")
                    # Fallback: Tạo DrissionPage mới với cùng options
                    drission_options = self.setup_drission_options()
                    self.drission_driver = ChromiumPage(addr_or_opts=drission_options)
                    self.drission_driver.get(self.driver.current_url)
                    self.recaptcha_solver = RecaptchaSolver(self.drission_driver)
            
            # Giải captcha trực tiếp
            t0 = time.time()
            self.recaptcha_solver.solveCaptcha()
            solve_time = time.time() - t0
            
            self.log_message(f"Đã giải captcha trong {solve_time:.2f} giây")
            self.update_status("Captcha đã được giải, đang tiếp tục...")
            
            # Refresh selenium driver để đồng bộ
            self.driver.refresh()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.log_message(f"Lỗi khi giải captcha: {str(e)}")
            return True

            
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if self.is_scraping:
            return
            
        # Validate inputs
        try:
            delay = float(self.delay_var.get())
            max_links = int(self.max_links_var.get())
            search_url = self.search_url_var.get().strip()
            
            if not search_url:
                messagebox.showerror("Lỗi", "Vui lòng nhập Search URL")
                return
                
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ cho Delay và Số link")
            return
            
        self.is_scraping = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start(10)
        
        # Start scraping in separate thread
        self.scrape_thread = threading.Thread(target=self.scrape_profiles, 
                                             args=(search_url, delay, max_links))
        self.scrape_thread.daemon = True
        self.scrape_thread.start()
        
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_scraping = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        if self.drission_driver:
            try:
                self.drission_driver.quit()
            except:
                pass
        self.update_status("Đã dừng tìm kiếm")
        self.log_message("Người dùng dừng quá trình tìm kiếm")
        self.reset_ui_after_scraping()
        
    def reset_ui_after_scraping(self):
        """Reset UI elements after scraping is complete"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.is_scraping = False
        
    def scrape_profiles(self, search_url, delay, max_links):
        """Main scraping function"""
        try:
            self.log_message("Bắt đầu khởi tạo Chrome driver...")
            self.update_status("Đang khởi tạo trình duyệt...")
            
            # Setup Chrome options với stealth mode
            options = self.setup_stealth_options()
            
            self.driver = uc.Chrome(options=options)
            
            # Thêm các script để tránh bị phát hiện
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.log_message("Chrome driver đã khởi tạo thành công")
            
            current_results = 0
            page = 1
            
            while current_results < max_links and self.is_scraping:
                try:
                    # Navigate to search URL
                    if page == 1:
                        current_url = search_url
                    else:
                        # Add page parameter for pagination
                        separator = "&" if "?" in search_url else "?"
                        current_url = f"{search_url}{separator}start={10 * (page - 1)}"
                    
                    self.log_message(f"Đang truy cập trang {page}...")
                    self.update_status(f"Đang tải trang {page} (Tìm thấy: {current_results}/{max_links})")
                    
                    self.driver.get(current_url)
                    
                    # Delay ngẫu nhiên để tránh bị phát hiện
                    random_delay = self.get_random_delay(delay)
                    time.sleep(random_delay)
                    
                    # Check for captcha
                    try:
                        captcha_element = self.driver.find_element(By.CSS_SELECTOR, '[src*="recaptcha"]')
                        if captcha_element:
                            self.log_message("Phát hiện captcha")
                            if not self.handle_captcha():
                                self.log_message("Không thể giải captcha, dừng tìm kiếm")
                                break
                    except:
                        # No captcha found, continue
                        pass
                    
                    # Find result cards
                    cards = self.driver.find_elements(By.CSS_SELECTOR, 'a[jsname="UWckNb"]')
                    
                    if not cards:
                        self.log_message("Không tìm thấy kết quả nào trên trang này")
                        break
                    
                    self.log_message(f"Tìm thấy {len(cards)} kết quả trên trang {page}")
                    
                    page_results = 0
                    for card in cards:
                        if current_results >= max_links or not self.is_scraping:
                            break
                            
                        try:
                            link = card.get_attribute("href")
                            name_element = card.find_element(By.CSS_SELECTOR, 'h3')
                            name = name_element.text
                            
                            # Remove "vn." if present
                            if link and link.startswith("https://vn.linkedin.com/"):
                                link = link.replace("https://vn.", "https://")
                            
                            if link and name and "linkedin.com" in link:
                                # Kiểm tra trùng lặp trước
                                if link not in self.found_links:
                                    self.found_links.add(link)
                                    self.root.after(0, self.add_result_to_table, name, link)
                                    current_results += 1
                                    page_results += 1
                                    self.log_message(f"[{current_results}] {name}")
                                else:
                                    self.log_message(f"Bỏ qua link trùng: {name}")
                                
                        except Exception as e:
                            continue
                    
                    if page_results == 0:
                        self.log_message("Không có kết quả mới, dừng tìm kiếm")
                        break
                        
                    page += 1
                    
                    # Delay ngẫu nhiên giữa các trang
                    if self.is_scraping and current_results < max_links:
                        page_delay = self.get_random_delay(delay)
                        self.log_message(f"Chờ {page_delay:.1f}s trước khi chuyển trang...")
                        time.sleep(page_delay)
                        
                except Exception as e:
                    self.log_message(f"Lỗi khi xử lý trang {page}: {str(e)}")
                    break
            
            self.log_message(f"Hoàn thành! Tổng cộng tìm thấy {current_results} profile")
            self.update_status(f"Hoàn thành - Tìm thấy {current_results} profiles")
            
        except Exception as e:
            self.log_message(f"Lỗi: {str(e)}")
            self.update_status("Có lỗi xảy ra")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            if self.drission_driver:
                try:
                    self.drission_driver.quit()
                except:
                    pass
            self.root.after(0, self.reset_ui_after_scraping)
            
    def export_json(self):
        """Export results to JSON file"""
        if not self.results:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Lưu kết quả"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                self.log_message(f"Đã xuất {len(self.results)} kết quả ra file: {file_path}")
                messagebox.showinfo("Thành công", f"Đã xuất {len(self.results)} kết quả ra file JSON")
            except Exception as e:
                self.log_message(f"Lỗi khi xuất file: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể xuất file: {str(e)}")

    def export_excel(self):
        """Export results to Excel file directly"""
        if not self.results:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        # Generate filename from search keyword
        search_keyword = self.search_url_var.get()
        default_filename = self.generate_excel_filename(search_keyword)
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,  # ✅ Đúng tham số
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Lưu file Excel"
        )

        
        if file_path:
            try:
                df = pd.DataFrame(self.results)
                df.index = df.index + 1  # Bắt đầu từ 1
                df.index.name = 'STT'
                
                # Đổi tên cột
                df.columns = ['Tên', 'Link LinkedIn']
                
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='LinkedIn Profiles', index=True)
                    
                    # Format worksheet
                    worksheet = writer.sheets['LinkedIn Profiles']
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                self.log_message(f"Đã xuất {len(self.results)} kết quả ra file Excel: {file_path}")
                messagebox.showinfo("Thành công", f"Đã xuất {len(self.results)} kết quả ra file Excel")
                
            except Exception as e:
                self.log_message(f"Lỗi khi xuất file Excel: {str(e)}")
                messagebox.showerror("Lỗi", f"Không thể xuất file Excel: {str(e)}")
                
    def clear_results(self):
        """Clear all results"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả kết quả?"):
            # Clear treeview
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Clear results list and found links set
            self.results.clear()
            self.found_links.clear()
            
            # Clear log
            self.log_text.delete(1.0, tk.END)
            
            self.update_status("Đã xóa kết quả")
            self.log_message("Đã xóa tất cả kết quả")

def main():
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    style.theme_use('clam')  # or 'alt', 'default', 'classic'
    
    app = LinkedInScraperGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_scraping:
            if messagebox.askokcancel("Thoát", "Đang có quá trình tìm kiếm. Bạn có muốn dừng và thoát?"):
                app.stop_scraping()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
