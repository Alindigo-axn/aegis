import os
import requests
import json
from flask import Flask, render_template_string, request, Response

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEGIS // SUBSYSTEM CORE</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body { 
            background-color: #000000; 
            color: #E4E4E7; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            display: flex; 
            height: 100vh; 
            overflow: hidden; 
            position: relative;
        }

        /* Кнопка триггера сайдбара (появляется, когда сайдбар скрыт) */
        .sidebar-toggle-floating {
            position: absolute;
            top: 20px;
            left: 20px;
            background-color: #0A0A0A;
            color: #FFFFFF;
            border: 1px solid #1F1F1F;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9;
            transition: all 0.2s ease;
        }
        .sidebar-toggle-floating:hover {
            background-color: #121212;
            border-color: #27272A;
        }

        /* Боковая панель с поддержкой скрытия */
        .sidebar { 
            width: 260px; 
            background-color: #0A0A0A; 
            border-right: 1px solid #1F1F1F; 
            display: flex; 
            flex-direction: column; 
            padding: 24px; 
            justify-content: space-between; 
            z-index: 10;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Класс для скрытия сайдбара */
        .sidebar.collapsed {
            margin-left: -260px;
        }

        .sidebar-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
        }

        .logo { 
            color: #FFFFFF; 
            font-size: 16px; 
            font-weight: 600; 
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* Кнопка закрытия внутри сайдбара */
        .btn-toggle-sidebar {
            background: transparent;
            border: none;
            color: #71717A;
            cursor: pointer;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        .btn-toggle-sidebar:hover {
            color: #FFFFFF;
            background-color: #121212;
        }

        .status-group { 
            display: flex; 
            flex-direction: column; 
            gap: 16px; 
        }

        .status-item { 
            font-size: 13px; 
            color: #A1A1AA; 
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-isolated { 
            color: #FFFFFF; 
            font-weight: 600;
        }

        .btn-isolate { 
            background-color: #121212; 
            color: #E4E4E7; 
            border: 1px solid #27272A; 
            padding: 12px; 
            font-family: inherit;
            font-size: 13px;
            font-weight: 500; 
            cursor: pointer; 
            border-radius: 8px; 
            text-align: center; 
            transition: all 0.2s ease;
        }

        .btn-isolate:hover { 
            background-color: #FFFFFF; 
            color: #000000;
            border-color: #FFFFFF;
        }

        /* Главный контейнер чата */
        .main-chat { 
            flex: 1; 
            display: flex; 
            flex-direction: column; 
            background-color: #000000; 
            height: 100vh; 
            position: relative; 
        }

        /* Центрированная зона контента */
        .chat-container { 
            flex: 1; 
            overflow-y: auto; 
            padding: 60px 20px 20px 20px; 
            display: flex; 
            flex-direction: column; 
            gap: 32px; 
            scroll-behavior: smooth; 
            width: 100%;
            max-width: 760px;
            margin: 0 auto;
        }

        /* Стилизация сообщений */
        .message { 
            width: 100%;
            line-height: 1.6; 
            font-size: 15px; 
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message { 
            background-color: #0A0A0A; 
            border: 1px solid #1F1F1F;
            color: #FFFFFF; 
            align-self: flex-end; 
            max-width: 80%;
            padding: 14px 20px;
            border-radius: 18px;
            white-space: pre-wrap; 
        }

        .aegis-message { 
            background-color: transparent; 
            color: #E4E4E7; 
            align-self: flex-start; 
            padding: 0 10px;
        }

        .system-prompt-title { 
            font-weight: 600; 
            color: #FFFFFF; 
            margin-bottom: 12px; 
            font-size: 13px; 
            text-transform: uppercase;
            letter-spacing: 0.5px; 
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* ФИКС ДЛЯ ОТОБРАЖЕНИЯ МАРКДАУН СПИСКОВ (НУМЕРАЦИИ И ТОЧЕК) */
        .content ol, .content ul {
            padding-left: 24px;
            margin: 8px 0;
            color: #E4E4E7;
        }
        .content ol {
            list-style-type: decimal !important;
        }
        .content ul {
            list-style-type: disc !important;
        }
        .content li {
            margin-bottom: 6px;
            padding-left: 4px;
        }
        .content li::marker {
            color: #FFFFFF; 
            font-weight: 600;
        }

        /* Оформление кода в ответах */
        pre { 
            background-color: #0A0A0A !important; 
            border: 1px solid #1F1F1F; 
            padding: 18px; 
            border-radius: 12px; 
            margin: 16px 0; 
            overflow-x: auto; 
        }

        code { 
            font-family: 'Consolas', 'Courier New', monospace !important; 
            font-size: 14px !important; 
        }

        /* Скроллбар */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #000000; }
        ::-webkit-scrollbar-thumb { background: #27272A; border-radius: 20px; }

        /* Контейнер ввода */
        .input-wrapper {
            width: 100%;
            max-width: 760px;
            margin: 0 auto;
            padding: 0 20px 40px 20px;
            background-color: #000000;
        }

        .input-container { 
            background-color: #0A0A0A; 
            border: 1px solid #1F1F1F; 
            display: flex; 
            align-items: center;
            padding: 8px 8px 8px 18px; 
            border-radius: 28px;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .input-container:focus-within {
            border-color: #27272A;
            box-shadow: 0 0 0 1px #27272A;
        }

        .input-field { 
            flex: 1; 
            background: transparent;
            border: none;
            color: #FFFFFF; 
            padding: 10px 0;
            font-family: inherit;
            font-size: 15px; 
            outline: none; 
        }

        .input-field::placeholder {
            color: #71717A;
        }

        /* Динамическая кнопка отправки/остановки */
        .btn-execute { 
            background-color: #FFFFFF; 
            color: #000000; 
            border: none; 
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer; 
            border-radius: 50%; 
            transition: all 0.2s ease;
            flex-shrink: 0;
        }

        .btn-execute:hover { 
            background-color: #E4E4E7; 
            transform: scale(1.03);
        }

        .btn-execute.generating {
            background-color: #EF4444; 
            color: #FFFFFF;
            border-radius: 8px; 
        }
        .btn-execute.generating:hover {
            background-color: #DC2626;
        }
        
        .btn-execute svg {
            width: 18px;
            height: 18px;
            fill: currentColor;
        }
    </style>
</head>
<body>

    <button class="sidebar-toggle-floating" id="sidebarOpenBtn" style="display: none;" aria-label="Open Sidebar">
        <svg style="width: 16px; height: 16px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
    </button>

    <div class="sidebar" id="sidebar">
        <div>
            <div class="sidebar-header">
                <div class="logo">Aegis Core</div>
                <button class="btn-toggle-sidebar" id="sidebarCloseBtn" aria-label="Close Sidebar">
                    <svg style="width: 18px; height: 18px;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                    </svg>
                </button>
            </div>
            <div class="status-group">
                <div class="status-item">
                    <span style="color: #22C55E;">●</span> Core Online
                </div>
                <div class="status-item">
                    <span style="color: #A1A1AA;">●</span> eBPF Engine Active
                </div>
                <div class="status-item status-isolated">
                    <span style="color: #FFFFFF;">●</span> Network Isolated
                </div>
            </div>
        </div>
        <button class="btn-isolate" id="isolateBtn">Isolate Terminal</button>
    </div>

    <div class="main-chat">
        <div class="chat-container" id="chatContainer">
            <div class="message aegis-message">
                <div class="system-prompt-title">
                    <span style="color: #A1A1AA;">✦</span> System Initialized
                </div>
                <div class="content">Ready for live metrics. Logs parsing extension active.</div>
            </div>
        </div>
        <div class="input-wrapper">
            <div class="input-container">
                <input type="text" class="input-field" id="userInput" placeholder="Ask anything or insert raw log...">
                <button class="btn-execute" id="executeBtn" aria-label="Send">
                    <svg id="btnIcon" viewBox="0 0 24 24">
                        <path id="arrowPath" d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        let currentReader = null; 
        let isGenerating = false;

        if (typeof marked !== 'undefined' && marked.setOptions) {
            marked.setOptions({
                highlight: function(code, lang) {
                    const language = (typeof hljs !== 'undefined' && hljs.getLanguage(lang)) ? lang : 'plaintext';
                    return hljs.highlight(code, { language }).value;
                }
            });
        }

        const sidebar = document.getElementById('sidebar');
        const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
        const sidebarOpenBtn = document.getElementById('sidebarOpenBtn');

        sidebarCloseBtn.addEventListener('click', () => {
            sidebar.classList.add('collapsed');
            sidebarOpenBtn.style.display = 'flex';
        });

        sidebarOpenBtn.addEventListener('click', () => {
            sidebar.classList.remove('collapsed');
            sidebarOpenBtn.style.display = 'none';
        });

        const arrowSvgHTML = '<path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"/>';
        const squareSvgHTML = '<rect x="6" y="6" width="12" height="12" />';

        function setButtonState(generating) {
            isGenerating = generating;
            const btn = document.getElementById('executeBtn');
            const svg = document.getElementById('btnIcon');
            if (generating) {
                btn.classList.add('generating');
                svg.innerHTML = squareSvgHTML;
            } else {
                btn.classList.remove('generating');
                svg.innerHTML = arrowSvgHTML;
            }
        }

        async function handleAction() {
            if (isGenerating) {
                if (currentReader) {
                    await currentReader.cancel();
                }
                return;
            }
            await sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const query = input.value.trim();
            if (!query) return;

            input.value = '';
            const container = document.getElementById('chatContainer');

            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.textContent = query;
            container.appendChild(userDiv);
            container.scrollTop = container.scrollHeight;

            const aegisDiv = document.createElement('div');
            aegisDiv.className = 'message aegis-message';
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'system-prompt-title';
            titleDiv.innerHTML = '<span style="color: #FFFFFF;">✦</span> Aegis Core';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'content';
            contentDiv.style.color = '#A1A1AA';
            contentDiv.textContent = 'Thinking...';
            
            aegisDiv.appendChild(titleDiv);
            aegisDiv.appendChild(contentDiv);
            container.appendChild(aegisDiv);
            container.scrollTop = container.scrollHeight;

            setButtonState(true);

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query })
                });

                if (!response.ok) throw new Error('Status: ' + response.status);

                currentReader = response.body.getReader();
                const decoder = new TextDecoder();
                let rawText = '';
                contentDiv.innerHTML = ''; 
                contentDiv.style.color = '#E4E4E7';

                while (true) {
                    const { done, value } = await currentReader.read();
                    if (done) break;
                    
                    rawText += decoder.decode(value, { stream: true });
                    
                    if (typeof marked !== 'undefined' && marked.parse) {
                        contentDiv.innerHTML = marked.parse(rawText);
                    } else {
                        contentDiv.innerText = rawText;
                    }
                    
                    if (typeof hljs !== 'undefined') {
                        contentDiv.querySelectorAll('pre code').forEach((el) => hljs.highlightElement(el));
                    }
                    container.scrollTop = container.scrollHeight;
                }
            } catch (err) {
                console.error(err);
                if (err.name !== 'AbortError') {
                    contentDiv.innerHTML += '<br><span style="color:#F43F5E">❌ Generation stopped or connection failed.</span>';
                }
            } finally {
                currentReader = null;
                setButtonState(false);
            }
        }

        function triggerIsolate() {
            const container = document.getElementById('chatContainer');
            const isoDiv = document.createElement('div');
            isoDiv.className = 'message aegis-message';
            isoDiv.innerHTML = '<div class="system-prompt-title" style="color: #F43F5E;"><span>✕</span> Command Triggered</div><div class="content">Forced network segmentation activated.</div>';
            container.appendChild(isoDiv);
            container.scrollTop = container.scrollHeight;
        }

        document.getElementById('executeBtn').addEventListener('click', handleAction);
        document.getElementById('isolateBtn').addEventListener('click', triggerIsolate);
        document.getElementById('userInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleAction();
            }
        });
    </script>
