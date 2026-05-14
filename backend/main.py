from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
# 移除 sqlite3，改用 sqlalchemy
from sqlalchemy import create_engine

# 1. 建立 FastAPI 伺服器實例
app = FastAPI()

# 2. 設定 CORS (允許前端網頁連線過來)
# 這是必填的，否則你的 React 網頁 (port 5173) 會被瀏覽器阻擋，無法跟 FastAPI (port 8000) 溝通
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允許所有網域，實務上上線會改成前端的真實網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_db_data(stock_id: str, type_filter: str, days_filter: str):
    """
    從 雲端 PostgreSQL 資料庫中讀取並計算資料
    """
    # 🚨 將此處換成你的 Supabase 連線字串 (保留引號)
    DB_URL = "postgresql://postgres.devzpwqskyimxbivawac:xOfBbffRuStQsHol@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"
    
    warrant_type = 'call' if type_filter == '認購買超' else 'put'
    limit_days = int(days_filter.replace('日', ''))
    
    try:
        # 建立資料庫引擎
        engine = create_engine(DB_URL)
        
        query = f"""
            SELECT * FROM broker_trades
            WHERE stock_id = '{stock_id}' 
              AND warrant_type = '{warrant_type}'
            ORDER BY date DESC
        """
        
        # 讓 pandas 透過 engine 執行 SQL
        df_filtered = pd.read_sql_query(query, engine)
        
    except Exception as e:
        print(f"❌ 撈取資料失敗: {e}")
        return []

    # 如果沒撈到資料，直接回傳空陣列
    if df_filtered.empty:
        return []

    # (我們將天數過濾留在這裡處理，因為真正的「交易日」計算比較複雜，我們用筆數模擬)
    # 取最新的 N 天 (這裡用極簡化的方式模擬)
    df_filtered = df_filtered.head(limit_days * 10) 

    # 計算每筆交易的淨買超
    df_filtered['net_buy'] = df_filtered['buy_amount'] - df_filtered['sell_amount']

    # 按照券商名稱分群，並將淨買超加總
    grouped_df = df_filtered.groupby('broker_name')['net_buy'].sum().reset_index()

    # 按照加總後的淨買超進行排序 (由大到小)
    grouped_df = grouped_df.sort_values(by='net_buy', ascending=False)
    
    # 過濾掉賣超或0的券商
    grouped_df = grouped_df[grouped_df['net_buy'] > 0]

    # 轉換成前端需要的 JSON 格式
    result = []
    for index, row in grouped_df.iterrows():
        result.append({
            "name": row['broker_name'] + " (雲端版)", # 加上標記讓我們確認是從雲端來的
            "amount": int(row['net_buy'])
        })
        
    return result

@app.get("/api/warrants")
def get_warrant_chips(stock: str = '4919', type: str = '認購買超', days: str = '5日'):
    print(f"收到前端請求：股票={stock}, 類型={type}, 天數={days}")
    
    # 改為呼叫新的資料庫處理函數
    processed_data = process_db_data(stock, type, days)
    
    return {
        "status": "success", 
        "data": processed_data
    }