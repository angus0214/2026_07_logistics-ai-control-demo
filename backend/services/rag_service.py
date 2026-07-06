import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

VECTOR_STORE_DIR = "./chroma_db"
KNOWLEDGE_DIR = "./knowledge"

_rag_chain = None

def format_docs(docs):
    formatted = []
    for d in docs:
        source_path = d.metadata.get('source', 'Unknown')
        filename = os.path.basename(source_path)
        page = d.metadata.get('page', 'Unknown')
        # PyPDFLoader 的 page 預設是 0-indexed，我們加 1 讓它符合人類閱讀習慣
        page_num = page + 1 if isinstance(page, int) else page
        
        formatted.append(f"[來源: {filename}, 第 {page_num} 頁]\n{d.page_content}")
    return "\n\n---\n\n".join(formatted)

def initialize_vector_db():
    global _rag_chain
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"找不到知識庫資料夾: {KNOWLEDGE_DIR}")
        return

    print(f"載入 {KNOWLEDGE_DIR} 目錄下的所有 PDF 並建立 RAG 向量資料庫中...")
    loader = PyPDFDirectoryLoader(KNOWLEDGE_DIR)
    docs = loader.load()
    
    if not docs:
        print(f"在 {KNOWLEDGE_DIR} 中沒有找到任何 PDF 檔案。")
        return

    # 將長文件切塊 (Chunking)，每塊 1000 字，保留 200 字重疊以維持上下文語意
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 建立 Chroma 向量資料庫並儲存到硬碟
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
        persist_directory=VECTOR_STORE_DIR
    )
    
    # 設定檢索器 (Retriever)，每次抓取最相關的 3 個段落
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 建立語言模型
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 設計 RAG 專屬的 System Prompt
    system_prompt = (
        "你是一個專業的台灣物流與報關法規助手 (OP 法規 Copilot)。\n"
        "請根據以下檢索到的背景知識來回答問題。\n"
        "如果背景知識中找不到答案，請回答「根據目前的法規文件，我找不到相關資訊」。\n"
        "請保持專業且語氣友善，並盡量列點說明。\n\n"
        "⚠️ 重要指示：當你回答問題時，請務必在回答的最後獨立一行，清楚標註你參考的來源檔名與頁碼（根據背景知識提供的標籤）。如果沒有參考資料，則無需標註。\n\n"
        "背景知識：\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])
    
    # 使用更現代的 LCEL (LangChain Expression Language) 語法，避開舊版 chains 模組
    _rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG 引擎初始化完成！可以開始問問題了！")

def get_rag_response(query: str) -> str:
    """
    提供給 API 呼叫的入口函式。
    輸入使用者問題，回傳 AI 根據 PDF 生成的答案。
    """
    if not _rag_chain:
        return "RAG 引擎尚未初始化或找不到知識庫文件。"
    
    return _rag_chain.invoke(query)

def stream_rag_response(query: str):
    """
    以 Streaming 形式回傳 AI 生成的文字片段 (Chunks)。
    交由 FastAPI StreamingResponse 傳遞給前端。
    """
    if not _rag_chain:
        yield "RAG 引擎尚未初始化或找不到知識庫文件。"
        return
    
    # .stream() 會回傳一個產生器，隨著 LLM 運算逐字產出
    for chunk in _rag_chain.stream(query):
        yield chunk
