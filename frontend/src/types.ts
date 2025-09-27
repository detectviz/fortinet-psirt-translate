export interface Advisory {
  id?: string;
  title_en: string;
  title_zh: string;
  summary_en: string;
  summary_zh: string;
  link?: string;
  published?: string | null;
}

export interface AdvisoryResponse {
  items: Advisory[];
}
