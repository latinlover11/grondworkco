// Shared conversion tracking. Plausible is loaded only when the site owner enables it.
(function () {
  function track(eventName, props) {
    if (typeof window.plausible === 'function') {
      window.plausible(eventName, props ? { props: props } : undefined);
    }
  }

  function initializeContactForm() {
    var form = document.querySelector('form[action*="formspree.io"]');
    var service = document.getElementById('service');
    if (!form || !service) return;

    var params = new URLSearchParams(window.location.search);
    var requestedService = params.get('service');
    var serviceAliases = {
      hardscape: 'hardscaping',
      xeriscaping: 'hardscaping',
      lawn: 'lawn-care',
      maintenance: 'lawn-care'
    };
    requestedService = serviceAliases[requestedService] || requestedService;
    if (requestedService && Array.prototype.some.call(service.options, function (option) {
      return option.value === requestedService;
    })) {
      service.value = requestedService;
    }

    var errorBox = document.getElementById('form-error');
    var successBox = document.getElementById('form-success');
    var submitButton = form.querySelector('button[type="submit"]');
    var validationFields = Array.prototype.slice.call(form.querySelectorAll('input:not([type="hidden"]), select, textarea'));

    function showError(message) {
      if (!errorBox) return;
      errorBox.textContent = message;
      errorBox.hidden = false;
    }

    function clearError() {
      if (errorBox) errorBox.hidden = true;
    }

    validationFields.forEach(function (field) {
      field.addEventListener('blur', function () {
        field.setAttribute('aria-invalid', field.validity.valid ? 'false' : 'true');
      });
      field.addEventListener('input', function () {
        if (field.validity.valid) field.setAttribute('aria-invalid', 'false');
        if (validationFields.every(function (item) { return item.validity.valid; })) clearError();
      });
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      clearError();
      validationFields.forEach(function (field) {
        field.setAttribute('aria-invalid', field.validity.valid ? 'false' : 'true');
      });

      if (!form.checkValidity()) {
        showError('Please check the highlighted fields before sending your request.');
        var firstInvalid = validationFields.find(function (field) { return !field.validity.valid; });
        if (firstInvalid) firstInvalid.focus();
        return;
      }

      track('Quote form submit', {
        page: window.location.pathname,
        service: service.value || 'not-selected',
        timeline: (document.getElementById('timeline') || {}).value || 'not-selected'
      });
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Sending…';
      }

      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (response) {
        if (!response.ok) throw new Error('Submission failed');
        form.reset();
        validationFields.forEach(function (field) { field.setAttribute('aria-invalid', 'false'); });
        if (successBox) {
          successBox.hidden = false;
          successBox.focus();
        }
        if (submitButton) submitButton.textContent = 'Request sent';
      }).catch(function () {
        showError('We couldn’t send your request right now. Please try again or call (720) 707-5411.');
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = 'Send request';
        }
      });
    });
  }

  function ensureMobileCta() {
    if (document.getElementById('mobile-cta') || !document.body) return;

    var bar = document.createElement('div');
    bar.className = 'mobile-cta';
    bar.id = 'mobile-cta';
    bar.setAttribute('aria-label', 'Quick contact');
    bar.innerHTML = '<a href="tel:+17207075411">Call</a>' +
      '<a href="/contact.html" class="mobile-cta-quote">Get a quote</a>' +
      '<button type="button" aria-label="Hide quick contact bar">×</button>';
    document.body.appendChild(bar);
    bar.querySelector('button').addEventListener('click', function () {
      bar.hidden = true;
    });
  }

  function enhanceKeyboardAccess() {
    document.querySelectorAll('.nav-mobile-panel').forEach(function (panel) {
      var toggle = document.querySelector('[aria-controls="' + panel.id + '"]');
      function syncPanel() {
        var open = panel.classList.contains('open');
        panel.setAttribute('aria-hidden', open ? 'false' : 'true');
        if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }
      syncPanel();
      new MutationObserver(syncPanel).observe(panel, { attributes: true, attributeFilter: ['class'] });
    });

    document.querySelectorAll('.lightbox-modal').forEach(function (modal) {
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      var closeButton = modal.querySelector('.lightbox-close');
      if (closeButton) closeButton.setAttribute('aria-label', 'Close image viewer');
      var lastTrigger = null;
      new MutationObserver(function () {
        if (modal.classList.contains('open')) {
          lastTrigger = document.activeElement;
          if (closeButton) closeButton.focus();
        } else if (lastTrigger && typeof lastTrigger.focus === 'function') {
          lastTrigger.focus();
          lastTrigger = null;
        }
      }).observe(modal, { attributes: true, attributeFilter: ['class'] });
    });

    document.querySelectorAll('.gallery-card, .main-photo-container img').forEach(function (trigger) {
      if (!trigger.hasAttribute('tabindex')) trigger.setAttribute('tabindex', '0');
      if (!trigger.hasAttribute('role')) trigger.setAttribute('role', 'button');
      trigger.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          trigger.click();
        }
      });
    });

    document.addEventListener('keydown', function (event) {
      var openMenu = document.querySelector('.nav-mobile-panel.open');
      if (event.key === 'Escape' && openMenu) {
        openMenu.classList.remove('open');
        var menuToggle = document.querySelector('[aria-controls="' + openMenu.id + '"]');
        if (menuToggle) menuToggle.focus();
        return;
      }

      var openModal = document.querySelector('.lightbox-modal.open');
      if (!openModal || event.key !== 'Tab') return;
      var focusable = Array.prototype.slice.call(openModal.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])'));
      if (!focusable.length) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      ensureMobileCta();
      initializeContactForm();
      enhanceKeyboardAccess();
    });
  } else {
    ensureMobileCta();
    initializeContactForm();
    enhanceKeyboardAccess();
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
    if (form && form.action && form.action.indexOf('formspree.io') !== -1 && form !== document.querySelector('form[action*="formspree.io"]')) {
      track('Form submit', { page: window.location.pathname });
    }
  });
}());
