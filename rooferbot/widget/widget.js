
(function () {
  const d = document;
  const s = d.currentScript;
  const API = s.getAttribute('data-api');
  let LANG = (s.getAttribute('data-lang') || 'auto').toLowerCase();

  // auto language detection
  if (LANG === 'auto') {
    const nav = (navigator.language || navigator.userLanguage || 'en').toLowerCase();
    LANG = nav.startsWith('de') ? 'de' : 'en';
  }

  const BIZ = s.getAttribute('data-biz') || (LANG==='de' ? 'Ihr Dachdecker' : 'Your Roofer');
  const PRIMARY = s.getAttribute('data-primary') || '#0f766e';
  const ACCENT = s.getAttribute('data-accent') || '#f59e0b';
  const CAL_URL = s.getAttribute('data-cal') || '';
  const PRIV_URL = s.getAttribute('data-privacy') || '#';

  const SID_KEY = 'rooferbot_session';
  let sid = localStorage.getItem(SID_KEY);
  if (!sid) { sid = 'sid_' + Math.random().toString(36).slice(2); localStorage.setItem(SID_KEY, sid); }

  const t = {
    de: {
      chat: 'Chat',
      consent: 'Mit dem Senden stimmen Sie der Verarbeitung Ihrer Angaben gem. Datenschutzhinweisen zu.',
      greet: `Hallo! Ich bin der Assistent von ${BIZ}.
Wie kann ich helfen?
• Sturmschaden/Leck
• Dachsanierung & Preise
• Photovoltaik
• Termin vereinbaren`,
      book: 'Direkt Termin buchen: ',
      error: 'Ups – da ging etwas schief. Bitte später erneut versuchen oder rufen Sie uns an.'
    },
    en: {
      chat: 'Chat',
      consent: 'By sending you agree to the processing of your data according to the privacy policy.',
      greet: `Hi! I am the assistant of ${BIZ}.
How can I help?
• Storm damage / leak
• Re-roofing & prices
• Solar PV
• Book an appointment`,
      book: 'Book appointment: ',
      error: 'Oops — something went wrong. Please try again later or call us.'
    }
  }[LANG];

  const css = `
  .rb-btn{position:fixed;right:16px;bottom:16px;border:none;border-radius:999px;
    padding:14px 16px;font-size:16px;box-shadow:0 6px 24px rgba(0,0,0,.16);
    background:${PRIMARY};color:#fff;cursor:pointer;z-index:999998}
  .rb-wrap{position:fixed;right:16px;bottom:84px;width:360px;max-width:calc(100% - 32px);
    height:520px;max-height:70vh;border-radius:16px;overflow:hidden;background:#fff;
    box-shadow:0 14px 40px rgba(0,0,0,.22);display:none;flex-direction:column;z-index:999999}
  .rb-head{background:${PRIMARY};color:#fff;padding:12px 16px;display:flex;align-items:center;gap:10px}
  .rb-dot{width:10px;height:10px;background:${ACCENT};border-radius:50%}
  .rb-title{font-weight:600}
  .rb-body{flex:1;overflow:auto;padding:12px;background:#fafafa}
  .rb-msg{display:flex;margin:8px 0}
  .rb-msg--bot{justify-content:flex-start}
  .rb-msg--me{justify-content:flex-end}
  .rb-bubble{max-width:78%;padding:10px 12px;border-radius:14px;line-height:1.35;font-size:15px;white-space:pre-wrap}
  .rb-bubble--bot{background:#fff;border:1px solid #eee}
  .rb-bubble--me{background:${PRIMARY};color:#fff}
  .rb-foot{padding:8px;background:#fff;border-top:1px solid #eee;display:flex;gap:8px}
  .rb-input{flex:1;border:1px solid #ddd;border-radius:12px;padding:10px 12px;font-size:15px}
  .rb-send{background:${ACCENT};color:#111;border:none;border-radius:12px;padding:10px 14px;cursor:pointer}
  .rb-consent{font-size:12px;color:#666;padding:0 12px 8px}
  .rb-link{color:${PRIMARY}}
  @media (prefers-reduced-motion: no-preference){.rb-wrap{transition:transform .18s ease, opacity .18s ease}}
  `;
  const style = d.createElement('style'); style.textContent = css; d.head.appendChild(style);

  const btn = d.createElement('button');
  btn.className = 'rb-btn'; btn.setAttribute('aria-haspopup','dialog'); btn.setAttribute('aria-expanded','false');
  btn.title = `${BIZ} Chat`; btn.innerText = t.chat; d.body.appendChild(btn);

  const consentHTML = t.consent.replace('Datenschutzhinweisen', `<a href="${PRIV_URL}" class="rb-link" target="_blank" rel="noopener">Datenschutzhinweisen</a>`)
                               .replace('privacy policy', `<a href="${PRIV_URL}" class="rb-link" target="_blank" rel="noopener">privacy policy</a>`);

  const box = d.createElement('section'); box.className = 'rb-wrap'; box.setAttribute('role','dialog');
  box.setAttribute('aria-label', `${BIZ} Chat`);
  box.innerHTML = `
    <header class="rb-head">
      <span class="rb-dot" aria-hidden="true"></span>
      <div class="rb-title">${BIZ} • ${t.chat}</div>
    </header>
    <main class="rb-body" id="rb-body" tabindex="0" aria-live="polite" aria-atomic="false"></main>
    <div class="rb-consent">${consentHTML}</div>
    <footer class="rb-foot">
      <input id="rb-input" class="rb-input" placeholder="${LANG==='de' ? 'Frage stellen oder Anliegen beschreiben…' : 'Ask a question or describe your issue…'}" autocomplete="off" />
      <button id="rb-send" class="rb-send">${LANG==='de' ? 'Senden' : 'Send'}</button>
    </footer>
  `;
  d.body.appendChild(box);

  const body = box.querySelector('#rb-body');
  const input = box.querySelector('#rb-input');
  const sendBtn = box.querySelector('#rb-send');

  function scrollBottom(){ body.scrollTop = body.scrollHeight; }
  function bubble(text, who='bot'){
    const msg = d.createElement('div'); msg.className = `rb-msg rb-msg--${who==='bot'?'bot':'me'}`;
    const b = d.createElement('div'); b.className = `rb-bubble rb-bubble--${who==='bot'?'bot':'me'}`; b.textContent = text;
    msg.appendChild(b); body.appendChild(msg); scrollBottom();
  }

  function greet(){
    bubble(t.greet);
    if (CAL_URL) bubble((t.book) + CAL_URL);
  }

  async function sendToAPI(text){
    try{
      const res = await fetch(`${API}/chat`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ sid, text, meta:{url:location.href, ua:navigator.userAgent, lang: LANG} })
      });
      if(!res.ok) throw new Error('net');
      const data = await res.json();
      (data.messages||[]).forEach(m=>bubble(m,'bot'));
      if (data.cta && data.cta.url) bubble(`→ ${data.cta.label}: ${data.cta.url}`);
    }catch(e){ bubble(t.error, 'bot'); }
  }

  btn.addEventListener('click', ()=>{
    const visible = box.style.display === 'flex';
    box.style.display = visible ? 'none' : 'flex';
    btn.setAttribute('aria-expanded', String(!visible));
    if (!visible && body.childElementCount===0) greet();
    setTimeout(scrollBottom, 50);
  });

  sendBtn.addEventListener('click', ()=>{
    const v = input.value.trim(); if(!v) return;
    bubble(v,'me'); input.value=''; sendToAPI(v);
  });
  input.addEventListener('keydown', (e)=>{ if(e.key==='Enter') sendBtn.click(); });

  const params = new URLSearchParams(location.search);
  if (params.get('chat')) { btn.click(); }
})();
