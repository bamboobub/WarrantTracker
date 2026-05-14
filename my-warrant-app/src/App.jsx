import React, { useState, useEffect } from 'react';
import { ChevronLeft, Share2, Star, ChevronDown, Loader2, Search, Trophy } from 'lucide-react';
import { createClient } from '@supabase/supabase-js';

// 🚨 請填入你在 Supabase API 設定頁面找到的 URL 和 anon key
const SUPABASE_URL = 'https://devzpwqskyimxbivawac.supabase.co'; 
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRldnpwd3Fza3lpbXhiaXZhd2FjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NzQxMDQsImV4cCI6MjA5NDI1MDEwNH0.76TCqVXWLi59_DXB_ZCLU8RXEsrT3uHhMjVd04aluKk';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 建立股票代碼對照表
const STOCK_MAP = {
  '2330': '台積電', '2317': '鴻海', '2454': '聯發科', '2308': '台達電',
  '2382': '廣達', '2303': '聯電', '2881': '富邦金', '2891': '中信金',
  '2603': '長榮', '4919': '新唐', '3231': '緯創', '3481': '群創',
  '2356': '英業達', '2379': '瑞昱', '3034': '聯詠'
};

export default function App() {
  const [activeTab, setActiveTab] = useState('每日主力'); // 預設改為排行榜大廳
  const [activeType, setActiveType] = useState('認購買超');
  const [daysFilter, setDaysFilter] = useState('5日');
  const [isLoading, setIsLoading] = useState(false);
  
  // 個股查詢狀態
  const [brokerageData, setBrokerageData] = useState([]);
  const [searchStock, setSearchStock] = useState('2330');
  const [currentStock, setCurrentStock] = useState('2330');
  
  // 排行榜狀態
  const [rankingData, setRankingData] = useState([]);
  const [latestDateText, setLatestDateText] = useState('');

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // 抓取單一股票資料 (原本的邏輯)
  const fetchSingleStockData = async (stockId, type, days) => {
    setIsLoading(true);
    const warrantType = type === '認購買超' ? 'call' : 'put';
    const limitDays = parseInt(days.replace('日', ''));

    try {
      const { data, error } = await supabase
        .from('broker_trades')
        .select('*')
        .eq('stock_id', stockId)
        .eq('warrant_type', warrantType)
        .order('date', { ascending: false })
        .limit(limitDays * 20);

      if (error) throw error;
      if (!data || data.length === 0) {
        setBrokerageData([]);
        setIsLoading(false);
        return;
      }

      const rankMap = {};
      data.forEach(trade => {
        const netBuy = trade.buy_amount - trade.sell_amount;
        if (!rankMap[trade.broker_name]) rankMap[trade.broker_name] = 0;
        rankMap[trade.broker_name] += netBuy;
      });

      const processedData = Object.keys(rankMap)
        .map(broker => ({ name: broker + " (直連)", amount: rankMap[broker] }))
        .filter(item => item.amount > 0)
        .sort((a, b) => b.amount - a.amount);

      setBrokerageData(processedData);
    } catch (err) {
      console.error("撈取失敗:", err);
      setBrokerageData([]);
    }
    setIsLoading(false);
  };

  // 抓取全市場排行資料 (全新邏輯)
  const fetchMarketRanking = async (type) => {
    setIsLoading(true);
    const warrantType = type === '認購買超' ? 'call' : 'put';

    try {
      // 1. 先找出資料庫裡「最新」的日期
      const { data: dateData, error: dateError } = await supabase
        .from('broker_trades')
        .select('date')
        .order('date', { ascending: false })
        .limit(1);

      if (dateError || !dateData || dateData.length === 0) throw new Error("無日期資料");
      const latestDate = dateData[0].date;
      
      // 將 YYYYMMDD 轉成顯示格式
      const dateStr = latestDate.toString();
      setLatestDateText(`${dateStr.substring(4,6)}/${dateStr.substring(6,8)}`);

      // 2. 撈出這一天「所有股票」的指定權證資料
      const { data, error } = await supabase
        .from('broker_trades')
        .select('stock_id, broker_name, buy_amount, sell_amount')
        .eq('date', latestDate)
        .eq('warrant_type', warrantType);

      if (error) throw error;

      // 3. 進行加總排序 (標的 + 券商)
      const rankMap = {};
      data.forEach(trade => {
        const netBuy = trade.buy_amount - trade.sell_amount;
        const key = `${trade.stock_id}_${trade.broker_name}`;
        if (!rankMap[key]) {
          rankMap[key] = { stockId: trade.stock_id, broker: trade.broker_name, netBuy: 0 };
        }
        rankMap[key].netBuy += netBuy;
      });

      // 4. 轉換成陣列、過濾賣超、排序、取前 20 名
      const processedData = Object.values(rankMap)
        .filter(item => item.netBuy > 0)
        .sort((a, b) => b.netBuy - a.netBuy)
        .slice(0, 20);

      setRankingData(processedData);
    } catch (err) {
      console.error("排行榜撈取失敗:", err);
      setRankingData([]);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (activeTab === '權證') {
      fetchSingleStockData(currentStock, activeType, daysFilter);
    } else if (activeTab === '每日主力') {
      fetchMarketRanking(activeType);
    }
  }, [activeTab, activeType, daysFilter, currentStock]);

  const tabs = ['即時', 'K線', '權證', '每日主力'];
  const dayOptions = ['1日', '3日', '5日', '10日'];

  return (
    <div className="flex justify-center items-start sm:items-center min-h-screen bg-black sm:bg-gray-900 font-sans text-white">
      <div className="w-full sm:w-[400px] h-screen sm:h-[800px] bg-[#0A111E] flex flex-col relative sm:shadow-2xl sm:rounded-3xl sm:border sm:border-gray-700 overflow-hidden">
        
        {/* 頂部導航列 (依據 Tab 動態切換) */}
        <div className="flex justify-between items-center px-4 py-3 shrink-0 h-14">
          {activeTab === '每日主力' ? (
             <div className="flex items-center w-full justify-center space-x-2">
               <Trophy size={20} className="text-yellow-500" />
               <span className="text-lg font-bold tracking-wider">全市場主力雷達</span>
               <Trophy size={20} className="text-yellow-500" />
             </div>
          ) : (
            <>
              <button className="text-white hover:bg-gray-800 p-2 -ml-2 rounded-full transition-colors">
                <ChevronLeft size={24} />
              </button>
              {/* 搜尋列 */}
              <div className="flex flex-col items-center flex-1 mx-4">
                <div className="relative w-full max-w-[160px]">
                  <input 
                    type="text" 
                    value={searchStock}
                    onChange={(e) => setSearchStock(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') setCurrentStock(searchStock);
                    }}
                    placeholder="輸入代碼"
                    className="w-full bg-[#1E293B] text-white text-center text-lg font-bold rounded-md py-1 px-8 focus:outline-none focus:ring-1 focus:ring-orange-500 placeholder-gray-500"
                  />
                  <Search size={16} className="absolute left-2 top-2 text-gray-400" />
                </div>
                <span className="text-xs text-gray-400 mt-1">{STOCK_MAP[currentStock] || '未知標的'}</span>
              </div>
              <div className="flex space-x-2">
                <button className="text-orange-500 hover:bg-gray-800 p-2 rounded-full"><Star size={20} fill="#f97316" /></button>
              </div>
            </>
          )}
        </div>

        {/* 主功能分頁 (Tabs) */}
        <div className="flex border-b border-gray-800 shrink-0">
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

        {/* 共用過濾器：買賣超切換 */}
        {(activeTab === '權證' || activeTab === '每日主力') && (
          <div className="flex justify-between items-center px-4 py-3 shrink-0">
            <div className="flex bg-[#121E2F] p-1 rounded-md">
              <button
                onClick={() => setActiveType('認購買超')}
                className={`px-4 py-1.5 text-sm rounded transition-colors ${
                  activeType === '認購買超' ? 'bg-[#1E3A8A] text-white' : 'text-gray-400'
                }`}
              >
                認購買超
              </button>
              <button
                onClick={() => setActiveType('認售買超')}
                className={`px-4 py-1.5 text-sm rounded transition-colors ${
                  activeType === '認售買超' ? 'bg-[#1E3A8A] text-white' : 'text-gray-400'
                }`}
              >
                認售買超
              </button>
            </div>
            
            {activeTab === '權證' ? (
              // 個股的天數下拉選單
              <div className="relative">
                <button 
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center space-x-1 bg-[#121E2F] px-3 py-1.5 rounded-md text-sm text-gray-200"
                >
                  <span>{daysFilter}</span>
                  <ChevronDown size={16} />
                </button>
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-1 w-24 bg-[#1E293B] border border-gray-700 rounded-md z-10 py-1">
                    {dayOptions.map(option => (
                      <button
                        key={option}
                        onClick={() => { setDaysFilter(option); setIsDropdownOpen(false); }}
                        className="w-full text-left px-4 py-2 text-sm hover:bg-gray-700"
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              // 排行榜顯示最新日期
              <div className="text-xs text-orange-400 bg-orange-900/30 px-3 py-1.5 rounded-md border border-orange-800/50">
                最新資料: {latestDateText}
              </div>
            )}
          </div>
        )}

        {}
        <div className="flex-1 overflow-hidden flex flex-col">
          {activeTab === '權證' && (
            <>
              <div className="flex justify-between px-6 py-2 bg-[#121E2F]/80 text-xs text-gray-400 shrink-0 border-y border-gray-800">
                <span>主力分點券商</span>
                <span>淨買超金額(萬元)</span>
              </div>
              <div className="flex-1 overflow-y-auto relative">
                {isLoading ? <LoadingOverlay /> : (
                  <div className="pb-20">
                    {brokerageData.length > 0 ? brokerageData.map((item, index) => (
                      <div key={index} className="flex justify-between items-center px-6 py-3.5 border-b border-gray-800/50">
                        <span className="text-gray-200 text-[15px]">{item.name}</span>
                        <span className="text-[#00E676] font-medium tracking-wide">
                          {item.amount.toLocaleString()}
                        </span>
                      </div>
                    )) : <EmptyState />}
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab === '每日主力' && (
            <>
              <div className="flex justify-between px-6 py-2 bg-[#121E2F]/80 text-xs text-gray-400 shrink-0 border-y border-gray-800">
                <span className="w-1/3">標的名稱</span>
                <span className="w-1/3 text-center">主力分點</span>
                <span className="w-1/3 text-right">淨買超(萬元)</span>
              </div>
              <div className="flex-1 overflow-y-auto relative">
                {isLoading ? <LoadingOverlay /> : (
                  <div className="pb-20">
                    {rankingData.length > 0 ? rankingData.map((item, index) => (
                      <div key={index} className="flex justify-between items-center px-6 py-3 border-b border-gray-800/50 hover:bg-gray-800/30">
                        <div className="w-1/3 flex flex-col">
                          <span className="text-gray-200 font-bold">{STOCK_MAP[item.stockId] || '未知'}</span>
                          <span className="text-gray-500 text-xs">{item.stockId}</span>
                        </div>
                        <span className="w-1/3 text-center text-gray-300 text-[14px] truncate px-1">
                          {item.broker}
                        </span>
                        <span className="w-1/3 text-right text-[#00E676] font-medium">
                          {item.netBuy.toLocaleString()}
                        </span>
                      </div>
                    )) : <EmptyState />}
                  </div>
                )}
              </div>
            </>
          )}

          {activeTab !== '權證' && activeTab !== '每日主力' && (
             <div className="flex-1 flex items-center justify-center text-gray-500">
               {activeTab} 畫面建置中...
             </div>
          )}
        </div>

      </div>
    </div>
  );
}

// 輔助元件
const LoadingOverlay = () => (
  <div className="absolute inset-0 flex flex-col items-center justify-center bg-[#0A111E]/80 z-0">
    <Loader2 className="animate-spin text-orange-500 mb-2" size={32} />
    <span className="text-gray-400 text-sm">載入資料中...</span>
  </div>
);

const EmptyState = () => (
  <div className="flex justify-center items-center h-32 text-gray-500 text-sm">
    查無符合條件之資料
  </div>
);