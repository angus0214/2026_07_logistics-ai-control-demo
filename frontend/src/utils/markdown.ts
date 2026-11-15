import DOMPurify from 'dompurify'
import { marked } from 'marked'

/**
 * 把 LLM 的 Markdown 回答轉成可以放進 v-html 的 HTML。
 *
 * 回答會帶出資料庫內容（包括使用者上傳提單後 OCR 讀出的文字），
 * 所以插入 DOM 前一律用 DOMPurify 過濾，避免儲存型 XSS（ADR-0007）。
 */
export function renderMarkdown(content: string): string {
  if (!content) return ''
  return DOMPurify.sanitize(marked.parse(content, { async: false }))
}
