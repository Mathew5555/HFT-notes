(() => {
  document.querySelectorAll('article table').forEach(table => { const wrapper = document.createElement('div'); wrapper.className = 'table-scroll'; wrapper.tabIndex = 0; wrapper.setAttribute('role','region'); wrapper.setAttribute('aria-label','Таблица — прокрутка по горизонтали'); table.before(wrapper); wrapper.append(table); });
  const links = [...document.querySelectorAll('.contents nav a')];
  if ('IntersectionObserver' in window) { const observer = new IntersectionObserver(entries => { for (const entry of entries) if (entry.isIntersecting) { links.forEach(link => { if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current','location'); else link.removeAttribute('aria-current'); }); } }, {rootMargin:'-5% 0px -65% 0px'}); document.querySelectorAll('article h2[id]').forEach(heading => observer.observe(heading)); }
})();
