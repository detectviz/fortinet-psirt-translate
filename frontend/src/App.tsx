import { useEffect, useMemo, useState } from "react";
import { fetchAdvisories, triggerRefresh, downloadJson } from "./api/advisories";
import type { Advisory } from "./types";
import { AdvisoryCard } from "./components/AdvisoryCard";

interface FetchState {
  items: Advisory[];
  loading: boolean;
  error?: string;
  lastUpdated?: Date;
}

function useAdvisories() {
  const [state, setState] = useState<FetchState>({ items: [], loading: true });

  const load = async (refresh = false) => {
    setState((prev) => ({ ...prev, loading: true, error: undefined }));
    try {
      const response = await fetchAdvisories(refresh);
      setState({
        items: response.items,
        loading: false,
        error: undefined,
        lastUpdated: new Date()
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "載入失敗";
      setState((prev) => ({ ...prev, loading: false, error: message }));
    }
  };

  useEffect(() => {
    void load(false);
  }, []);

  return {
    ...state,
    reload: (refresh = false) => load(refresh)
  };
}

export default function App() {
  const { items, loading, error, lastUpdated, reload } = useAdvisories();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const lastUpdatedText = useMemo(() => {
    if (!lastUpdated) return "--";
    return lastUpdated.toLocaleString("zh-TW");
  }, [lastUpdated]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await triggerRefresh();
      await reload(true);
    } catch (error) {
      console.error(error);
      alert("更新失敗，請稍後再試。");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDownload = async () => {
    try {
      await downloadJson();
    } catch (error) {
      console.error(error);
      alert("下載失敗，請稍後再試。");
    }
  };

  return (
    <div className="page">
      <header className="page__header">
        <div>
          <h1>Fortinet PSIRT 公告翻譯器</h1>
          <p className="page__subtitle">最新安全公告，自動翻譯與整理</p>
        </div>
        <div className="page__actions">
          <button className="button" onClick={() => void reload(true)} disabled={loading}>
            重新整理公告
          </button>
          <button className="button button--primary" onClick={handleDownload}>
            匯出為 JSON
          </button>
        </div>
      </header>

      <section className="status-bar">
        <p>最新更新時間：{lastUpdatedText}</p>
        <div className="status-bar__badges">
          {loading && <span className="badge badge--info">資料載入中…</span>}
          {isRefreshing && <span className="badge badge--info">更新中…</span>}
          {error && <span className="badge badge--error">{error}</span>}
        </div>
        <button className="button button--ghost" onClick={handleRefresh} disabled={isRefreshing}>
          從來源立即更新
        </button>
      </section>

      <main className="page__content">
        {items.map((advisory) => (
          <AdvisoryCard key={advisory.id || advisory.link || advisory.title_en} advisory={advisory} />
        ))}
        {!loading && items.length === 0 && (
          <div className="empty-state">目前尚無公告可顯示。</div>
        )}
      </main>
    </div>
  );
}
