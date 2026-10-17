(function () {
  "use strict";

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char];
    });
  }

  function categoryLabel(category) {
    return {
      "web-dev": "Web Development",
      "data-viz": "Data Visualization",
      app: "App Development"
    }[category] || category || "Project";
  }

  function twoLineName(value) {
    var parts = String(value || "").trim().split(/\s+/);
    if (parts.length < 2) return escapeHtml(value);
    return escapeHtml(parts.shift()) + "<br>" + escapeHtml(parts.join(" "));
  }

  function projectCard(item, index) {
    var title = escapeHtml(item.title || "Untitled project");
    var image = escapeHtml(item.image || "");
    var url = escapeHtml(item.url || "#work");
    var category = escapeHtml(categoryLabel(item.category));
    var filterClass = item.category === "data-viz" ? "data-viz" : "web-dev";
    return '<div class="portfolio-item-wrap masonry-block grid-item ohio-project-item ohio-filter-project-' + filterClass + ' vc_col-lg-4 vc_col-md-6 vc_col-xs-12" data-lazy-item="" data-lazy-scope="projects">' +
      '<div data-aos-once="true" data-aos="fade-up" data-aos-delay="' + (index * 100) + '">' +
      '<div class="portfolio-item portfolio-item-grid portfolio-grid-type-1 boxed hover-scale-img hover-color-overlay">' +
      '<div data-cursor-class="cursor-link" class="portfolio-item-image "><a href="' + url + '">' +
      (image ? '<noscript><img decoding="async" class="" src="' + image + '" alt="' + title + '"></noscript><img decoding="async" class="lazyload " src="data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20viewBox=%220%200%20210%20140%22%3E%3C/svg%3E" data-src="' + image + '" alt="' + title + '">' : '<div style="height:100%;min-height:180px"></div>') +
      '</a></div><div class="portfolio-item-details text-left"><h3 class="portfolio-item-headline title ">' + title + '</h3>' +
      '<div class="category-holder"><span class="category "><a href="#work">' + category + '</a></span></div>' +
      '<div class="show-project"><div class="show-project-link"><a href="' + url + '">Show project</a></div></div>' +
      '</div></div></div></div>';
  }

  function featuredSlide(item) {
    var name = escapeHtml(item.name || "Partner logo");
    var image = escapeHtml(item.image || "");
    var url = escapeHtml(item.url || "#");
    return '<div class="swiper-slide"><a href="' + url + '" target="_blank" rel="nofollow"><div class="elementor-carousel-image swiper-lazy" role="img" aria-label="' + name + '" data-background="' + image + '"><div class="swiper-lazy-preloader"></div></div></a></div>';
  }

  function apply(data) {
    var profile = data.profile || {};
    var name = document.querySelector("#top-heading-name h1");
    var role = document.querySelector("#hero-section h5");
    if (profile.name && name) name.innerHTML = twoLineName(profile.name);
    if (profile.role && role) role.textContent = profile.role;

    var partners = Array.isArray(data.partners) ? data.partners : data.featured;
    if (Array.isArray(partners) && partners.length) {
      var featuredWrapper = document.querySelector("#as-featured-in_carousel .swiper-wrapper");
      if (featuredWrapper) {
        featuredWrapper.innerHTML = partners.map(featuredSlide).join("");
        var featuredHeading = document.querySelector("#as-featured-in-text .elementor-heading-title");
        if (featuredHeading) featuredHeading.textContent = "Companies I've Worked With";
        var swiper = featuredWrapper.closest(".swiper") && featuredWrapper.closest(".swiper").swiper;
        if (swiper && typeof swiper.update === "function") swiper.update();
      }
    }

    var email = document.querySelector('#contact a[href*="email-protection"]');
    if (profile.email && email) {
      email.href = "mailto:" + profile.email;
      email.textContent = profile.email;
    }

    if (Array.isArray(data.projects) && data.projects.length) {
      var grid = document.querySelector(".vc_row.portfolio-grid");
      if (grid) {
        Array.prototype.slice.call(grid.querySelectorAll(".portfolio-item-wrap")).forEach(function (item) { item.remove(); });
        data.projects.forEach(function (item, index) { grid.insertAdjacentHTML("beforeend", projectCard(item, index)); });
      }
    }

    if (Array.isArray(data.experience) && data.experience.length) {
      var experienceItems = document.querySelectorAll("#experience .accordionItem");
      data.experience.forEach(function (item, index) {
        var target = experienceItems[index];
        if (!target) return;
        var position = target.querySelector(".position");
        var time = target.querySelector(".time");
        var description = target.querySelector(".accordionItem_content p");
        if (position) position.textContent = (item.role || "") + (item.company ? " @ " + item.company : "");
        if (time && item.period) time.textContent = item.period;
        if (description && item.description) description.textContent = item.description;
      });
    }

    if (Array.isArray(data.testimonials) && data.testimonials.length) {
      var testimonials = document.querySelectorAll("#contact .testimonial .elementor-column");
      data.testimonials.forEach(function (item, index) {
        var target = testimonials[index];
        if (!target) return;
        var quote = target.querySelector(".elementor-widget-text-editor p");
        var author = target.querySelector(".testimonial-author");
        if (quote && item.quote) quote.textContent = item.quote;
        if (author && item.author) author.textContent = "- " + item.author;
      });
    }
    document.documentElement.dataset.portfolioSynced = "true";
  }

  function installMobileOverflowFix() {
    var style = document.createElement("style");
    style.setAttribute("data-portfolio-mobile-fix", "true");
    style.textContent = "#top-heading-name h1 { font-size: clamp(58px, 8vw, 110px) !important; line-height: .92 !important; } .circle-cursor { display: none !important; } @media (max-width: 1280px) { #content > .elementor { box-sizing: border-box; width: 100%; max-width: 100%; margin-left: 0; margin-right: 0; } #content .elementor-section { box-sizing: border-box; max-width: 100%; } #content .elementor-section > .elementor-container { max-width: 100%; } }";
    document.head.appendChild(style);
  }

  installMobileOverflowFix();
  fetch("/data/portfolio.json", { cache: "no-store" })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) { if (data) apply(data); })
    .catch(function () { /* The original static content remains available if sync data is unavailable. */ });
}());
