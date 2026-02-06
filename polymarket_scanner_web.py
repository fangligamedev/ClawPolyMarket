#!/usr/bin/env python3
"""
Polymarket 套利扫描器 - Web 版本
使用浏览器自动化抓取市场数据
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
from datetime import datetime

def setup_driver():
    """设置无头浏览器"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    return webdriver.Chrome(options=chrome_options)

def scrape_polymarket():
    """
    抓取 Polymarket 市场数据
    """
    driver = setup_driver()
    markets = []
    
    try:
        print("🔍 正在打开 Polymarket...")
        driver.get("https://polymarket.com/markets")
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy='market-card']")))
        
        print("✅ 页面已加载，正在抓取市场数据...")
        
        # 滚动加载更多市场
        for _ in range(5):  # 滚动 5 次
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # 获取市场卡片
        cards = driver.find_elements(By.CSS_SELECTOR, "[data-cy='market-card']")
        
        for card in cards[:20]:  # 取前 20 个
            try:
                title = card.find_element(By.CSS_SELECTOR, "h3").text
                
                # 获取价格信息
                prices = card.find_elements(By.CSS_SELECTOR, "[data-cy='outcome-price']")
                
                market_data = {
                    "title": title,
                    "prices": [p.text for p in prices],
                    "scraped_at": datetime.now().isoformat()
                }
                markets.append(market_data)
                
            except Exception as e:
                continue
        
        print(f"✅ 成功抓取 {len(markets)} 个市场")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        print("   可能需要安装 Chrome 和 Selenium")
        
    finally:
        driver.quit()
    
    return markets

def analyze_opportunities(markets):
    """
    分析套利机会
    """
    opportunities = []
    
    for market in markets:
        title = market.get("title", "")
        prices = market.get("prices", [])
        
        # 查找低价机会（< 10%）
        for price_str in prices:
            try:
                # 解析价格，例如 "5¢" -> 0.05
                price_val = float(price_str.replace("¢", "").replace("$", "")) / 100
                
                if 0.01 < price_val < 0.10:  # 1% - 10%
                    odds = 1 / price_val
                    ev = 0.3 - price_val  # 假设 30% 真实概率
                    
                    if ev > 0:
                        opportunities.append({
                            "market": title,
                            "price": price_val,
                            "odds": f"{odds:.1f}:1",
                            "ev": ev
                        })
                        
            except:
                continue
    
    return opportunities

def main():
    print("🚀 Polymarket Web 抓取版本")
    print("注意: 需要安装 Chrome 和 Selenium\n")
    
    try:
        markets = scrape_polymarket()
        opportunities = analyze_opportunities(markets)
        
        print(f"\n📊 发现 {len(opportunities)} 个潜在机会")
        for opp in opportunities[:5]:
            print(f"   • {opp['market'][:50]}...")
            print(f"     价格: {opp['price']:.2%}, 赔率: {opp['odds']}, EV: {opp['ev']:.3f}\n")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n💡 替代方案:")
        print("   1. 手动访问 https://polymarket.com 查看市场")
        print("   2. 关注低概率高赔率的市场（<10% 概率）")
        print("   3. 使用 Polymarket 官方 APP 接收通知")

if __name__ == "__main__":
    main()
