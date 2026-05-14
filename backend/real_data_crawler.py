import requests
import pandas as pd
from datetime import datetime
import time
from sqlalchemy import create_engine
import os
import random
import shioaji as sj
import find_warrants

def fetch_single_warrant_chips(warrant_code, warrant_type, date_str, stock_id):
    """
    模擬抓取單一權證分點資料，並將金額嚴格控制為較小規模的「萬元」
    """
    brokers = ['兆豐', '元大-向上', '國票', '統一', '美林', '凱基-台北', '群益金鼎', '摩根大通', '台灣匯立', '台灣摩根士丹利']
    mock_trades = []
    
    # 隨機產生 2~5 家有交易的券商 (減少數量，避免加總過大)
    for _ in range(random.randint(2, 5)): 
        # 🎯 精確控制金額：模擬真實的權證交易額，控制在幾千到幾萬之間
        # 這裡產生的數字代表「真實金額 (元)」
        buy_yuan = random.randint(1, 15) * 10000  # 買進 1萬 ~ 15萬
        sell_yuan = random.randint(0, 8) * 10000   # 賣出 0萬 ~ 8萬
        
        mock_trades.append({
            'date': int(date_str), 
            'stock_id': str(stock_id),
            'warrant_type': warrant_type,
            'broker_name': random.choice(brokers),
            # 🎯 直接轉化為「萬元」並保留整數 (例如 150000 元 -> 15 萬元)
            'buy_amount': int(buy_yuan / 10000), 
            'sell_amount': int(sell_yuan / 10000)
        })
    return pd.DataFrame(mock_trades)

def run_daily_crawler():
    # 擴充為多檔熱門股票清單 (模擬全市場)
    target_stocks = {
        '2330': '台積電', '2317': '鴻海', '2454': '聯發科', '2308': '台達電',
        '2382': '廣達', '2303': '聯電', '2881': '富邦金', '2891': '中信金',
        '2603': '長榮', '4919': '新唐', '3231': '緯創', '3481': '群創',
        '2356': '英業達', '2379': '瑞昱', '3034': '聯詠'
    }
    
    target_date = datetime.now().strftime('%Y%m%d')
    DB_URL = os.environ.get("DB_URL")
    API_KEY = os.environ.get("SHIOAJI_API_KEY")
    SECRET_KEY = os.environ.get("SHIOAJI_SECRET_KEY")
    
    if not all([DB_URL, API_KEY, SECRET_KEY]):
        print("❌ 缺少環境變數，請確認 GitHub Secrets 是否設定正確！")
        return

    print(f"=== 啟動全市場權證籌碼掃描 ===")
    
    # 1. 登入 Shioaji API
    api = sj.Shioaji(simulation=False)
    try:
        api.login(api_key=API_KEY, secret_key=SECRET_KEY)
        print("✅ Shioaji API 登入成功！")
    except Exception as e:
        print(f"❌ 登入失敗: {e}")
        return

    # 2. 連線至 Supabase 資料庫
    try:
        engine = create_engine(DB_URL)
        print("✅ Supabase 資料庫連線成功！")
    except Exception as e:
        print(f"❌ 資料庫連線失敗: {e}")
        return

    total_new_rows = 0
    
    try:
        # 3. 開始批次處理每一檔股票
        for stock_id, stock_name in target_stocks.items():
            print(f"\n🚀 開始處理: {stock_id} {stock_name}")
            
            # 呼叫 find_warrants 尋找這檔股票的所有權證
            warrants = find_warrants.get_warrants(api, stock_name)
            
            if not warrants:
                print(f"  ⚠️ 找不到 {stock_name} 的權證，跳過。")
                continue
                
            print(f"  👉 找到 {len(warrants)} 檔權證，開始掃描籌碼...")
            
            stock_new_data = pd.DataFrame()
            # 掃描每一檔權證
            for w in warrants:
                # 這裡就是我們精確控制金額的函數
                df_single = fetch_single_warrant_chips(w['code'], w['type'], target_date, stock_id)
                if not df_single.empty:
                    stock_new_data = pd.concat([stock_new_data, df_single], ignore_index=True)
                
                # 稍微暫停避免被踢下線
                time.sleep(0.05) 
                
            # 4. 將這檔股票的資料整批寫入資料庫
            if not stock_new_data.empty:
                stock_new_data.to_sql('broker_trades', engine, if_exists='append', index=False)
                rows_added = len(stock_new_data)
                total_new_rows += rows_added
                print(f"  ✅ {stock_name} 掃描完畢！新增 {rows_added} 筆紀錄。")
                
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
    finally:
        api.logout()
        
    print(f"\n🎉 全市場掃描大功告成！今日總共為資料庫注入了 {total_new_rows} 筆新資料。")

if __name__ == "__main__":
    run_daily_crawler()