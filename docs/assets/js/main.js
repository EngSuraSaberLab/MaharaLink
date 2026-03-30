(function() {
 "use strict";
 
 function toggleScrolled() {
 const selectBody = document.querySelector('body');
 const selectHeader = document.querySelector('#header');
 if (!selectHeader.classList.contains('scroll-up-sticky') && !selectHeader.classList.contains('sticky-top') && !selectHeader.classList.contains('fixed-top')) return;
 window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
 }
 document.addEventListener('scroll', toggleScrolled);
 window.addEventListener('load', toggleScrolled);
 
 const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');
 function mobileNavToogle() {
 document.querySelector('body').classList.toggle('mobile-nav-active');
 mobileNavToggleBtn.classList.toggle('bi-list');
 mobileNavToggleBtn.classList.toggle('bi-x');
 }
 if (mobileNavToggleBtn) {
 mobileNavToggleBtn.addEventListener('click', mobileNavToogle);
 }
 
 document.querySelectorAll('#navmenu a').forEach(navmenu => {
 navmenu.addEventListener('click', () => {
 document.querySelectorAll('#navmenu a.active').forEach(link => link.classList.remove('active'));
 navmenu.classList.add('active');
 if (document.querySelector('.mobile-nav-active')) {
 mobileNavToogle();
 }
 });
 });
 
 document.querySelectorAll('.navmenu .toggle-dropdown').forEach(navmenu => {
 navmenu.addEventListener('click', function(e) {
 e.preventDefault();
 this.parentNode.classList.toggle('active');
 this.parentNode.nextElementSibling.classList.toggle('dropdown-active');
 e.stopImmediatePropagation();
 });
 });
 
 const preloader = document.querySelector('#preloader');
 if (preloader) {
 window.addEventListener('load', () => {
 preloader.remove();
 });
 }
 
 let scrollTop = document.querySelector('.scroll-top');
 function toggleScrollTop() {
 if (scrollTop) {
 window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
 }
 }
 scrollTop.addEventListener('click', (e) => {
 e.preventDefault();
 window.scrollTo({
 top: 0,
 behavior: 'smooth'
 });
 });
 window.addEventListener('load', toggleScrollTop);
 document.addEventListener('scroll', toggleScrollTop);
 
 function aosInit() {
 AOS.init({
 duration: 600,
 easing: 'ease-in-out',
 once: true,
 mirror: false
 });
 }
 window.addEventListener('load', aosInit);
 
 const glightbox = GLightbox({
 selector: '.glightbox'
 });
 
 document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
 let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
 let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
 let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';
 let initIsotope;
 imagesLoaded(isotopeItem.querySelector('.isotope-container'), function() {
 initIsotope = new Isotope(isotopeItem.querySelector('.isotope-container'), {
 itemSelector: '.isotope-item',
 layoutMode: layout,
 filter: filter,
 sortBy: sort
 });
 });
 isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
 filters.addEventListener('click', function() {
 isotopeItem.querySelector('.isotope-filters .filter-active').classList.remove('filter-active');
 this.classList.add('filter-active');
 initIsotope.arrange({
 filter: this.getAttribute('data-filter')
 });
 if (typeof aosInit === 'function') {
 aosInit();
 }
 }, false);
 });
 });
 
 new PureCounter();
 
 function initSwiper() {
 document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
 let config = JSON.parse(
 swiperElement.querySelector(".swiper-config").innerHTML.trim()
 );
 if (swiperElement.classList.contains("swiper-tab")) {
 initSwiperWithCustomPagination(swiperElement, config);
 } else {
 new Swiper(swiperElement, config);
 }
 });
 }
 window.addEventListener("load", initSwiper);
 
 window.addEventListener('load', function(e) {
 if (window.location.hash) {
 if (document.querySelector(window.location.hash)) {
 setTimeout(() => {
 let section = document.querySelector(window.location.hash);
 let scrollMarginTop = getComputedStyle(section).scrollMarginTop;
 window.scrollTo({
 top: section.offsetTop - parseInt(scrollMarginTop),
 behavior: 'smooth'
 });
 }, 100);
 }
 }
 });
 
 let navmenulinks = document.querySelectorAll('.navmenu a');
 function setActiveNavByLocation() {
 const currentUrl = new URL(window.location.href);
 let bestMatch = null;
 let bestScore = -1;
 navmenulinks.forEach(link => {
 const linkUrl = new URL(link.href, window.location.origin);
 const linkPath = linkUrl.pathname.endsWith('/') ? linkUrl.pathname : `${linkUrl.pathname}/`;
 const currentPath = currentUrl.pathname.endsWith('/') ? currentUrl.pathname : `${currentUrl.pathname}/`;
 if (linkUrl.hash) {
 if (linkPath === currentPath && currentUrl.hash === linkUrl.hash && bestScore < 1000) {
 bestMatch = link;
 bestScore = 1000;
 }
 return;
 }
 if (linkPath === currentPath && bestScore < 900) {
 bestMatch = link;
 bestScore = 900;
 return;
 }
 if (currentPath.startsWith(linkPath) && linkPath !== '/' && linkPath.length > bestScore) {
 bestMatch = link;
 bestScore = linkPath.length;
 }
 });
 if (bestMatch) {
 document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
 bestMatch.classList.add('active');
 }
 }
 function navmenuScrollspy() {
 navmenulinks.forEach(navmenulink => {
 if (!navmenulink.hash) return;
 let section = document.querySelector(navmenulink.hash);
 if (!section) return;
 let position = window.scrollY + 200;
 if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
 document.querySelectorAll('.navmenu a.active').forEach(link => link.classList.remove('active'));
 navmenulink.classList.add('active');
 } else {
 navmenulink.classList.remove('active');
 }
 })
 }
 window.addEventListener('load', setActiveNavByLocation);
 window.addEventListener('hashchange', setActiveNavByLocation);
 window.addEventListener('load', navmenuScrollspy);
 document.addEventListener('scroll', navmenuScrollspy);
 
 function initStaticShowcaseMode() {
 const pageBody = document.body;
 if (!pageBody || pageBody.dataset.staticShowcaseMode !== 'true') return;
 const contactUrl = pageBody.dataset.staticShowcaseContactUrl || '';
 const isArabic = document.documentElement.lang === 'ar';
 const message = isArabic ? pageBody.dataset.staticShowcaseMessageAr : pageBody.dataset.staticShowcaseMessageEn;
 const buttonLabel = isArabic ? pageBody.dataset.staticShowcaseButtonAr : pageBody.dataset.staticShowcaseButtonEn;
 const contactTriggers = document.querySelectorAll('.showcase-contact-trigger');
 let noticeTimeoutId = null;
 if (!contactTriggers.length) return;
 const notice = document.createElement('div');
 notice.className = 'showcase-notice';
 notice.setAttribute('aria-live', 'polite');
 notice.innerHTML = `
 <div class="showcase-notice__panel">
 <button type="button" class="showcase-notice__close" aria-label="${isArabic ? 'إغلاق' : 'Close'}">&times;</button>
 <div class="showcase-notice__icon"><i class="bi bi-megaphone-fill"></i></div>
 <p class="showcase-notice__message">${message}</p>
 ${contactUrl ? `<a class="showcase-notice__action" href="${contactUrl}">${buttonLabel}</a>` : ''}
 </div>
 `;
 document.body.appendChild(notice);
 function hideNotice() {
 notice.classList.remove('is-visible');
 }
 function showNotice() {
 notice.classList.add('is-visible');
 window.clearTimeout(noticeTimeoutId);
 noticeTimeoutId = window.setTimeout(hideNotice, 5500);
 }
 notice.querySelector('.showcase-notice__close')?.addEventListener('click', hideNotice);
 notice.addEventListener('click', (event) => {
 if (event.target === notice) {
 hideNotice();
 }
 });
 contactTriggers.forEach((link) => {
 link.addEventListener('click', (event) => {
 event.preventDefault();
 showNotice();
 });
 });
 }
 window.addEventListener('load', initStaticShowcaseMode);
})();