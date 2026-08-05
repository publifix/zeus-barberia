(() => {
  "use strict";

  /* Footer year */
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* Header background on scroll */
  const header = document.getElementById("site-header");
  const setHeaderState = () => {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 24);
  };
  setHeaderState();
  window.addEventListener("scroll", setHeaderState, { passive: true });

  /* Mobile nav toggle */
  const navToggle = document.getElementById("nav-toggle");
  const nav = document.getElementById("nav");
  if (navToggle && nav) {
    const closeNav = () => {
      navToggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
      document.body.style.overflow = "";
    };
    const openNav = () => {
      navToggle.setAttribute("aria-expanded", "true");
      nav.classList.add("is-open");
      document.body.style.overflow = "hidden";
    };
    navToggle.addEventListener("click", () => {
      const isOpen = navToggle.getAttribute("aria-expanded") === "true";
      isOpen ? closeNav() : openNav();
    });
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeNav);
    });
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeNav();
    });
  }

  /* Smooth scroll for in-page anchors, offset handled by CSS scroll-margin-top */
  document.querySelectorAll('a[href^="#"][data-scroll], a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const id = link.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      history.pushState(null, "", id);
    });
  });

  /* Scroll reveal */
  const revealTargets = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealTargets.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -60px 0px" }
    );
    revealTargets.forEach((el) => io.observe(el));
  } else {
    revealTargets.forEach((el) => el.classList.add("is-visible"));
  }

  /* Gallery lightbox */
  const lightbox = document.getElementById("lightbox");
  const lightboxImg = document.getElementById("lightbox-img");
  let lastFocused = null;

  if (lightbox && lightboxImg) {
    const openLightbox = (btn) => {
      lastFocused = btn;
      lightboxImg.src = btn.dataset.full;
      lightboxImg.alt = btn.dataset.alt || "";
      lightbox.hidden = false;
      document.body.style.overflow = "hidden";
      lightbox.querySelector(".lightbox__close").focus();
    };
    const closeLightbox = () => {
      lightbox.hidden = true;
      lightboxImg.src = "";
      document.body.style.overflow = "";
      if (lastFocused) lastFocused.focus();
    };

    document.querySelectorAll(".gallery__item button").forEach((btn) => {
      btn.addEventListener("click", () => openLightbox(btn));
    });

    lightbox.querySelectorAll("[data-close]").forEach((el) => {
      el.addEventListener("click", closeLightbox);
    });

    window.addEventListener("keydown", (e) => {
      if (lightbox.hidden) return;
      if (e.key === "Escape") closeLightbox();
      if (e.key === "Tab") {
        e.preventDefault();
        lightbox.querySelector(".lightbox__close").focus();
      }
    });
  }
})();
