import pandas as pd
import sqlite3
import os

def migrate_csv_to_sqlite():
    """
    這個函數負責把我們之前的 CSV 檔案內容，安全地搬移到新的 SQLite 資料庫裡。
    這在軟體開發中稱為「資料遷移 (Data Migration)」。
    """
    db_file = 'warrants.db'
    csv_file = 'mock_database.csv'
    
    print("=== 開始資料庫升級程序 ===")
    
    # 步驟 1：建立並連線到資料庫
    # 如果 warrants.db 不存在，這行指令會自動幫你建立一個全新的檔案
    conn = sqlite3.connect(db_file)
    print(f"✅ 成功連線至 SQLite 資料庫: {db_file}")

    # 步驟 2：讀取原本的 CSV 舊資料
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            print(f"📥 成功讀取 CSV 檔案，共有 {len(df)} 筆資料準備遷移...")
            
            # 確保資料型態正確，避免後續查詢出錯
            # 在資料庫裡，我們明確定義 date 應該是整數(例如 20260514)，stock_id 應該是字串
            df['date'] = pd.to_numeric(df['date'], errors='coerce').fillna(0).astype(int)
            df['stock_id'] = df['stock_id'].astype(str)
            
            # 步驟 3：將 DataFrame 直接寫入資料庫！
            # if_exists='replace' 代表如果表格已經存在，就整個覆蓋掉 (因為我們是第一次建立)
            # 未來爬蟲寫入時，我們會改成 if_exists='append'
            df.to_sql('broker_trades', conn, if_exists='replace', index=False)
            print("🚀 資料成功寫入 SQLite 的 broker_trades 表格中！")
            
        except Exception as e:
            print(f"❌ 讀取或寫入資料失敗: {e}")
    else:
        print(f"⚠️ 找不到 {csv_file}，略過資料遷移。但資料庫已準備就緒！")

    # 記得關閉連線，釋放資源
    conn.close()
    print("=== 資料庫升級完成！ ===")

if __name__ == "__main__":
    migrate_csv_to_sqlite()