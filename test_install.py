from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # 1. 启动 Chromium 浏览器（非头模式，这样你就能看到浏览器弹出来）
    browser = p.chromium.launch(headless=False)
    
    # 2. 打开一个新页面
    page = browser.new_page()
    
    # 3. 访问百度首页
    page.goto("https://www.baidu.com")
    
    # 4. 打印页面标题，证明成功访问
    print(f"成功打开网页，当前标题是: {page.title()}")
    
    # 暂停 5 秒让你看一眼，然后关闭
    time.sleep(5)
    browser.close()