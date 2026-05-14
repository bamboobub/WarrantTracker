import shioaji as sj
import pandas as pd
from sqlalchemy import create_engine
import os

# 🚨 請替換成你真實的金鑰與連線網址
API_KEY = "QGuAHbrAJVr7YjZo566fDobeSiSgAF7FdKcLZenQwed"
SECRET_KEY = "ncpXVRa6DyDkFBNxjJTQZQTRDbxbdZvMmtzRMPJao9s"
DB_URL = "postgresql://postgres.devzpwqskyimxbivawac:xOfBbffRuStQsHol@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"

def update_names():
    print("登入永豐 API...")
    api = sj.Shioaji(simulation=False)
    
    try:
        api.login(API_KEY, SECRET_KEY)
        print("✅ 登入成功！正在整理全台股名單...")
        
        stock_list = []
        # 掃描上市(TSE)與上櫃(OTC)市場
        for category in [api.Contracts.Stocks.TSE, api.Contracts.Stocks.OTC]:
            for c in category:
                # 過濾出純數字的4碼股票 (排除ETF、權證等)
                if len(c.code) == 4 and c.code.isdigit():
                    stock_list.append({"stock_id": c.code, "stock_name": c.name})
        
        # 轉成 DataFrame 準備寫入資料庫
        df = pd.DataFrame(stock_list)
        print(f"共找到 {len(df)} 檔普通股。正在寫入 Supabase...")
        
        engine = create_engine(DB_URL)
        # if_exists='replace' 會自動幫我們建立 stock_names 表格並覆蓋舊資料
        df.to_sql('stock_names', engine, if_exists='replace', index=False)
        
        print("🎉 股票代碼簿更新完成！")
        
    except Exception as e:
        print(f"發生錯誤：{e}")
    finally:
        api.logout()

if __name__ == "__main__":
    update_names()