import requests
import pandas as pd
from datetime import datetime
import time
import ssl

def fetch_warrant_chips(warrant_code, date_str):
    """
    爬取特定權證、特定日期的券商分點進出資料
    :param warrant_code: 權證代碼 (例如: '087114')
    :param date_str: 查詢日期 (格式: 'YYYYMMDD', 例如: '20240513')
    """
    print(f"開始抓取權證 {warrant_code} 在 {date_str} 的資料...")
    
    # 證交所 API 網址
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date_str}&type=ALL"
    
    # 設定 Headers，偽裝成正常的瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # 新增 verify=False 來略過 SSL 憑證檢查 (僅限於爬蟲測試遇到憑證問題時使用)
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status() 
        
        data = response.json()
        
        if data['stat'] == 'OK':
            print("✅ 成功連線並取得資料！")
            print("資料欄位:", data.keys())
            return data
        else:
            print("❌ 無法取得資料，可能是非交易日或無此代碼。")
            return None
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None

if __name__ == "__main__":
    # 因為今天是 2026 年，為了確保一定有資料，我們用 20240513 做測試
    test_date = '20240513' 
    test_warrant = '087114'
    
    # 忽略 urllib3 的 InsecureRequestWarning 警告 (因為我們設了 verify=False)
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    fetch_warrant_chips(test_warrant, test_date)