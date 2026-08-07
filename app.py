from flask import Flask, send_file, jsonify, request
from flask_socketio import SocketIO, emit
import feedparser
import requests
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import re

import sys

def get_base_path():
    """Retorna o caminho base do projeto (funciona em dev e no PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller empacota em uma pasta temporaria
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

app = Flask(__name__, static_folder=BASE_PATH, template_folder=BASE_PATH)
app.config['SECRET_KEY'] = 'crawl-tv-evangelizar-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

CONFIG_FILE = 'config.json'
HISTORY_FILE = 'quotes_history.json'

# Estado compartilhado em memória (sincronizado entre todos os clientes)
shared_state = {
    "approved": [],      # lista ordenada de títulos aprovados
    "rejected": set(),   # conjunto de títulos rejeitados
    "quotes": []         # cotações atuais
}

DEFAULT_CONFIG = {
    "rss_feeds": [
        {"url": "https://g1.globo.com/rss/g1/economia/", "name": "G1 Economia", "category": "Economia"},
        {"url": "https://g1.globo.com/rss/g1/politica/", "name": "G1 Política", "category": "Política"},
        {"url": "https://www.canalrural.com.br/feed/", "name": "Canal Rural", "category": "Agronegócio"},
        {"url": "https://www.noticiasagricolas.com.br/rss.php", "name": "Notícias Agrícolas", "category": "Agronegócio"},
        {"url": "https://g1.globo.com/rss/g1/ciencia-e-saude/", "name": "G1 Ciência", "category": "Ciência"},
        {"url": "https://g1.globo.com/rss/g1/tecnologia/", "name": "G1 Tecnologia", "category": "Tecnologia"}
    ],
    "export_path": "C:\\GC\\crawl\\noticias_crawl.txt",
    "commodity_mode": "auto",
    "manual_quotes": {},
    "active_categories": ["Economia", "Política", "Agronegócio", "Ciência", "Tecnologia"]
}

def load_json(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_config():
    return load_json(CONFIG_FILE, DEFAULT_CONFIG.copy())

def save_config(config):
    save_json(CONFIG_FILE, config)

def load_history():
    return load_json(HISTORY_FILE, {})

def save_history(history):
    save_json(HISTORY_FILE, history)

def get_currency_quotes():
    quotes = []
    try:
        resp = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL', timeout=15)
        data = resp.json()
        history = load_history()
        today = datetime.now().strftime('%Y-%m-%d')
        for code, label in [('USDBRL', 'Dólar'), ('EURBRL', 'Euro')]:
            item = data.get(code, {})
            value = float(item.get('bid', 0))
            prev = value
            hist_key = label.lower()
            if hist_key in history and history[hist_key].get('date') != today:
                prev = history[hist_key]['value']
            elif 'pctChange' in item and float(item.get('pctChange', 0)) != 0:
                pct = float(item.get('pctChange', 0)) / 100
                prev = value / (1 + pct)
            quotes.append({"label": label, "value": value, "prev": prev, "unit": "R$", "type": "currency"})
            history[hist_key] = {"date": today, "value": value}
        save_history(history)
    except Exception as e:
        print(f"Erro moedas: {e}")
    return quotes

def get_commodity_quotes():
    from bs4 import BeautifulSoup
    quotes = []
    history = load_history()
    today = datetime.now().strftime('%Y-%m-%d')
    commodities = [
        {"label": "Soja (saca 60kg)", "unit": "R$", "url": "https://cepea.org.br/br/indicador/soja.aspx", "table_index": 0, "col_value": 1, "col_var": 2},
        {"label": "Milho (saca 60kg)", "unit": "R$", "url": "https://cepea.org.br/br/indicador/milho.aspx", "table_index": 0, "col_value": 1, "col_var": 2},
        {"label": "Trigo (saca 60kg)", "unit": "R$", "url": "https://cepea.org.br/br/indicador/trigo.aspx", "table_index": 0, "col_value": 1, "col_var": 2, "is_ton": True},
        {"label": "Boi gordo (@)", "unit": "R$", "url": "https://cepea.org.br/br/indicador/boi-gordo.aspx", "table_index": 0, "col_value": 1, "col_var": 2}
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': 'https://cepea.org.br/',
    }
    session = requests.Session()
    for comm in commodities:
        try:
            resp = session.get(comm['url'], headers=headers, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            tables = soup.find_all('table')
            if not tables: continue
            table_idx = comm.get('table_index', 0)
            if table_idx >= len(tables): table_idx = 0
            table = tables[table_idx]
            rows = table.find_all('tr')
            if len(rows) < 2: continue
            data_row = rows[1]
            cells = data_row.find_all(['td', 'th'])
            if len(cells) <= comm['col_value']: continue
            value_text = cells[comm['col_value']].get_text(strip=True)
            value_text = value_text.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            value = float(value_text)
            if comm.get('is_ton'): value = value / 16.67
            prev = value
            if len(cells) > comm['col_var']:
                var_text = cells[comm['col_var']].get_text(strip=True)
                var_match = re.search(r'([+-]?[\d.,]+)%', var_text)
                if var_match:
                    var_str = var_match.group(1).replace('.', '').replace(',', '.')
                    var_pct = float(var_str) / 100
                    prev = value / (1 + var_pct)
            hist_key = comm['label'].lower().replace(' ', '_').replace('(', '').replace(')', '')
            if hist_key in history and history[hist_key].get('date') != today:
                prev = history[hist_key]['value']
            quotes.append({"label": comm['label'], "value": round(value, 2), "prev": round(prev, 2), "unit": comm['unit'], "type": "commodity", "source": "CEPEA"})
            history[hist_key] = {"date": today, "value": round(value, 2)}
            print(f"[OK] {comm['label']}: R$ {value:.2f}")
        except Exception as e:
            print(f"[ERRO] {comm['label']}: {e}")
    save_history(history)
    return quotes

@app.route('/')
def index():
    return send_file(os.path.join(BASE_PATH, 'index.html'))

@app.route('/api/config', methods=['GET', 'POST'])
def config_route():
    if request.method == 'POST':
        data = request.json
        save_config(data)
        return jsonify({"status": "ok"})
    return jsonify(load_config())

@app.route('/api/news')
def get_news():
    config = load_config()
    all_news = []
    seen = set()
    active_cats = set(config.get('active_categories', []))
    for feed_info in config.get('rss_feeds', []):
        cat = feed_info.get('category', 'Geral')
        if cat not in active_cats: continue
        try:
            feed = feedparser.parse(feed_info['url'])
            for entry in feed.entries[:15]:
                title = entry.get('title', '').strip()
                if title and title not in seen:
                    seen.add(title)
                    all_news.append({"id": len(seen), "title": title, "source": feed.feed.get('title', feed_info.get('name', 'Desconhecido')), "link": entry.get('link', ''), "published": entry.get('published', entry.get('updated', '')), "category": cat})
        except Exception as e: print(f"Erro feed: {e}")
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    total = len(all_news)
    start = (page - 1) * per_page
    end = start + per_page
    return jsonify({"items": all_news[start:end], "total": total, "page": page, "per_page": per_page, "pages": (total + per_page - 1) // per_page})

@app.route('/api/quotes')
def get_quotes():
    config = load_config()
    if config.get('commodity_mode') == 'manual':
        manual = config.get('manual_quotes', {})
        quotes = []
        for key, val in manual.items():
            quotes.append({"label": key, "value": float(val.get('value', 0)), "prev": float(val.get('prev', 0)), "unit": val.get('unit', 'R$'), "type": val.get('type', 'commodity')})
        shared_state["quotes"] = quotes
        return jsonify(quotes)
    quotes = get_currency_quotes()
    quotes.extend(get_commodity_quotes())
    shared_state["quotes"] = quotes
    return jsonify(quotes)

@app.route('/api/export', methods=['POST'])
def export():
    data = request.json
    config = load_config()
    path = data.get('path', config.get('export_path'))
    approved_news = data.get('news', [])
    quotes = data.get('quotes', [])
    def fmt_br(val):
        s = f"{val:,.2f}"
        s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
        return s
    q_parts = []
    for q in quotes:
        diff = q['value'] - q['prev']
        arrow = '■' if abs(diff) < 0.01 else ('▲' if diff > 0 else '▼')
        val_str = f"{q['unit']} {fmt_br(q['value'])}"
        q_parts.append(f"{q['label']}: {val_str} {arrow}")
    q_line = ' | '.join(q_parts)
    news_parts = [f"• {n['title']}" for n in approved_news]
    news_line = ' '.join(news_parts)
    content = (q_line + ' • ' + news_line).upper()
    errors = []
    try:
        dir_path = os.path.dirname(path)
        if dir_path: os.makedirs(dir_path, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f: f.write(content)
        return jsonify({"status": "ok", "path": path, "content": content})
    except PermissionError as e:
        errors.append(f"Sem permissão: {path}")
    except Exception as e: errors.append(str(e))
    try:
        fallback_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.basename(path))
        with open(fallback_path, 'w', encoding='utf-8') as f: f.write(content)
        return jsonify({"status": "ok", "path": fallback_path, "content": content, "warning": f"Salvo na pasta do programa. Não foi possível salvar em: {path}"})
    except Exception as e: errors.append(str(e))
    try:
        import tempfile
        temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(path))
        with open(temp_path, 'w', encoding='utf-8') as f: f.write(content)
        return jsonify({"status": "ok", "path": temp_path, "content": content, "warning": f"Salvo na pasta temporária. Não foi possível salvar em: {path}"})
    except Exception as e: errors.append(str(e))
    return jsonify({"status": "fallback", "message": "Não foi possível salvar. Use o botão Baixar.", "content": content, "errors": errors}), 200

@app.route('/api/save-quotes', methods=['POST'])
def save_quotes():
    data = request.json
    config = load_config()
    config['manual_quotes'] = data.get('quotes', {})
    config['commodity_mode'] = data.get('mode', 'auto')
    save_config(config)
    return jsonify({"status": "ok"})

# ===== SOCKET.IO — SINCRONIZAÇÃO EM TEMPO REAL =====

@socketio.on('connect')
def handle_connect():
    print(f'Cliente conectado: {request.sid}')
    # Envia estado atual para o novo cliente
    emit('sync_state', {
        "approved": shared_state["approved"],
        "rejected": list(shared_state["rejected"])
    })

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('approve_item')
def handle_approve(data):
    title = data.get('title')
    if title and title not in shared_state["approved"]:
        shared_state["approved"].append(title)
    if title in shared_state["rejected"]:
        shared_state["rejected"].discard(title)
    emit('state_update', {
        "approved": shared_state["approved"],
        "rejected": list(shared_state["rejected"])
    }, broadcast=True)

@socketio.on('reject_item')
def handle_reject(data):
    title = data.get('title')
    if title:
        shared_state["rejected"].add(title)
    if title in shared_state["approved"]:
        shared_state["approved"].remove(title)
    emit('state_update', {
        "approved": shared_state["approved"],
        "rejected": list(shared_state["rejected"])
    }, broadcast=True)

@socketio.on('remove_item')
def handle_remove(data):
    title = data.get('title')
    if title in shared_state["approved"]:
        shared_state["approved"].remove(title)
    if title in shared_state["rejected"]:
        shared_state["rejected"].discard(title)
    emit('state_update', {
        "approved": shared_state["approved"],
        "rejected": list(shared_state["rejected"])
    }, broadcast=True)

@socketio.on('reorder_items')
def handle_reorder(data):
    new_order = data.get('order', [])
    # Mantém apenas os que ainda estão aprovados
    shared_state["approved"] = [t for t in new_order if t in shared_state["approved"]]
    emit('state_update', {
        "approved": shared_state["approved"],
        "rejected": list(shared_state["rejected"])
    }, broadcast=True)

@socketio.on('clear_all')
def handle_clear():
    shared_state["approved"] = []
    shared_state["rejected"] = set()
    emit('state_update', {
        "approved": [],
        "rejected": []
    }, broadcast=True)

if __name__ == '__main__':
    print('=' * 50)
    print('  CRAWL TV EVANGELIZAR — ONLINE')
    print('  Acesse: http://localhost:5000')
    print('  Para acessar de outra máquina: http://IP_DA_MAQUINA:5000')
    print('  Pressione CTRL+C para encerrar')
    print('=' * 50)
    socketio.run(app, debug=False, port=5000, host='0.0.0.0')
