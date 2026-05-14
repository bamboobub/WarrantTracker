import shioaji as sj
import os

# 建立 Shioaji API 物件
api = sj.Shioaji()

# 這裡要換成你剛剛申請到的真實金鑰 (請務必保護好，不要上傳到公開的 GitHub)
# 實務上我們會用環境變數 (.env) 來管理，但為了初步測試，我們先直接寫在這裡
API_KEY = "QGuAHbrAJVr7YjZo566fDobeSiSgAF7FdKcLZenQwed"
SECRET_KEY = "ncpXVRa6DyDkFBNxjJTQZQTRDbxbdZvMmtzRMPJao9s"

print("🔄 嘗試登入永豐 Shioaji API...")
try:
    # 執行登入
    # 如果你剛剛沒有勾選「正式環境」，這裡可能需要加上參數，但我們建議勾正式環境
    api.login(
        api_key=API_KEY,
        secret_key=SECRET_KEY
    )
    
    print("✅ 登入成功！")
    
    # 測試抓取資料：取得「新唐 (4919)」的股票基本資料合約
    contract = api.Contracts.Stocks["4919"]
    print(f"📊 成功取得標的合約：{contract.name} ({contract.code})")
    
    # 接下來就是 Shioaji 的強項：抓取這檔股票今日的 tick 報價或盤後資料
    # (我們後續的章節會用它來抓權證與分點明細)
    
except Exception as e:
    print(f"❌ 登入或連線失敗，錯誤訊息：\n{e}")

finally:
    # 測試完畢後，記得登出
    api.logout()
    print("🔌 系統已登出。")    