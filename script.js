/* =====================================================
   HAWAII UNCLAIMED FUNDS RECOVERY
   Main JavaScript — script.js
   ===================================================== */

// ⚠️ PASTE YOUR REAL FORMSPREE ENDPOINT HERE before going live
var FORMSPREE_ENDPOINT = 'https://formspree.io/f/xnjylrgj';

document.addEventListener('DOMContentLoaded', function () {
  initStickyNav();
  initMobileMenu();
  initFaqAccordion();
  initForms();
  initScrollAnimations();
  setActiveNavLink();
  initSmoothScroll();
});

/* ---- Sticky Navigation ---- */
function initStickyNav() {
  var nav = document.querySelector('.site-nav');
  if (!nav) return;

  window.addEventListener('scroll', function () {
    if (window.scrollY > 10) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }, { passive: true });
}

/* ---- Mobile Menu ---- */
function initMobileMenu() {
  var hamburger = document.querySelector('.hamburger');
  var mobileMenu = document.querySelector('.mobile-menu');
  if (!hamburger || !mobileMenu) return;

  function openMenu() {
    hamburger.classList.add('open');
    mobileMenu.classList.add('open');
    document.body.classList.add('menu-open');
    hamburger.setAttribute('aria-expanded', 'true');
  }

  function closeMenu() {
    hamburger.classList.remove('open');
    mobileMenu.classList.remove('open');
    document.body.classList.remove('menu-open');
    hamburger.setAttribute('aria-expanded', 'false');
  }

  hamburger.addEventListener('click', function () {
    mobileMenu.classList.contains('open') ? closeMenu() : openMenu();
  });

  // Close on link click
  mobileMenu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });
}

/* ---- FAQ Accordion ---- */
function initFaqAccordion() {
  var items = document.querySelectorAll('.faq-item');
  if (!items.length) return;

  items.forEach(function (item) {
    var question = item.querySelector('.faq-question');
    var answer = item.querySelector('.faq-answer');
    if (!question || !answer) return;

    question.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');

      // Close all
      items.forEach(function (other) {
        other.classList.remove('open');
        var otherAnswer = other.querySelector('.faq-answer');
        if (otherAnswer) otherAnswer.style.maxHeight = null;
      });

      // Open clicked if it was closed
      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = answer.scrollHeight + 'px';
      }
    });

    question.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        question.click();
      }
    });
  });
}

/* ---- Form Validation ---- */
function initForms() {
  document.querySelectorAll('.contact-form').forEach(function (form) {
    var requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(function (field) {
      field.addEventListener('blur', function () { validateField(field); });
      field.addEventListener('input', function () {
        if (field.classList.contains('error')) validateField(field);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var valid = true;
      requiredFields.forEach(function (field) {
        if (!validateField(field)) valid = false;
      });
      if (valid) submitForm(form);
    });
  });
}

function validateField(field) {
  var value = field.value.trim();
  var group = field.closest('.form-group');
  var errorEl = group ? group.querySelector('.form-error') : null;
  var isValid = true;
  var msg = '';

  if (!value) {
    isValid = false;
    msg = 'This field is required.';
  } else if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    isValid = false;
    msg = 'Please enter a valid email address.';
  } else if (field.type === 'tel' && value && !/^[\d\s\-\(\)\+]{7,}$/.test(value)) {
    isValid = false;
    msg = 'Please enter a valid phone number.';
  }

  if (isValid) {
    field.classList.remove('error');
    if (errorEl) errorEl.classList.remove('show');
  } else {
    field.classList.add('error');
    if (errorEl) { errorEl.textContent = msg; errorEl.classList.add('show'); }
  }

  return isValid;
}

function submitForm(form) {
  var submitBtn = form.querySelector('[type="submit"]');
  var successEl = form.querySelector('.form-success');
  var fieldsEl = form.querySelector('.form-fields');

  // Ensure a submit-error element exists
  var submitErrorEl = form.querySelector('.form-submit-error');
  if (!submitErrorEl) {
    submitErrorEl = document.createElement('div');
    submitErrorEl.className = 'form-submit-error';
    submitErrorEl.setAttribute('role', 'alert');
    submitErrorEl.setAttribute('aria-live', 'polite');
    submitErrorEl.style.cssText = 'color:#c0392b; background:#fdf2f2; border:1px solid #f5c6cb; border-radius:6px; padding:0.75rem 1rem; margin-top:0.75rem; font-size:0.9rem; display:none;';
    var submitRow = form.querySelector('.form-submit-row');
    if (submitRow) {
      submitRow.parentNode.insertBefore(submitErrorEl, submitRow.nextSibling);
    } else {
      form.appendChild(submitErrorEl);
    }
  }

  function showSubmitError(msg) {
    submitErrorEl.textContent = msg;
    submitErrorEl.style.display = 'block';
    if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Send Message'; }
  }

  // Guard: endpoint not yet configured
  if (FORMSPREE_ENDPOINT.indexOf('YOUR_FORM_ID') !== -1) {
    console.error('Formspree endpoint is not configured. Set FORMSPREE_ENDPOINT in script.js before going live.');
    showSubmitError('Contact form is not yet configured. Please reach out directly.');
    return;
  }

  if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending…'; }
  submitErrorEl.style.display = 'none';

  // Collect form data as JSON
  var data = {};
  var elements = form.querySelectorAll('input, select, textarea');
  elements.forEach(function (el) {
    if (el.name) {
      if (el.type === 'radio') {
        if (el.checked) data[el.name] = el.value;
      } else {
        data[el.name] = el.value;
      }
    }
  });

  fetch(FORMSPREE_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(function (response) {
    if (response.ok) {
      // Success
      if (fieldsEl) {
        fieldsEl.style.display = 'none';
      } else {
        form.querySelectorAll('.form-group, .form-row, .form-submit-row, .form-privacy').forEach(function (el) {
          el.style.display = 'none';
        });
      }
      if (successEl) successEl.classList.add('show');
    } else {
      return response.json().then(function (json) {
        throw new Error((json && json.error) ? json.error : 'Submission failed. Please try again.');
      });
    }
  })
  .catch(function (err) {
    showSubmitError(err.message || 'There was an error sending your message. Please try again or reach out directly.');
  });
}

/* ---- Scroll Animations ---- */
function initScrollAnimations() {
  var els = document.querySelectorAll('.fade-in-up');
  if (!els.length || !('IntersectionObserver' in window)) {
    // Fallback: show all without animation
    els.forEach(function (el) { el.classList.add('animated'); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('animated');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  els.forEach(function (el) { observer.observe(el); });
}

/* ---- Active Nav Link ---- */
function setActiveNavLink() {
  var page = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-menu nav a').forEach(function (link) {
    var href = link.getAttribute('href');
    if (href === page || (page === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

/* ---- Smooth Scroll ---- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (href === '#') return;
      var target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      var navH = (document.querySelector('.site-nav') || {}).offsetHeight || 72;
      window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - navH - 20, behavior: 'smooth' });
    });
  });
}
