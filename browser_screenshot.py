# -*- coding: utf-8 -*-
"""
浏览器自动截图模块
使用 Playwright 自动访问京东页面并截图
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time


def take_jd_screenshot(
    url: str,
    output_path: str = "screenshot.png",
    width: int = 1920,
    height: int = 1080,
    wait_time: int = 3
) -> str:
    """
    自动截取京东商品页面
    
    Args:
        url: 京东商品链接
        output_path: 截图保存路径
        width: 浏览器宽度
        height: 浏览器高度
        wait_time: 页面加载后等待时间（秒）
    
    Returns:
        截图保存的完整路径
    """
    output_file = Path(output_path)
    
    with sync_playwright() as p:
        # 启动浏览器（非无头模式可以看到过程）
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 创建上下文，模拟真实浏览器
        context = browser.new_context(
            viewport={'width': width, 'height': height},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        
        try:
            # 访问页面
            print(f"正在访问: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 等待页面完全加载
            time.sleep(wait_time)
            
            # 滚动到顶部确保显示完整
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)
            
            # 截图
            page.screenshot(path=str(output_file), full_page=False)
            print(f"截图已保存: {output_file.absolute()}")
            
        except Exception as e:
            print(f"截图失败: {e}")
            raise
        finally:
            browser.close()
    
    return str(output_file.absolute())


def take_screenshot_with_scroll(
    url: str,
    output_path: str = "screenshot_full.png",
    width: int = 1920
) -> str:
    """
    截取整个页面（长截图）
    
    Args:
        url: 页面链接
        output_path: 截图保存路径
        width: 浏览器宽度
    
    Returns:
        截图保存的完整路径
    """
    output_file = Path(output_path)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': width, 'height': 800},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(2)
            
            # 全页面截图
            page.screenshot(path=str(output_file), full_page=True)
            print(f"长截图已保存: {output_file.absolute()}")
            
        finally:
            browser.close()
    
    return str(output_file.absolute())


if __name__ == "__main__":
    # 测试
    test_url = "https://item.jd.com/100012043978.html"
    take_jd_screenshot(test_url, "test_screenshot.png")





