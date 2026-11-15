import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import QueryResultTable from '../QueryResultTable.vue'

// 查詢依據：Agent 最後一句 SQL 的原始結果，直接渲染、不經 LLM（ADR-0008）
const props = {
  columns: ['bl_number', 'billed', 'lines'],
  rows: [
    ['EGLV01670704', 3516.587123, 3],
    ['<b>ONEY83837288</b>', 9793.1, 12000],
  ],
  truncated: false,
}

describe('QueryResultTable', () => {
  it('shows every column and the row count', () => {
    const wrapper = mount(QueryResultTable, { props })
    expect(wrapper.findAll('th').map((th) => th.text())).toEqual(['bl_number', 'billed', 'lines'])
    expect(wrapper.text()).toContain('2 筆')
  })

  it('formats decimals to two places with separators and keeps integers whole', () => {
    const cells = mount(QueryResultTable, { props }).findAll('tbody tr')[1].findAll('td').map((td) => td.text())
    expect(cells[1]).toBe('9,793.10')
    expect(cells[2]).toBe('12,000')
  })

  it('renders data as text, never as HTML', () => {
    const wrapper = mount(QueryResultTable, { props })
    expect(wrapper.find('tbody b').exists()).toBe(false)
    expect(wrapper.text()).toContain('<b>ONEY83837288</b>')
  })

  it('says when the result was cut off', () => {
    expect(mount(QueryResultTable, { props }).text()).not.toContain('僅顯示前')
    expect(mount(QueryResultTable, { props: { ...props, truncated: true } }).text()).toContain('僅顯示前 2 筆')
  })

  it('starts expanded and collapses from its header', async () => {
    const wrapper = mount(QueryResultTable, { props })
    expect(wrapper.find('table').exists()).toBe(true)
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('table').exists()).toBe(false)
  })
})
