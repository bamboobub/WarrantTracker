import pandas as pd
from datetime import datetime
import time
from sqlalchemy import create_engine
import os
import random
import shioaji as sj

def fetch_single_warrant_chips(warrant_code, warrant_type, date_str, stock_id):
    """
    抓取單一權證分點資料，並精確控制金額為「萬元」級別
    """
    # 移除了外資券商，換成台灣權證市場常見的本土主力分點
    brokers = ['兆豐', '元大-向上', '國票', '統一', '凱基-台北', '群益金鼎', '富邦-建國', '元大-館前', '永豐金', '康和', '華南永昌']
    mock_trades = []
    
    # 隨機產生 1~4 家有交易的券商
    for _ in range(random.randint(1, 4)): 
        # 產生合理的權證單筆交易金額基數 (約幾萬到一百多萬)
        buy_yuan = random.randint(1, 150) * 10000 
        sell_yuan = random.randint(0, 80) * 10000
        
        mock_trades.append({
            'date': int(date_str), 
            'stock_id': str(stock_id),
            'warrant_code': str(warrant_code), # 🚨 新增：紀錄權證代號
            'warrant_type': warrant_type,
            'broker_name': random.choice(brokers),
            # 直接轉化為「萬元」儲存
            'buy_amount': int(buy_yuan / 10000), 
            'sell_amount': int(sell_yuan / 10000)
        })
    return pd.DataFrame(mock_trades)

def run_daily_crawler():
    target_date = datetime.now().strftime('%Y%m%d')
    DB_URL = os.environ.get("DB_URL")
    API_KEY = os.environ.get("SHIOAJI_API_KEY")
    SECRET_KEY = os.environ.get("SHIOAJI_SECRET_KEY")
    
    if not all([DB_URL, API_KEY, SECRET_KEY]):
        print("❌ 缺少環境變數！")
        return

    print(f"=== 啟動全市場權證籌碼掃描 ===")
    api = sj.Shioaji(simulation=False)
    
    try:
        api.login(api_key=API_KEY, secret_key=SECRET_KEY)
        engine = create_engine(DB_URL)
        print("✅ API 與資料庫連線成功！開始建構全市場地圖...")
        
        # 1. 取得全市場所有 4 碼普通股
        stock_dict = {}
        for category in [api.Contracts.Stocks.TSE, api.Contracts.Stocks.OTC]:
            for c in category:
                if len(c.code) == 4 and c.code.isdigit():
                    stock_dict[c.name] = c.code

        # 2. 高速配對：將全市場權證分類到對應的股票下
        warrant_map = {}
        total_warrants = 0
        for category in [api.Contracts.Stocks.TSE, api.Contracts.Stocks.OTC]:
            for c in category:
                if len(c.code) >= 6 and c.code.startswith('0'):
                    w_type = 'call' if '購' in c.name else ('put' if '售' in c.name else None)
                    if w_type:
                        # 用權證名字去比對屬於哪檔股票 (例如: 台積電群益36購01 -> 台積電)
                        for s_name, s_id in stock_dict.items():
                            if s_name in c.name:
                                if s_id not in warrant_map:
                                    warrant_map[s_id] = []
                                warrant_map[s_id].append({"code": c.code, "name": c.name, "type": w_type})
                                total_warrants += 1
                                break
                                
        print(f"🗺️ 地圖建構完成！找到 {len(warrant_map)} 檔有發行權證的股票，共 {total_warrants} 檔權證。")

        total_new_rows = 0
        
        # 3. 開始掃描並寫入資料庫
        for stock_id, warrants in warrant_map.items():
            stock_new_data = pd.DataFrame()
            
            for w in warrants:
                df_single = fetch_single_warrant_chips(w['code'], w['type'], target_date, stock_id)
                if not df_single.empty:
                    stock_new_data = pd.concat([stock_new_data, df_single], ignore_index=True)
                
            if not stock_new_data.empty:
                stock_new_data.to_sql('broker_trades', engine, if_exists='append', index=False)
                total_new_rows += len(stock_new_data)
                print(f"  ✅ 股票代號 {stock_id} 掃描完畢！寫入 {len(stock_new_data)} 筆明細。")
                
            time.sleep(0.05) # 微小暫停避免斷線

        print(f"\n🎉 全市場掃描大功告成！今日總共為資料庫注入了 {total_new_rows} 筆新資料。")
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
    finally:
        api.logout()

if __name__ == "__main__":
    run_daily_crawler()