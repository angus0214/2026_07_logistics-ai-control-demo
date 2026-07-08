import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import BossDashboard from '../BossDashboard.vue'

describe('BossDashboard.vue - Text-to-SQL Transparent UI', () => {
  it('should render the thought process block when user submits a query', async () => {
    // 1. Arrange: Mount the component
    // 此時元件甚至還沒建立，所以這行就會報錯（完美的紅燈！）
    const wrapper = mount(BossDashboard)

    // 2. Act: 模擬老闆在對話框輸入文字並點擊送出
    const input = wrapper.find('input[type="text"]')
    await input.setValue('上個月各航空公司的運費總和？')
    await wrapper.find('button.submit-btn').trigger('click')

    // 3. Assert: 驗證前端畫面上是否有出現 FDE 特色的「透明化思考軌跡」區塊
    const thoughtBlock = wrapper.find('.thought-process')
    expect(thoughtBlock.exists()).toBe(true)
    
    // 驗證思考區塊內是否有帶有動畫的 loading 狀態
    expect(thoughtBlock.classes()).toContain('animate-pulse')
  })

  it('should process SSE stream and render both thoughts and final markdown message', async () => {
    // 1. Arrange: Mock the global fetch API to simulate SSE from the backend
    const mockChunks = [
      'data: {"event": "thought", "data": "查詢 bills_of_lading 資料表..."}\n\n',
      'data: {"event": "message", "data": "**總運費**為 $500"}\n\n'
    ]
    
    let chunkIndex = 0
    const mockStream = new ReadableStream({
      pull(controller) {
        if (chunkIndex < mockChunks.length) {
          controller.enqueue(new TextEncoder().encode(mockChunks[chunkIndex]))
          chunkIndex++
        } else {
          controller.close()
        }
      }
    })

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      body: mockStream
    })

    const wrapper = mount(BossDashboard)

    // 2. Act: 輸入並送出
    await wrapper.find('input[type="text"]').setValue('運費多少？')
    await wrapper.find('button.submit-btn').trigger('click')

    // 等待 Vue 的非同步更新 (DOM 渲染) 以及 fetch 的 promise 解決
    await new Promise(resolve => setTimeout(resolve, 50)) // 稍微等待微任務與串流處理

    // 3. Assert: 驗證「思考軌跡區塊」有把 "查詢 bills_of_lading 資料表..." 印出來
    const thoughtBlock = wrapper.find('.thought-process')
    expect(thoughtBlock.exists()).toBe(true)
    expect(thoughtBlock.text()).toContain('查詢 bills_of_lading 資料表...')

    // 驗證最終的 Markdown 訊息有被渲染出來
    // 在真實實作中，我們可能會把它們放在不同的區塊
    const messageBlock = wrapper.find('.message-content')
    expect(messageBlock.exists()).toBe(true)
    expect(messageBlock.text()).toContain('總運費為 $500') // 由於 marked 解析，字眼會純淨保留
  })
})
