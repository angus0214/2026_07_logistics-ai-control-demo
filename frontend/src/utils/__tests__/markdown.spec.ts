import { describe, expect, it } from 'vitest'
import { renderMarkdown } from '../markdown'

// LLM 回答會帶出資料庫內容（含使用者上傳提單的 OCR 文字），插入 DOM 前必須過濾（ADR-0007）
describe('renderMarkdown', () => {
  it('still renders lists, bold text and tables', () => {
    const html = renderMarkdown('**注意**\n\n- 第一點\n\n| 提單號 | 運費 |\n|---|---|\n| EGLV1 | 100 |')
    expect(html).toContain('<strong>注意</strong>')
    expect(html).toContain('<li>第一點</li>')
    expect(html).toContain('<table>')
    expect(html).toContain('<td>EGLV1</td>')
  })

  it('removes script tags', () => {
    expect(renderMarkdown('託運人 <script>alert(1)</script>Apple')).not.toContain('<script')
  })

  it('removes inline event handlers', () => {
    const html = renderMarkdown('<img src="x" onerror="alert(1)">')
    expect(html).not.toContain('onerror')
  })

  it('removes javascript: links', () => {
    expect(renderMarkdown('[點我](javascript:alert(1))')).not.toContain('javascript:')
  })

  it('treats empty content as empty', () => {
    expect(renderMarkdown('')).toBe('')
  })
})
