import React, { useState, useEffect } from 'react';
import { ChevronLeft, Share2, Star, ChevronDown, Loader2, Search } from 'lucide-react';
import { createClient } from '@supabase/supabase-js';

// 🚨 請填入你在 Supabase API 設定頁面找到的 URL 和 anon key
const SUPABASE_URL = 'https://devzpwqskyimxbivawac.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRldnpwd3Fza3lpbXhiaXZhd2FjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NzQxMDQsImV4cCI6MjA5NDI1MDEwNH0.76TCqVXWLi59_DXB_ZCLU8RXEsrT3uHhMjVd04aluKk';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export default function App() {
  const [activeTab, setActiveTab] = useState('權證');
  const [activeType, setActiveType] = useState('認購買超');
  const [daysFilter, setDaysFilter] = useState('5日');
  const [isLoading, setIsLoading] = useState(false);
  const [brokerageData, setBrokerageData] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchInput, setSearchInput] = useState('');
  const [currentStock, setCurrentStock] = useState('4919'); 

  const stockData = {
    name: currentStock === '4919' ? '新唐' : currentStock === '2330' ? '台積電' : currentStock === '2317' ? '鴻海' : '查詢中',
    code: currentStock,
    price: currentStock === '4919' ? '166.0' : currentStock === '2330' ? '825.0' : '---',
    change: currentStock === '4919' ? '15.0' : currentStock === '2330' ? '10.0' : '---',
    changePercent: currentStock === '4919' ? '-8.29%' : currentStock === '2330' ? '+1.22%' : '---',
    isDown: currentStock === '4919',
    time: '最新交易日',
    volume: '---',
    totalVolume: '---',
  };

  // 直接從 Supabase 抓取資料並在前端進行計算！
  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    
    const fetchSupabaseData = async () => {
      try {
        const warrantType = activeType === '認購買超' ? 'call' : 'put';
        const limitDays = parseInt(daysFilter.replace('日', ''));
        
        // 1. 向 Supabase 請求資料 (對應 SQL: SELECT * FROM broker_trades WHERE ...)
        const { data, error } = await supabase
          .from('broker_trades')
          .select('*')
          .eq('stock_id', currentStock)
          .eq('warrant_type', warrantType)
          .order('date', { ascending: false })
          .limit(limitDays * 10); // 這裡我們沿用原本的模擬筆數限制

        if (error) throw error;

        // 2. 在前端用 JavaScript 進行加總計算 (取代原本 Python pandas 的工作)
        if (data && data.length > 0) {
          const brokerTotals = {};
          
          data.forEach(row => {
            const netBuy = row.buy_amount - row.sell_amount;
            if (!brokerTotals[row.broker_name]) {
              brokerTotals[row.broker_name] = 0;
            }
            brokerTotals[row.broker_name] += netBuy;
          });

          // 3. 過濾出買超 > 0 的券商，並由大到小排序
          const processedResult = Object.keys(brokerTotals)
            .map(name => ({
              name: name + " (直連雲端)", 
              amount: brokerTotals[name]
            }))
            .filter(item => item.amount > 0)
            .sort((a, b) => b.amount - a.amount);

          if (isMounted) setBrokerageData(processedResult);
        } else {
          if (isMounted) setBrokerageData([]); // 沒資料就清空
        }
      } catch (err) {
        console.error('抓取 Supabase 資料失敗:', err);
        if (isMounted) setBrokerageData([]);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    fetchSupabaseData();

    return () => { isMounted = false; };
  }, [currentStock, activeType, daysFilter]);

  const tabs = ['即時', 'K線', '權證', '每日主力'];
  const dayOptions = ['1日', '3日', '5日', '10日'];

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim() !== '') {
      setCurrentStock(searchInput.trim());
      setSearchInput('');
    }
  };

  return (
    <div className="flex justify-center items-start sm:items-center min-h-screen bg-black sm:bg-gray-900 font-sans text-white">
      <div className="w-full sm:w-[400px] h-screen sm:h-[800px] bg-[#0A111E] flex flex-col relative sm:shadow-2xl sm:rounded-3xl sm:border sm:border-gray-700 overflow-hidden">
        
        {/* --- 頂部導航列 (修改為搜尋框) --- */}
        <div className="flex justify-between items-center px-4 py-3 shrink-0 bg-[#0A111E] z-20">
          <button className="text-white hover:bg-gray-800 p-2 -ml-2 rounded-full transition-colors">
            <ChevronLeft size={24} />
          </button>
          
          <form onSubmit={handleSearch} className="flex flex-col items-center relative">
            <div className="flex items-center bg-gray-800 rounded-md px-2 py-1 focus-within:ring-1 focus-within:ring-orange-500">
              <Search size={14} className="text-gray-400 mr-1" />
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder={currentStock}
                className="bg-transparent text-white text-center text-lg font-bold w-20 outline-none placeholder-gray-400"
              />
            </div>
            <span className="text-xs text-gray-400 mt-1">{stockData.name}</span>
          </form>

          <div className="flex space-x-2">
            <button className="text-white hover:bg-gray-800 p-2 rounded-full transition-colors"><Share2 size={20} /></button>
            <button className="text-orange-500 hover:bg-gray-800 p-2 rounded-full transition-colors"><Star size={20} fill="#f97316" /></button>
          </div>
        </div>

        {/* --- 股票屬性標籤 --- */}
        <div className="px-4 py-1 flex items-center shrink-0">
          <span className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded-sm border border-gray-700">
            上市-可當沖/有股期/有權證
          </span>
        </div>

        {/* --- 價格與成交量資訊 --- */}
        <div className="flex justify-between items-start px-4 mt-3 shrink-0">
          <div className="flex flex-col">
            <div className="flex items-baseline space-x-2">
              <span className={`text-5xl font-bold tracking-tight ${stockData.isDown ? 'text-[#00E676]' : 'text-[#FF3B30]'}`}>
                {stockData.price}
              </span>
              <div className={`flex flex-col text-sm font-medium ${stockData.isDown ? 'text-[#00E676]' : 'text-[#FF3B30]'}`}>
                <span>{stockData.isDown ? '▼' : '▲'}{stockData.change}</span>
                <span>({stockData.changePercent})</span>
              </div>
            </div>
          </div>
          <div className="flex flex-col text-right text-xs text-gray-400 space-y-1">
            <span>{stockData.time}</span>
            <span>單量 <span className="text-[#FF3B30] font-bold">{stockData.volume}</span></span>
            <span>總量 {stockData.totalVolume}</span>
          </div>
        </div>

        {/* --- 主功能分頁 (Tabs) --- */}
        <div className="flex border-b border-gray-800 mt-5 shrink-0">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-3 text-center text-sm font-medium transition-colors relative
                ${activeTab === tab ? 'text-white' : 'text-gray-500 hover:text-gray-300'}
              `}
            >
              {tab}
              {activeTab === tab && (
                <div className="absolute bottom-0 left-[20%] right-[20%] h-0.5 bg-orange-500"></div>
              )}
            </button>
          ))}
        </div>

        {/* --- 權證專屬操作區 --- */}
        {activeTab === '權證' && (
          <>
            <div className="flex justify-between items-center px-4 py-3 shrink-0">
              <div className="flex bg-[#121E2F] p-1 rounded-md">
                <button
                  onClick={() => setActiveType('認購買超')}
                  className={`px-4 py-1.5 text-sm rounded transition-colors ${
                    activeType === '認購買超' ? 'bg-[#1E3A8A] text-white shadow-sm' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  認購買超
                </button>
                <button
                  onClick={() => setActiveType('認售買超')}
                  className={`px-4 py-1.5 text-sm rounded transition-colors ${
                    activeType === '認售買超' ? 'bg-[#1E3A8A] text-white shadow-sm' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  認售買超
                </button>
              </div>
              
              <div className="relative">
                <button 
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center space-x-1 bg-[#121E2F] border border-gray-700 hover:bg-gray-800 px-3 py-1.5 rounded-md text-sm text-gray-200 transition-colors"
                >
                  <span>{daysFilter}</span>
                  <ChevronDown size={16} />
                </button>
                
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-1 w-24 bg-[#1E293B] border border-gray-700 rounded-md shadow-xl z-10 py-1">
                    {dayOptions.map(option => (
                      <button
                        key={option}
                        onClick={() => {
                          setDaysFilter(option);
                          setIsDropdownOpen(false);
                        }}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-700 transition-colors ${daysFilter === option ? 'text-orange-400' : 'text-gray-300'}`}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-between px-6 py-2 bg-[#121E2F]/80 text-xs text-gray-400 shrink-0 border-y border-gray-800">
              <span>券商名稱</span>
              <span>買超金額(千)</span>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar relative">
              {isLoading ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0A111E]/80 z-0">
                  <Loader2 className="animate-spin text-blue-500 mb-2" size={32} />
                  <span className="text-gray-400 text-sm">載入籌碼資料中...</span>
                </div>
              ) : brokerageData.length > 0 ? (
                <div className="pb-20">
                  {brokerageData.map((item, index) => (
                    <div 
                      key={index} 
                      className="flex justify-between items-center px-6 py-3.5 border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors active:bg-gray-800"
                    >
                      <span className="text-gray-200 text-[15px]">{item.name}</span>
                      <span className="text-gray-100 font-medium tracking-wide">
                        {item.amount.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <span>目前查無此條件之資料</span>
                  <span className="text-xs mt-2">請確認代碼是否輸入正確或等待盤後更新</span>
                </div>
              )}
            </div>
          </>
        )}
        
        {activeTab !== '權證' && (
           <div className="flex-1 flex items-center justify-center text-gray-500">
             {activeTab} 內容建置中...
           </div>
        )}

      </div>
    </div>
  );
}