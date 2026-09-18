// Shared conversion tracking. Plausible is loaded only when the site owner enables it.
(function () {
  function track(eventName, props) {
    if (typeof window.plausible === 'function') {
      window.plausible(eventName, props ? { props: props } : undefined);
    }
  }

  document.addEventListener('click', function (event) {
    var link = event.target.closest('a');
    if (!link) return;

    var href = link.getAttribute('href') || '';
    var label = (link.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    if (href.indexOf('tel:') === 0) track('Phone click', { location: window.location.pathname });
    if (href.indexOf('contact.html') !== -1) track('Quote CTA click', { label: label, page: window.location.pathname });
    if (href.indexOf('case-studies/') !== -1) track('Case study click', { label: label });
  });

  document.addEventListener('submit', function (event) {
    var form = event.target;
    if (form && form.action && form.action.indexOf('formspree.io') !== -1) {
      track('Quote form submit', { page: window.location.pathname });
    }
  });
}());
