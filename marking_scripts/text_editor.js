function detectTextEditor() {
  const editors = [
    '.kix-appview-editor',
    '.monaco-editor .view-lines',
    '.CodeMirror',
    '.cm-content[contenteditable="true"]',
    '[contenteditable="true"]'
  ];
  for (const sel of editors) {
    const el = document.querySelector(sel);
    if (el) {
      return { XPath: getXPath(el), x: el.getBoundingClientRect().left + 10, y: el.getBoundingClientRect().top + 10 };
    }
  }
  return null;
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
