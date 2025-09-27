import type { Advisory } from "../types";

interface Props {
  advisory: Advisory;
}

function formatDate(value?: string | null): string {
  if (!value) return "";
  try {
    const date = new Date(value);
    return date.toLocaleDateString("zh-TW", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit"
    });
  } catch (error) {
    return value;
  }
}

export function AdvisoryCard({ advisory }: Props) {
  return (
    <article className="advisory-card">
      <header className="advisory-card__header">
        <div>
          <p className="advisory-card__date">{formatDate(advisory.published)}</p>
          <h2 className="advisory-card__title">{advisory.title_zh || advisory.title_en}</h2>
          <p className="advisory-card__subtitle">{advisory.title_en}</p>
        </div>
        <a className="advisory-card__link" href={advisory.link} target="_blank" rel="noreferrer">
          查看原文
        </a>
      </header>
      <section className="advisory-card__section">
        <h3>重點摘要（繁體中文）</h3>
        <p>{advisory.summary_zh || "暫無翻譯"}</p>
      </section>
      <section className="advisory-card__section">
        <h3>重點摘要（English）</h3>
        <p>{advisory.summary_en}</p>
      </section>
    </article>
  );
}