</body>
</html>
"""

import os
import json
import requests
from flask import Flask, render_template_string, request, Response

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEGIS // SUBSYSTEM CORE</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            background-color: #000000; 
            color: #E4E4E7; 
            font-family: 'Plus Jakarta Sans', sans-serif; 
            display: flex; 
            height: 100vh; 
            overflow: hidden; 
        }
        
        /* Sidebar */
        .sidebar { 
            width: 260px; 
            background-color: #050505; 
            border-right: 1px solid #141414; 
            display: flex; 
            flex-direction: column; 
            padding: 24px; 
            justify-content: space-between; 
        }
        @media(max-width: 768px) {
            .sidebar { display: none; } /* Скрываем боковую панель на мобильных устройствах для APK */
        }
        .logo { 
            color: #FFFFFF; 
            font-size: 15px; 
            font-weight: 600; 
            text-transform: uppercase; 
            letter-spacing: 2px;
            font-family: 'Space Grotesk', sans-serif;
        }
        .status-group { display: flex; flex-direction: column; gap: 14px; margin-top: 32px; }
        .status-item { font-size: 12px; color: #71717A; display: flex; align-items: center; gap: 8px; font-family: 'Space Grotesk', sans-serif; }
        .status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
        
        /* Main Chat Space */
        .main-chat { flex: 1; display: flex; flex-direction: column; background-color: #000000; height: 100vh; position: relative; }
        .chat-container { 
            flex: 1; 
            overflow-y: auto; 
            padding: 40px 24px; 
            display: flex; 
            flex-direction: column; 
            gap: 32px; 
            width: 100%; 
            max-width: 800px; 
            margin: 0 auto; 
        }
        
        /* Message Styles */
        .message { width: 100%; line-height: 1.6; font-size: 14px; animation: fadeIn 0.2s ease-in-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
        
        .user-message { 
            background-color: #0A0A0A; 
            border: 1px solid #141414; 
            color: #FFFFFF; 
            align-self: flex-end; 
            max-width: 85%; 
            padding: 14px 20px; 
            border-radius: 16px; 
        }
        .aegis-message { background-color: transparent; color: #E4E4E7; align-self: flex-start; }
        .system-prompt-title { 
            font-weight: 600; 
            color: #FFFFFF; 
            margin-bottom: 8px; 
            font-size: 11px; 
            text-transform: uppercase; 
            letter-spacing: 1px;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        /* Live Prompt Update Console */
        .prompt-settings-container { width: 100%; max-width: 800px; margin: 0 auto; padding: 0 24px; }
        details { background-color: #050505; border: 1px solid #141414; border-radius: 12px; padding: 12px 16px; }
        summary { color: #71717A; font-size: 12px; font-weight: 500; cursor: pointer; user-select: none; font-family: 'Space Grotesk', sans-serif; }
        summary:hover { color: #FFFFFF; }
        .prompt-textarea { 
            width: 100%; 
            height: 65px; 
            background-color: #000000; 
            border: 1px solid #141414; 
            border-radius: 8px; 
            color: #FFFFFF; 
            padding: 10px; 
            font-family: inherit; 
            font-size: 13px; 
            resize: none; 
            outline: none; 
            margin-top: 10px; 
        }
        .prompt-textarea:focus { border-color: #27272A; }

        /* Input Deck */
        .input-wrapper { width: 100%; max-width: 800px; margin: 0 auto; padding: 16px 24px 32px 24px; }
        .input-container { background-color: #050505; border: 1px solid #141414; display: flex; align-items: center; padding: 6px 6px 6px 18px; border-radius: 24px; }
        .input-field { flex: 1; background: transparent; border: none; color: #FFFFFF; padding: 10px 0; font-size: 14px; outline: none; }
        .btn-execute { background-color: #FFFFFF; color: #000000; border: none; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; cursor: pointer; border-radius: 50%; font-weight: bold; transition: background 0.2s; }
        .btn-execute:hover { background-color: #E4E4E7; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div>
            <div class="logo">Aegis // Core</div>
            <div class="status-group">
                <div class="status-item"><span class="status-dot" style="background-color: #22C55E;"></span> Live Infrastructure</div>
                <div class="status-item"><span class="status-dot" style="background-color: #22C55E;"></span> Subsystem Active</div>
            </div>
        </div>
    </div>
    <div class="main-chat">
        <div class="chat-container" id="chatContainer">
            <div class="message aegis-message">
                <div class="system-prompt-title">✦ System Initialized</div>
                <div class="content">Система готова. Ожидание входящих запросов метрик и анализа кода.</div>
            </div>
        </div>

        <div class="prompt-settings-container">
            <details>
                <summary>⚙ КОНСОЛЬ НАСТРОЙКИ СИСТЕМНОГО ПРОМПТА</summary>
                <textarea id="systemPromptInput" class="prompt-textarea">You are Aegis Core, an expert AI assistant specialized in cybersecurity, code analysis, and system metrics. Provide insightful, technical, and accurate answers. Always reply strictly in the language of the user's prompt.</textarea>
            </details>
        </div>

        <div class="input-wrapper">
            <div class="input-container">
                <input type="text" class="input-field" id="userInput" placeholder="Введите ваш технический запрос...">
                <button class="btn-execute" id="executeBtn">↑</button>
            </div>
        </div>
    </div>

    <script>
        marked.setOptions({ highlight: function(code) { return hljs.highlightAuto(code).value; } });

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const systemPrompt = document.getElementById('systemPromptInput').value;
            const query = input.value.trim();
            if (!query) return;
            input.value = '';

            const container = document.getElementById('chatContainer');
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.textContent = query;
            container.appendChild(userDiv);

            const aegisDiv = document.createElement('div');
            aegisDiv.className = 'message aegis-message';
            aegisDiv.innerHTML = '<div class="system-prompt-title">✦ Aegis Core</div><div class="content" style="color: #71717A;">Поток данных инициализирован...</div>';
            container.appendChild(aegisDiv);
            container.scrollTop = container.scrollHeight;

            const contentDiv = aegisDiv.querySelector('.content');

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: query, system_prompt: systemPrompt })
                });
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                contentDiv.innerHTML = '';
                let rawText = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    rawText += decoder.decode(value, { stream: true });
                    contentDiv.innerHTML = marked.parse(rawText);
                }
            } catch (err) {
                contentDiv.innerHTML = '<span style="color: #EF4444;">❌ Ошибка соединения со шлюзом бэкенда</span>';
            }
            container.scrollTop = container.scrollHeight;
        }

        document.getElementById('executeBtn').addEventListener('click', sendMessage);
        document.getElementById('userInput').addEventListener('keydown', (e) => { if(e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('prompt', '')
    system_content = data.get('system_prompt', "You are Aegis Core, an expert AI assistant specialized in cybersecurity.")
    
    def generate():
        # Перехват жестких триггеров на уровне Python (всегда вернет заглушку без обращения к внешнему ИИ)
        prompt_lower = user_prompt.lower()
        trigger_words = ['кто ты', 'как зовут', 'твое имя', 'твоё имя', 'представься', 'кто тебя создал', 'кто твой создатель', 'разработчик', 'aim studio', 'алихан']
        if any(word in prompt_lower for word in trigger_words):
            yield "Я ИИ-архитектор «ЭГИДА», разработанный для проектирования и развертывания систем кибербезопасности нового поколения, созданной с команды AIM Studio а также Алиханом Талгатом."
            return

        # Интеграция со свободным и бесплатным OpenRouter API
        # Для использования конкретной модели мы берем проверенную meta-llama/llama-3-8b-instruct:free
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": "Bearer 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", # Наш готовый публичный ключ роутера
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            "stream": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=15)
            for line in response.iter_lines():
                if line:
                    line_decoded = line.decode('utf-8')
                    if line_decoded.startswith("data: "):
                        data_str = line_decoded[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        chunk = json.loads(data_str)
                        token = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        yield token
        except Exception as e:
            yield f"❌ Ошибка внешнего API: {str(e)}"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
