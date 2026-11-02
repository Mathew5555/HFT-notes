(() => {
  'use strict';
  const catalog = window.HFT_CATALOG || [];
  const home = document.getElementById('home-view');
  const topics = document.getElementById('topics-view');
  const buttons = document.getElementById('section-buttons');
  const list = document.getElementById('topic-list');
  const search = document.getElementById('topic-search');
  const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');
  const icons = {
    ml: '<circle cx="12" cy="12" r="3"/><path d="M12 1v5m0 12v5M1 12h5m12 0h5M4 4l4 4m8 8 4 4M4 20l4-4m8-8 4-4"/>',
    infrastructure: '<rect x="4" y="3" width="16" height="7" rx="2"/><rect x="4" y="14" width="16" height="7" rx="2"/><path d="M8 6.5h.1m0 11h.1M12 6.5h5m-5 11h5"/>',
    'strategy-research': '<path d="M3 19V5m0 14h18M6 15l4-5 4 2 6-8"/><path d="M16 4h4v4"/>',
    contributing: '<path d="M14 3H5v18h14v-9M10 14l1-4 7-7 3 3-7 7-4 1Z"/>'
  };
  catalog.forEach((section, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'section-button';
    const icon = document.createElement('span');
    icon.className = 'icon'; icon.setAttribute('aria-hidden', 'true');
    icon.innerHTML = '<svg viewBox="0 0 24 24">' + (icons[section.id] || icons.ml) + '</svg>';
    const title = document.createElement('span'); title.className = 'button-title'; title.textContent = section.title;
    const arrow = document.createElement('span'); arrow.className = 'arrow'; arrow.textContent = '↗'; arrow.setAttribute('aria-hidden', 'true');
    button.append(icon, title, arrow);
    button.addEventListener('click', () => { location.hash = section.id; });
    buttons.append(button);
  });
  let currentSection = null;
  let routeRevision = 0;
  let activeView = home;
  function renderTopics() {
    list.replaceChildren();
    if (!currentSection) return;
    const query = search.value.trim().toLocaleLowerCase('ru');
    const shown = currentSection.pages.filter(page => (page.title + ' ' + page.description).toLocaleLowerCase('ru').includes(query));
    shown.forEach((page, index) => {
      const row = document.createElement('li'); row.className = 'topic-row'; row.style.setProperty('--i', Math.min(index, 12));
      const link = document.createElement(page.ready ? 'a' : 'div');
      if (page.ready) { link.href = page.url; link.setAttribute('aria-label', page.title); }
      else { link.className = 'upcoming'; }
      const number = document.createElement('span'); number.className = 'topic-number'; number.textContent = String(page.number).padStart(2, '0');
      const text = document.createElement('span');
      const title = document.createElement('span'); title.className = 'topic-name'; title.textContent = page.title; text.append(title);
      if (page.description) { const summary = document.createElement('span'); summary.className = 'topic-summary'; summary.textContent = page.description; text.append(summary); }
      const ending = document.createElement('span'); ending.className = page.ready ? 'topic-arrow' : 'soon-tag'; ending.textContent = page.ready ? '→' : 'Скоро';
      if (page.ready) ending.setAttribute('aria-hidden', 'true');
      link.append(number, text, ending); row.append(link); list.append(row);
    });
    document.getElementById('empty-search').hidden = shown.length !== 0 || currentSection.pages.length === 0;
    document.getElementById('empty-section').hidden = currentSection.pages.length !== 0;
    const ready = currentSection.pages.filter(p => p.ready).length;
    document.getElementById('topic-count').textContent = query ? 'Найдено: ' + shown.length : 'Всего тем: ' + currentSection.pages.length + ' · Доступно: ' + ready;
  }
  async function route(initial = false) {
    const revision = ++routeRevision;
    let id = ''; try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { /* Invalid fragment opens the home view. */ }
    const section = catalog.find(item => item.id === id);
    const nextView = section ? topics : home;
    if (!initial && !motionQuery.matches) {
      await activeView.animate([{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(-14px)'}], {duration:190,easing:'ease-in',fill:'forwards'}).finished.catch(() => {});
    }
    if (revision !== routeRevision) return;
    activeView.getAnimations().forEach(animation => animation.cancel());
    home.hidden = nextView !== home; topics.hidden = nextView !== topics;
    currentSection = section || null;
    if (section) {
      document.getElementById('topics-title').textContent = section.title;
      document.getElementById('section-label').textContent = section.label;
      document.getElementById('section-mark').textContent = String(catalog.indexOf(section) + 1).padStart(2, '0');
      search.value = ''; renderTopics();
      document.title = section.title + ' · HFT Notes';
    } else { document.title = 'Пространство знаний · HFT Notes'; }
    activeView = nextView;
    window.scrollTo({top:0,behavior:'instant'});
    if (!initial && !motionQuery.matches) nextView.animate([{opacity:0,transform:'translateY(18px)'},{opacity:1,transform:'translateY(0)'}],{duration:470,easing:'cubic-bezier(.2,.8,.2,1)'});
    if (!initial) {
      if (section) document.getElementById('topics-title').focus({preventScroll:true});
      else buttons.querySelector('button')?.focus({preventScroll:true});
    }
  }
  search.addEventListener('input', renderTopics);
  document.getElementById('back').addEventListener('click', () => { location.hash = ''; });
  window.addEventListener('hashchange', () => route());
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && currentSection) location.hash = ''; });
  route(true);

  // Keep the cloud texture in compositor layers instead of repainting a canvas.
  const sky = document.getElementById('sky');
  const toggle = document.getElementById('motion-toggle');
  let paused = motionQuery.matches, pointerFrame = 0, hoverTimer = 0;
  const pointer = {x: 0, y: 0};
  const clouds = [
    {x:-.53,y:-.33,w:1.12,h:.88,v:.026,a:.80,s:0,depth:.35},
    {x:.55,y:-.32,w:1.13,h:.88,v:-.024,a:.88,s:2,depth:.45},
    {x:-.67,y:.05,w:1.15,h:1.0,v:.030,a:.96,s:1,depth:.8},
    {x:.53,y:.16,w:1.16,h:1.02,v:-.028,a:.97,s:0,depth:1},
    {x:-.46,y:.56,w:1.36,h:.85,v:.033,a:1,s:2,depth:1.5},
    {x:.24,y:.65,w:1.35,h:.82,v:-.030,a:1,s:1,depth:1.8}
  ];
  const drifts = clouds.map(cloud => {
    const layer = document.createElement('div');
    layer.className = 'cloud-layer';
    Object.assign(layer.style, {
      left: `${cloud.x * 100}%`, top: `${cloud.y * 100}%`,
      width: `${cloud.w * 100}%`, height: `${cloud.h * 100}%`, opacity: cloud.a,
      transformOrigin: `${(.5 - cloud.x) / cloud.w * 100}% ${(.5 - cloud.y) / cloud.h * 100}%`
    });
    layer.style.setProperty('--depth', cloud.depth);
    layer.style.setProperty('--hover-scale', 1 + .1 * cloud.depth);
    const image = document.createElement('img');
    image.src = 'assets/cloud-bank.png';
    image.alt = ''; image.draggable = false; image.decoding = 'async';
    layer.append(image); sky.append(layer);
    const flip = cloud.s === 1 ? -1 : 1;
    // A closed loop with eased extrema approximates the previous sine drift.
    const positions = [0, 1, 0, -1, 0];
    const frames = positions.map((position, index) => ({
      transform: `translate3d(${position * Math.sign(cloud.v) * 3.5}vw, ${Math.sin(index * Math.PI / 2 + cloud.s) * 6}px, 0) scaleX(${flip})`,
      easing: 'cubic-bezier(.37,0,.63,1)'
    }));
    const animation = image.animate(frames, {duration: 2 * Math.PI / Math.abs(cloud.v) * 1000, iterations: Infinity});
    animation.pause();
    return animation;
  });
  function applyPointer() {
    pointerFrame = 0;
    sky.style.setProperty('--pointer-x', `${-pointer.x * 70}px`);
    sky.style.setProperty('--pointer-y', `${-pointer.y * 46}px`);
  }
  function schedulePointer() {
    if (!paused && !document.hidden && !pointerFrame) pointerFrame = requestAnimationFrame(applyPointer);
  }
  document.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch' || paused) return;
    pointer.x = (event.clientX / innerWidth - .5) * 2;
    pointer.y = (event.clientY / innerHeight - .5) * 2;
    schedulePointer();
  }, {passive: true});
  document.documentElement.addEventListener('pointerleave', () => {
    pointer.x = pointer.y = 0;
    schedulePointer();
  });
  const interactiveSelector = '.section-button,.topic-row a,.back-button,.classic-link';
  function updateHover() {
    hoverTimer = 0;
    const overControl = document.querySelector(`${interactiveSelector.split(',').map(s => `${s}:hover`).join(',')},${interactiveSelector.split(',').map(s => `${s}:focus-visible`).join(',')}`);
    sky.classList.toggle('is-interactive', !paused && !document.hidden && !!overControl);
  }
  function scheduleHover() {
    // Coalesce focusout/focusin and pointerout/pointerover into one target.
    if (!hoverTimer) hoverTimer = setTimeout(updateHover, 0);
  }
  ['pointerover', 'pointerout', 'focusin', 'focusout'].forEach(type => document.addEventListener(type, scheduleHover));
  function updateMotion() {
    toggle.setAttribute('aria-pressed', String(paused));
    document.getElementById('motion-label').textContent = paused ? 'Включить движение' : 'Остановить облака';
    toggle.querySelector('.motion-icon').textContent = paused ? '▷' : 'Ⅱ';
    const running = !paused && !document.hidden;
    sky.classList.toggle('is-paused', !running);
    drifts.forEach(animation => running ? animation.play() : animation.pause());
    if (!running) { cancelAnimationFrame(pointerFrame); pointerFrame = 0; }
    else schedulePointer();
    updateHover();
  }
  toggle.addEventListener('click', () => { paused = !paused; updateMotion(); });
  document.addEventListener('visibilitychange', updateMotion);
  motionQuery.addEventListener('change', event => { paused = event.matches; updateMotion(); });
  updateMotion();
})();
