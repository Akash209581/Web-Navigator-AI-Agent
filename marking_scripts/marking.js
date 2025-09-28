function captureInteractiveElements() {
  const results = [];
  const toRect = (el) => (el.getBoundingClientRect ? el.getBoundingClientRect() : {x:0,y:0});
  const pushEl = (el, type, description) => {
    const r = el.getBoundingClientRect();
    const x = r.left + r.width/2;
    const y = r.top + r.height/2;
    results.push({
      index: results.length,
      text: (el.innerText || el.value || '').trim().slice(0,200),
      type,
      xpath: getXPath(el),
      x, y,
      description: description || el.getAttribute('aria-label') || el.getAttribute('title') || '',
      inViewport: !!(r.top >= 0 && r.left >= 0 && r.bottom <= (window.innerHeight||document.documentElement.clientHeight) && r.right <= (window.innerWidth||document.documentElement.clientWidth))
    });
  };

  document.querySelectorAll('a,button,input,textarea,[role="button"],[contenteditable="true"]').forEach(el => {
    const tag = el.tagName.toLowerCase();
    let type = tag;
    if (tag === 'a') type = 'link';
    if (el.isContentEditable) type = 'text_editor';
    pushEl(el, type, undefined);
  });
  return results;
}

function getXPath(element) {
  if (element.id) return `//*[@id='${element.id}']`;
  const parts = [];
  while (element && element.nodeType === Node.ELEMENT_NODE) {
    let nb = 0, idx = 0;
    const siblings = element.parentNode ? element.parentNode.children : [];
    for (let i=0;i<siblings.length;i++) {
      const sib = siblings[i];
      if (sib.nodeName === element.nodeName) {
        nb++;
        if (sib === element) idx = nb;
      }
    }
    const tagName = element.nodeName.toLowerCase();
    const nth = idx > 1 ? `[${idx}]` : '';
    parts.unshift(`${tagName}${nth}`);
    element = element.parentNode;
  }
  return '//' + parts.join('/');
}

function unmarkElements() {
  // noop placeholder to match remover scripts
}
