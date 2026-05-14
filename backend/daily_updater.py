import pandas as pd
from datetime import datetime
import random

def fetch_todays_data_from_api(stock_id):
    """
    這裡模擬我們透過券商 API (如永豐/富果) 抓取到了今天的權證分點資料。
    實務上，這裡會是呼叫 API 的 requests 程式碼。
    """
    # 取得今天的日期，格式轉為 YYYYMMDD
    today_str = datetime.now().strftime('%Y%m%d')
    print(f"📡 正在從 API 抓取 {today_str} 的籌碼資料...")
    
    # 模擬抓到的隨機真實資料
    brokers = ['兆豐', '元大-向上', '國票', '統一', '美林', '凱基-台北', '群益金鼎']
    
    new_data = []
    # 模擬產生 10 筆今天的交易紀錄
    for _ in range(10):
        new_data.append({
            'date': today_str,
            'stock_id': stock_id,
            'warrant_type': random.choice(['call', 'put']), # 隨機認購或認售
            'broker_name': random.choice(brokers),
            'buy_amount': random.randint(1000, 10000),
            'sell_amount': random.randint(0, 5000)
        })
        
    return pd.DataFrame(new_data)

def update_database():
    csv_file = 'mock_database.csv'
    
    # 1. 抓取今日新資料
    df_new = fetch_todays_data_from_api(stock_id='4919')
    
    if not df_new.empty:
        # 2. 安全的寫入方式：先讀取舊資料，合併後再整個寫入
        try:
            # 引入 pandas，因為我們需要用它來讀取和合併資料
            import pandas as pd
            df_old = pd.read_csv(csv_file)
            # 將舊資料與新資料上下合併 (concat)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        except FileNotFoundError:
            # 如果檔案不存在，新資料就是全部資料
            df_combined = df_new
            
        # index=False 代表不寫入最前面的 0, 1, 2 索引編號
        df_combined.to_csv(csv_file, index=False)
        print(f"✅ 成功將 {len(df_new)} 筆新資料寫入 {csv_file}！")
    else:
        print("今天沒有抓到新資料。")

if __name__ == "__main__":
    print("=== 啟動每日籌碼更新排程 ===")
    update_database()