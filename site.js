// Shared site interactions and form enhancements.
(function () {
  function initializeContactForm() {
    var form = document.querySelector('form[action*="formspree.io"]');
    var service = document.getElementById('service');
    if (!form || !service) return;

    var params = new URLSearchParams(window.location.search);
    var requestedService = params.get('service');
    var serviceAliases = {
      hardscape: 'hardscaping',
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

  function requestedService() {
    var params = new URLSearchParams(window.location.search);
    var aliases = { hardscape: 'hardscaping', lawn: 'lawn-care', maintenance: 'lawn-care' };
    var value = aliases[params.get('service')] || params.get('service') || '';
    return value;
  }

  function serviceFromPage() {
    // Pages can declare their service; falls back to the URL param.
    var declared = document.body.getAttribute('data-service');
    return declared || requestedService();
  }

  function ensureQuoteSheet() {
    if (document.getElementById('quote-sheet') || !document.body) return;

    var backdrop = document.createElement('div');
    backdrop.className = 'quote-sheet-backdrop';
    backdrop.id = 'quote-sheet';
    backdrop.innerHTML =
      '<div class="quote-sheet" role="dialog" aria-modal="true" aria-labelledby="quote-sheet-title">' +
      '  <button type="button" class="quote-sheet-close" aria-label="Close quote form">×</button>' +
      '  <h2 id="quote-sheet-title">Get your free quote</h2>' +
      '  <p class="quote-sheet-sub">Tell us what you need — we\u2019ll follow up to schedule a walkthrough.</p>' +
      '  <div class="quote-sheet-chips" role="radiogroup" aria-label="Service needed">' +
      '    <button type="button" class="chip" data-value="hardscaping" aria-pressed="false">Hardscaping</button>' +
      '    <button type="button" class="chip" data-value="fencing" aria-pressed="false">Fencing</button>' +
      '    <button type="button" class="chip" data-value="lawn-care" aria-pressed="false">Lawn care</button>' +
      '    <button type="button" class="chip" data-value="xeriscaping" aria-pressed="false">Xeriscape</button>' +
      '  </div>' +
      '  <form action="https://formspree.io/f/mjyvregb" method="POST">' +
      '    <input type="hidden" name="_subject" value="Quick quote — Groundwork Landscaping">' +
      '    <input type="hidden" name="_next" value="https://groundworkllc.netlify.app/thank-you.html">' +
      '    <input type="hidden" name="service" value="">' +
      '    <label class="visually-hidden" for="qs-name">Name</label>' +
      '    <input id="qs-name" name="name" type="text" placeholder="Your name" required autocomplete="name">' +
      '    <label class="visually-hidden" for="qs-contact">Phone or email</label>' +
      '    <input id="qs-contact" name="contact" type="text" placeholder="Phone or email" required>' +
      '    <label class="visually-hidden" for="qs-notes">Project notes</label>' +
      '    <textarea id="qs-notes" name="message" rows="2" placeholder="What are you planning? (optional)"></textarea>' +
      '    <button type="submit" class="quote-sheet-send">Send request</button>' +
      '  </form>' +
      '  <a class="quote-sheet-call" href="tel:+17207075411">Or call (720) 707-5411</a>' +
      '</div>';
    document.body.appendChild(backdrop);

    var sheet = backdrop.querySelector('.quote-sheet');
    var chips = Array.prototype.slice.call(backdrop.querySelectorAll('.chip'));
    var serviceInput = backdrop.querySelector('input[name="service"]');
    var lastTrigger = null;

    function selectedService() {
      var active = chips.filter(function (chip) { return chip.getAttribute('aria-pressed') === 'true'; })[0];
      return active ? active.getAttribute('data-value') : '';
    }

    function syncService() {
      serviceInput.value = selectedService();
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var isOn = chip.getAttribute('aria-pressed') === 'true';
        chips.forEach(function (other) { other.setAttribute('aria-pressed', 'false'); });
        chip.setAttribute('aria-pressed', isOn ? 'false' : 'true');
        syncService();
      });
    });

    function preselect() {
      var value = serviceFromPage();
      chips.forEach(function (chip) {
        chip.setAttribute('aria-pressed', chip.getAttribute('data-value') === value ? 'true' : 'false');
      });
      syncService();
    }

    function open() {
      lastTrigger = document.activeElement;
      preselect();
      backdrop.classList.add('open');
      document.body.classList.add('sheet-open');
      var firstField = backdrop.querySelector('input[type="text"]');
      if (firstField) firstField.focus();
    }

    function close() {
      backdrop.classList.remove('open');
      document.body.classList.remove('sheet-open');
      if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus();
      lastTrigger = null;
    }

    backdrop.addEventListener('click', function (event) {
      if (event.target === backdrop) close();
    });
    backdrop.querySelector('.quote-sheet-close').addEventListener('click', close);
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && backdrop.classList.contains('open')) close();
    });

    // Focus trap
    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Tab' || !backdrop.classList.contains('open')) return;
      var focusable = Array.prototype.slice.call(
        backdrop.querySelectorAll('button, [href], input, textarea, [tabindex]:not([tabindex="-1"])')
      ).filter(function (el) { return el.offsetParent !== null; });
      if (!focusable.length) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    });

    var form = backdrop.querySelector('form');
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      syncService();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var sendButton = form.querySelector('.quote-sheet-send');
      sendButton.disabled = true;
      sendButton.textContent = 'Sending…';
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (response) {
        if (!response.ok) throw new Error('failed');
        window.location.href = '/thank-you.html';
      }).catch(function () {
        sendButton.disabled = false;
        sendButton.textContent = 'Send request';
        window.location.href = '/contact.html';
      });
    });

    return { open: open, close: close };
  }

  function ensureMobileCta() {
    if (document.getElementById('mobile-cta') || !document.body) return;

    var bar = document.createElement('div');
    bar.className = 'mobile-cta';
    bar.id = 'mobile-cta';
    bar.setAttribute('aria-label', 'Quick contact');
    bar.innerHTML = '<a href="tel:+17207075411">Call</a>' +
      '<button type="button" class="mobile-cta-quote">Get a quote</button>' +
      '<button type="button" aria-label="Hide quick contact bar">×</button>';
    document.body.appendChild(bar);

    var sheet = ensureQuoteSheet();
    bar.querySelector('.mobile-cta-quote').addEventListener('click', function () {
      if (sheet) sheet.open();
      else window.location.href = '/contact.html';
    });
    bar.querySelector('button[aria-label="Hide quick contact bar"]').addEventListener('click', function () {
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

}());
