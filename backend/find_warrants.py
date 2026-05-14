import shioaji as sj

def get_warrants(api, target_stock_name):
    print(f"🔍 正在搜尋名稱包含【{target_stock_name}】的權證...")
    call_warrants = []
    put_warrants = []

    try:
        tse_contracts = list(api.Contracts.Stocks.TSE)
        otc_contracts = list(api.Contracts.Stocks.OTC)
        all_contracts = tse_contracts + otc_contracts

        for contract in all_contracts:
            contract_name = str(getattr(contract, 'name', ''))
            contract_code = str(getattr(contract, 'code', ''))
            
            # 過濾條件：名字包含標的，代碼長度>=6，且通常以0開頭
            if target_stock_name in contract_name and len(contract_code) >= 6 and contract_code.startswith('0'):
                w_type = 'call' if '購' in contract_name else ('put' if '售' in contract_name else 'unknown')
                
                if w_type != 'unknown':
                    warrant_info = {"code": contract_code, "name": contract_name, "type": w_type}
                    if w_type == 'call':
                         call_warrants.append(warrant_info)
                    else:
                         put_warrants.append(warrant_info)
                         
    except Exception as e:
        print(f"搜尋過程中發生錯誤: {e}")

    return call_warrants + put_warrants