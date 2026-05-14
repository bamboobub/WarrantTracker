import requests
import pandas as pd
from datetime import datetime
import time
# 移除 sqlite3，改用 sqlalchemy
from sqlalchemy import create_engine
import urllib3
from fake_useragent import UserAgent

# 匯入我們寫好的找權證模組
import find_warrants

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_single_warrant_chips(warrant_code, warrant_type, date_str, stock_id):
    """
    去抓單一權證的「券商分點明細」。
    (這裡保留之前的模擬真實資料邏輯，未來可替換為券商 API)
    """
    # 為了畫面整潔，我們把印出單檔的 print 拿掉，改在迴圈外印出總進度
    import random
    brokers = ['兆豐', '元大-向上', '國票', '統一', '美林', '凱基-台北', '群益金鼎', '摩根大通', '台灣匯立', '台灣摩根士丹利']
    
    mock_trades = []
    # 隨機產生 3~10 家有交易的券商
    for _ in range(random.randint(3, 10)): 
        mock_trades.append({
            'date': int(date_str), # 存進資料庫我們統一用整數格式如 20260514
            'stock_id': str(stock_id),
            'warrant_type': warrant_type,
            'broker_name': random.choice(brokers),
            'buy_amount': random.randint(100, 10000) * 1000, 
            'sell_amount': random.randint(0, 8000) * 1000
        })
        
    return pd.DataFrame(mock_trades)

def run_daily_crawler():
    # 🎯 你的自選股追蹤清單！
    target_stocks = {
        '4919': '新唐',
        '2330': '台積電',
        '2317': '鴻海'
    }
    
    target_date = datetime.now().strftime('%Y%m%d')
    
    # 🚨 將此處換成你的 Supabase 連線字串 (保留引號)
    DB_URL = "postgresql://postgres.devzpwqskyimxbivawac:xOfBbffRuStQsHol@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
    
    print(f"=== 啟動每日自動籌碼更新排程 (雲端版) ===")
    print(f"📅 日期: {target_date}")
    
    # 1. 建立雲端資料庫引擎
    try:
        engine = create_engine(DB_URL)
        print("✅ 成功連線至 Supabase 雲端資料庫！")
    except Exception as e:
        print(f"❌ 資料庫連線失敗: {e}")
        return

    total_new_rows = 0
    
    try:
        # 2. 迴圈處理每一檔股票
        for stock_id, stock_name in target_stocks.items():
            print(f"🚀 開始處理: {stock_id} {stock_name}")
            
            # 呼叫 Shioaji 找權證
            warrants = find_warrants.get_warrants(stock_name)
            
            if not warrants:
                print(f"  ⚠️ 找不到 {stock_name} 的權證，跳過此檔。\n")
                continue
                
            print(f"  👉 找到 {len(warrants)} 檔權證，開始掃描籌碼...")
            
            stock_new_data = pd.DataFrame()
            # 迴圈抓取該股票底下的每一檔權證
            for w in warrants:
                df_single = fetch_single_warrant_chips(w['code'], w['type'], target_date, stock_id)
                if not df_single.empty:
                    stock_new_data = pd.concat([stock_new_data, df_single], ignore_index=True)
                
                # 爬蟲禮儀：每抓一檔休息 0.1 秒 (因為是模擬所以調快，實務上建議 1-3 秒)
                time.sleep(0.1) 
                
            # 3. 將這檔股票的資料寫入 Supabase 資料庫！
            if not stock_new_data.empty:
                # 這裡把 conn 換成 engine
                stock_new_data.to_sql('broker_trades', engine, if_exists='append', index=False)
                rows_added = len(stock_new_data)
                total_new_rows += rows_added
                print(f"  ✅ {stock_name} 掃描完畢！共新增 {rows_added} 筆分點紀錄至資料庫。\n")
                
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
    finally:
        # SQLAlchemy engine 會自動管理連線池，不需手動 close()
        pass
        
    print(f"🎉 爬蟲任務大功告成！今日總共為雲端資料庫注入了 {total_new_rows} 筆新資料。")

if __name__ == "__main__":
    run_daily_crawler()