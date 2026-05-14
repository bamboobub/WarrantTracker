import shioaji as sj
import pandas as pd
import os

def get_warrants(target_stock_name):
    # 初始化 API
    api = sj.Shioaji(simulation=False) 

    # 🚨 改由環境變數讀取金鑰 (GitHub Actions 安全機制)
    # 請把後面的預設值換回你自己的真實金鑰，以便在本地端測試
    API_KEY = os.environ.get("SHIOAJI_API_KEY", "QGuAHbrAJVr7YjZo566fDobeSiSgAF7FdKcLZenQwed")
    SECRET_KEY = os.environ.get("SHIOAJI_SECRET_KEY", "ncpXVRa6DyDkFBNxjJTQZQTRDbxbdZvMmtzRMPJao9s")

    print("🔄 登入永豐 Shioaji API...")
    try:
        api.login(api_key=API_KEY, secret_key=SECRET_KEY)
    except Exception as e:
         print(f"登入失敗: {e}")
         return []

    print(f"🔍 正在搜尋名稱包含【{target_stock_name}】的所有流通權證...")

    call_warrants = []
    put_warrants = []

    tse_contracts = list(api.Contracts.Stocks.TSE)
    otc_contracts = list(api.Contracts.Stocks.OTC)
    all_contracts = tse_contracts + otc_contracts

    for contract in all_contracts:
        try:
            contract_name = str(getattr(contract, 'name', ''))
            contract_code = str(getattr(contract, 'code', ''))
            
            if target_stock_name in contract_name:
                # 判斷是認購還是認售
                w_type = 'call' if '購' in contract_name else ('put' if '售' in contract_name else 'unknown')
                
                if w_type != 'unknown':
                    warrant_info = {
                        "code": contract_code,
                        "name": contract_name,
                        "type": w_type
                    }
                    if w_type == 'call':
                         call_warrants.append(warrant_info)
                    else:
                         put_warrants.append(warrant_info)
        except Exception:
            pass

    # 將兩個清單合併並回傳
    all_warrants = call_warrants + put_warrants
    print(f"✅ 共找到 {len(call_warrants)} 檔認購，{len(put_warrants)} 檔認售。")
    return all_warrants

# 測試用：如果直接執行這支檔案，才會印出結果
if __name__ == "__main__":
    warrants = get_warrants("新唐")
    print(f"總共找到 {len(warrants)} 檔相關合約。")