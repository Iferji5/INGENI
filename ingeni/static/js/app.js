(function(){
  const qs = (sel, scope=document) => scope.querySelector(sel);
  const qsa = (sel, scope=document) => Array.from(scope.querySelectorAll(sel));

  const navToggle = qs('.nav-toggle');
  const navLinks = qs('[data-role="nav-links"]');
  if(navToggle && navLinks){
    navToggle.addEventListener('click', () => {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!expanded));
      navLinks.classList.toggle('is-open', !expanded);
    });
  }

  const dropdown = qs('[data-dropdown]');
  if(dropdown){
    const trigger = dropdown.querySelector('.nav-link--trigger');
    const menu = dropdown.querySelector('.nav-dropdown__menu');
    trigger?.addEventListener('click', (evt) => {
      evt.preventDefault();
      const isOpen = dropdown.classList.toggle('open');
      trigger.setAttribute('aria-expanded', String(isOpen));
    });
    trigger?.addEventListener('keydown', (evt) => {
      if(evt.key === 'Escape'){
        dropdown.classList.remove('open');
        trigger.setAttribute('aria-expanded','false');
      }
    });
    document.addEventListener('keydown', (evt) => {
      if(evt.key === 'Escape'){
        dropdown.classList.remove('open');
        trigger?.setAttribute('aria-expanded','false');
      }
    });
    document.addEventListener('click', (evt) => {
      if(!dropdown.contains(evt.target)){
        dropdown.classList.remove('open');
        trigger?.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const areaLinks = qsa('[data-area-link]');
  areaLinks.forEach(link => {
    link.addEventListener('click', (evt) => {
      const url = new URL(link.href, window.location.origin);
      const targetId = url.hash.replace('#','');
      const samePage = window.location.pathname === '/' || window.location.pathname === '/index.html';
      if(samePage && targetId){
        evt.preventDefault();
        dropdown?.classList.remove('open');
        dropdown?.querySelector('.nav-link--trigger')?.setAttribute('aria-expanded','false');
        if(navLinks?.classList.contains('is-open')){
          navLinks.classList.remove('is-open');
          navToggle?.setAttribute('aria-expanded','false');
        }
        const target = document.getElementById(targetId);
        if(target){
          target.scrollIntoView({ behavior:'smooth', block:'start' });
        }
      }
    });
  });

  class Carousel{
    constructor(root){
      this.root = root;
      this.track = qs('[data-carousel-track]', root);
      this.slides = qsa('.carousel-slide', root);
      this.prevBtn = qs('[data-carousel-prev]', root);
      this.nextBtn = qs('[data-carousel-next]', root);
      this.dotsNav = qs('[data-carousel-dots]', root);
      this.index = 0;
      this.interval = null;
      this.duration = 5000;
      this.setup();
    }
    setup(){
      if(!this.root || !this.track || !this.slides.length){ return; }
      this.createDots();
      this.attachEvents();
      this.update();
      this.start();
    }
    createDots(){
      this.dots = this.slides.map((_, idx) => {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.dataset.index = idx;
        dot.setAttribute('aria-label', `Ir a la diapositiva ${idx + 1}`);
        this.dotsNav.appendChild(dot);
        return dot;
      });
    }
    attachEvents(){
      this.root.addEventListener('mouseenter', () => this.stop());
      this.root.addEventListener('mouseleave', () => this.start());
      this.prevBtn?.addEventListener('click', () => this.goto(this.index - 1));
      this.nextBtn?.addEventListener('click', () => this.goto(this.index + 1));
      this.dots.forEach(dot => dot.addEventListener('click', () => this.goto(Number(dot.dataset.index))));
      this.root.setAttribute('tabindex', '0');
      this.root.addEventListener('keydown', (evt) => {
        if(evt.key === 'ArrowLeft'){ evt.preventDefault(); this.goto(this.index - 1); }
        if(evt.key === 'ArrowRight'){ evt.preventDefault(); this.goto(this.index + 1); }
      });
    }
    start(){
      this.stop();
      this.interval = setInterval(() => this.goto(this.index + 1), this.duration);
    }
    stop(){
      if(this.interval){ clearInterval(this.interval); }
    }
    goto(newIndex){
      const total = this.slides.length;
      this.index = (newIndex + total) % total;
      this.update();
    }
    update(){
      const offset = -this.index * 100;
      this.track.style.transform = `translateX(${offset}%)`;
      this.slides.forEach((slide, idx) => slide.setAttribute('aria-hidden', idx !== this.index));
      this.dots.forEach((dot, idx) => dot.classList.toggle('is-active', idx === this.index));
    }
  }

  const carouselRoot = qs('[data-carousel]');
  if(carouselRoot){ new Carousel(carouselRoot); }

  const revealTargets = qsa('.reveal');
  if('IntersectionObserver' in window){
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if(entry.isIntersecting){
          entry.target.classList.add('reveal-in');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold:0.15 });
    revealTargets.forEach(target => observer.observe(target));
  }else{
    revealTargets.forEach(target => target.classList.add('reveal-in'));
  }

  const spyLinks = qsa('[data-scrollspy]');
  const spySections = spyLinks
    .map(link => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);

  const setActiveLink = () => {
    const scrollPos = window.scrollY + 160;
    let activeIndex = 0;
    spySections.forEach((section, idx) => {
      if(section.offsetTop <= scrollPos){ activeIndex = idx; }
    });
    spyLinks.forEach((link, idx) => link.classList.toggle('is-active', idx === activeIndex));
  };
  if(spySections.length){
    window.addEventListener('scroll', setActiveLink, { passive:true });
    setActiveLink();
  }

  const productGrid = qs('[data-product-grid]');
  if(productGrid){
    const filterButtons = qsa('[data-filter]');
    const cards = qsa('.product-card', productGrid);
    const setFilter = (value) => {
      filterButtons.forEach(btn => {
        const isActive = btn.dataset.filter === value || (value === 'all' && btn.dataset.filter === 'all');
        btn.classList.toggle('pill--active', isActive);
        btn.setAttribute('aria-selected', String(isActive));
      });
      cards.forEach(card => {
        const show = value === 'all' || card.dataset.category === value;
        card.style.display = show ? '' : 'none';
      });
    };
    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => setFilter(btn.dataset.filter || 'all'));
    });
    const params = new URLSearchParams(window.location.search);
    const fromUrl = params.get('cat');
    if(fromUrl){
      const match = filterButtons.find(btn => btn.dataset.filter === fromUrl);
      if(match){
        setFilter(fromUrl);
      }else{
        setFilter('all');
      }
    }else{
      setFilter('all');
    }
  }

  const areaCards = qsa('.area-card');
  areaCards.forEach(card => {
    card.setAttribute('tabindex', '0');
    card.setAttribute('role', 'link');
    const slug = card.dataset.cat;
    const goTo = () => { window.location.href = `/productos/?cat=${slug}`; };
    card.addEventListener('click', goTo);
    card.addEventListener('keydown', (evt) => {
      if(evt.key === 'Enter' || evt.key === ' '){
        evt.preventDefault();
        goTo();
      }
    });
  });

  const toaster = (message) => {
    const toast = qs('#toaster');
    if(!toast){ return; }
    toast.textContent = message;
    toast.classList.add('is-visible');
    setTimeout(() => toast.classList.remove('is-visible'), 2600);
  };

  const contactForm = qs('[data-contact-form]');
  if(contactForm){
    const getRows = () => qsa('.form-row', contactForm);

    contactForm.addEventListener('submit', (evt) => {
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const loadingLabel = submitBtn?.dataset.loadingText || 'Enviando...';
      const originalLabel = submitBtn?.dataset.originalLabel || submitBtn?.textContent || '';
      if(submitBtn && !submitBtn.dataset.originalLabel){
        submitBtn.dataset.originalLabel = originalLabel;
      }

      let valid = true;
      getRows().forEach(row => {
        const field = qs('input, textarea, select', row);
        if(!field){ return; }
        const hasServerError = row.dataset.serverError === '1';
        const feedback = qs('.form-feedback', row);
        if(!field.checkValidity()){
          valid = false;
          row.classList.add('is-error');
          if(feedback && !feedback.textContent.trim()){
            feedback.textContent = field.validationMessage || 'Por favor completa este campo.';
          }
        }else if(!hasServerError){
          row.classList.remove('is-error');
        }
      });

      if(!valid){
        evt.preventDefault();
        if(submitBtn){
          submitBtn.disabled = false;
          submitBtn.textContent = originalLabel;
        }
        toaster('Por favor completa los campos obligatorios.');
      }else if(submitBtn){
        submitBtn.disabled = true;
        submitBtn.textContent = loadingLabel;
      }

      getRows().forEach(row => {
        if(row.dataset.serverError){
          delete row.dataset.serverError;
        }
      });
    });

    getRows().forEach(row => {
      const field = qs('input, textarea, select', row);
      if(!field){ return; }
      const clearError = () => {
        row.classList.remove('is-error');
        if(row.dataset.serverError){
          delete row.dataset.serverError;
        }
        const feedback = qs('.form-feedback', row);
        if(feedback && !field.validationMessage){
          feedback.textContent = '';
        }
      };
      field.addEventListener('input', clearError);
      field.addEventListener('change', clearError);
    });
  }

  qsa('[data-marquee]').forEach(wrapper => {
    const track = qs('.brand-track', wrapper);
    wrapper.addEventListener('mouseenter', () => track.style.animationPlayState = 'paused');
    wrapper.addEventListener('mouseleave', () => track.style.animationPlayState = 'running');
  });

  // === Mapa INGENI (Cartago) ===
(function initIngeniMap(){
  const el = document.getElementById('map');
  // Solo corre en la página de contacto y si Leaflet está cargado
  if (!el || !window.L) return;

  const center = [9.8644, -83.9194]; // Cartago, CR
  const map = L.map(el, { center, zoom: 13, scrollWheelZoom: false, zoomControl: true });

  // Tiles OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19
  }).addTo(map);

  // Marcador + popup
  const marker = L.marker(center).addTo(map);
  marker.bindPopup(
    '<strong>INGENI</strong><br>Cartago, Costa Rica<br>' +
    '<a href="https://maps.google.com/?q=Cartago+Costa+Rica" target="_blank" rel="noopener">Abrir en Google Maps</a>'
  );

  // Habilita scroll-zoom solo al enfocar el mapa
  el.addEventListener('mouseenter', () => map.scrollWheelZoom.enable());
  el.addEventListener('mouseleave', () => map.scrollWheelZoom.disable());
})();





})();



