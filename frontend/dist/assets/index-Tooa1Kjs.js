(function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const a of document.querySelectorAll('link[rel="modulepreload"]'))o(a);new MutationObserver(a=>{for(const n of a)if(n.type==="childList")for(const i of n.addedNodes)i.tagName==="LINK"&&i.rel==="modulepreload"&&o(i)}).observe(document,{childList:!0,subtree:!0});function s(a){const n={};return a.integrity&&(n.integrity=a.integrity),a.referrerPolicy&&(n.referrerPolicy=a.referrerPolicy),a.crossOrigin==="use-credentials"?n.credentials="include":a.crossOrigin==="anonymous"?n.credentials="omit":n.credentials="same-origin",n}function o(a){if(a.ep)return;a.ep=!0;const n=s(a);fetch(a.href,n)}})();const R="";function I(e){return e?e.startsWith("http://")||e.startsWith("https://")||e.startsWith("data:")?e:`${R}${e.startsWith("/")?"":"/"}${e}`:""}async function y({page:e=1,pageSize:t=24,search:s="",category:o="",sort:a="latest"}={}){const n=new URLSearchParams({page:String(e),page_size:String(t)});s&&n.set("search",s),o&&n.set("category",o),a&&n.set("sort",a);const i=await fetch(`${R}/games?${n}`,{headers:{Accept:"application/json"}});if(!i.ok)throw new Error(`HTTP ${i.status}`);return i.json()}async function D(e){const t=await fetch(`${R}/games/${e}`,{headers:{Accept:"application/json"}});if(!t.ok)throw new Error(`HTTP ${t.status}`);return t.json()}async function z(){const e=await fetch(`${R}/games/random`);if(!e.ok)throw new Error("No random game available");return e.json()}const c=document.getElementById("app");function r(e){const t=document.createElement("div");return t.textContent=e||"",t.innerHTML}const S=[{name:"Action",slug:"action"},{name:"Adventure",slug:"adventure"},{name:"Anime",slug:"anime"},{name:"Building",slug:"building"},{name:"First-person Shooter",slug:"fps"},{name:"Horror",slug:"horror"},{name:"Indie",slug:"indie"},{name:"Multiplayer",slug:"multiplayer"},{name:"Open World",slug:"open-world"},{name:"Racing",slug:"racing"},{name:"Role-playing Game",slug:"rpg"},{name:"Sci-fi",slug:"sci-fi"},{name:"Shooters",slug:"shooting"},{name:"Simulation",slug:"simulation"},{name:"Sports",slug:"sports"},{name:"Strategy",slug:"strategy"},{name:"Survival",slug:"survival"},{name:"Virtual Reality",slug:"vr"}];function L(e="",t=""){const s=(e+" "+t).toLowerCase();return s.includes("vr")||s.includes("virtual reality")?"Virtual Reality":s.includes("horror")||s.includes("somnia")||s.includes("hellraiser")?"Horror":s.includes("anime")||s.includes("slayer")||s.includes("yaiba")?"Anime":s.includes("racing")||s.includes("forza")||s.includes("rally")?"Racing":s.includes("simulator")||s.includes("bakery")||s.includes("cafe")?"Simulation":s.includes("rpg")||s.includes("witcher")||s.includes("elden")||s.includes("eternia")?"Role-playing Game":s.includes("multiplayer")||s.includes("co-op")||s.includes("friends")?"Multiplayer":s.includes("adventure")||s.includes("harvest")||s.includes("explore")?"Adventure":s.includes("indie")||s.includes("dupery")||s.includes("paperhead")?"Indie":"Action"}function E(e=""){const t=e.match(/Build\s+\d+/i);if(t)return t[0];const s=e.match(/v\d+(\.\d+)+/i);return s?s[0]:e.toLowerCase().includes("co-op")?"Co-op":e.toLowerCase().includes("recompiled")?"Recompiled":null}function q(e=""){return e.replace(/\s*Free\s*Download\s*/i,"").replace(/\s*\([^)]*\)\s*$/,"").trim()||e}let k;function M(){if(!("IntersectionObserver"in window)){document.querySelectorAll("img[data-src]").forEach(e=>{e.src=e.dataset.src,e.classList.remove("opacity-0")});return}k&&k.disconnect(),k=new IntersectionObserver(e=>{e.forEach(t=>{if(t.isIntersecting){const s=t.target;s.src=s.dataset.src,s.classList.remove("opacity-0"),k.unobserve(s)}})},{rootMargin:"300px",threshold:0}),document.querySelectorAll("img[data-src]").forEach(e=>k.observe(e))}function H(e){let t=document.getElementById("toast");t||(t=document.createElement("div"),t.id="toast",t.className="fixed bottom-6 right-6 bg-[#181326] border border-[#a855f7] text-white text-xs font-bold px-4 py-3 rounded-xl shadow-2xl z-50 transition-all",document.body.appendChild(t)),t.innerHTML=`
    <div class="flex items-center gap-2">
      <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
      <span>${r(e)}</span>
    </div>
  `,t.classList.remove("hidden"),setTimeout(()=>t.classList.add("hidden"),3500)}let B;async function F(e){const t=document.getElementById("search-live-dropdown");if(t){if(e=(e||"").trim(),e.length<2){t.classList.add("hidden");return}try{const s=await y({page:1,pageSize:6,search:e});if(!s.items||s.items.length===0){t.innerHTML=`<div class="p-3 text-xs text-gray-400 text-center">No games found matching "${r(e)}"</div>`,t.classList.remove("hidden");return}const o=s.items.map(a=>{const n=I(a.thumbnail_url);return`
          <div
            onclick="goRoute('/game/${a.id}'); document.getElementById('search-live-dropdown').classList.add('hidden');"
            class="p-2.5 hover:bg-[#251d38] flex items-center gap-3 cursor-pointer transition border-b border-[#281f3b] last:border-none"
          >
            <img src="${r(n)}" class="w-9 h-12 object-cover rounded bg-[#100c19] flex-shrink-0" onerror="this.src='/logo.png'">
            <div class="flex-1 min-w-0">
              <h4 class="text-xs font-bold text-white truncate">${r(a.title)}</h4>
              <div class="flex items-center gap-2 text-[10px] text-gray-400 mt-0.5">
                <span class="text-[#c537ff] font-semibold">${r(a.category||L(a.title,a.slug))}</span>
                <span>•</span>
                <span>${r(a.file_size||"Direct Download")}</span>
              </div>
            </div>
          </div>
        `}).join("");t.innerHTML=`<div class="p-1 max-h-80 overflow-y-auto">${o}</div>`,t.classList.remove("hidden")}catch{t.classList.add("hidden")}}}function p(e="",t="home"){const s=S.map(o=>`
      <a href="/category/${o.slug}" onclick="goRoute('/category/${o.slug}'); return false;" class="nav-dropdown-item ${t===o.slug?"active":""}">
        <span>${r(o.name)}</span>
        <svg class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
      </a>
    `).join("");return`
    <header class="theme-header header-layout-1 sticky top-0 z-50 bg-[#16131f] border-b border-[#251d38]">
      <div class="max-w-[1250px] mx-auto px-4 h-[75px] flex items-center justify-between gap-4">
        <!-- Mobile Menu Hamburger Button -->
        <button
          onclick="toggleMobileMenu()"
          class="lg:hidden text-gray-300 hover:text-white p-2 focus:outline-none"
          title="Open Menu"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>

        <!-- SteamRIP Official Logo -->
        <a href="/" onclick="goRoute('/'); return false;" class="flex items-center gap-2 group flex-shrink-0" title="SteamRIP — Free Pre-installed Steam Games">
          <img
            src="/logo.png"
            alt="SteamRIP"
            class="h-[46px] w-auto object-contain transition-transform group-hover:scale-105"
            onerror="this.src='https://steamrip.com/wp-content/uploads/2021/06/Site-logo3.png'"
          >
        </a>

        <!-- Main Navigation Bar -->
        <nav class="hidden lg:flex items-center gap-1">
          <!-- Home -->
          <a href="/" onclick="goRoute('/'); return false;" class="steamrip-nav-item ${t==="home"?"active":""}">
            <svg class="w-4 h-4 fill-current text-[#007dff]" viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm3.87 14.13-1.89-1.9a2.53 2.53 0 0 0-.85.34l-.87 1.86a.46.46 0 0 1-.41.27H9.22a.46.46 0 0 1-.41-.67l.87-1.86a2.49 2.49 0 0 0 .34-.85l-1.9-1.89a.46.46 0 0 1 .32-.79h2.63a.46.46 0 0 1 .46.46v2.63a.46.46 0 0 1-.79.32l-.47-.47a1.64 1.64 0 0 1-.54.54l-.47-.47a.46.46 0 0 1 .32-.79h2.63a.46.46 0 0 1 .46.46v2.63a.46.46 0 0 1-.78.33z"/></svg>
            <span>Home</span>
          </a>

          <!-- Categories Dropdown -->
          <div class="nav-dropdown">
            <button class="steamrip-nav-item flex items-center gap-1 ${t.startsWith("category")?"active":""}">
              <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M4 6h16V4H4zm0 5h16V9H4zm0 5h16v-2H4zm0 5h16v-2H4z"/></svg>
              <span>Categories</span>
              <svg class="w-3 h-3 text-gray-400 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
            <div class="nav-dropdown-menu grid grid-cols-2 gap-1 w-[380px] p-2">
              ${s}
            </div>
          </div>

          <!-- Top Games -->
          <a href="/top-games" onclick="goRoute('/top-games'); return false;" class="steamrip-nav-item ${t==="top-games"?"active":""}">
            <span>Top Games</span>
          </a>

          <!-- Recent Updates -->
          <a href="/updated-games" onclick="goRoute('/updated-games'); return false;" class="steamrip-nav-item ${t==="updated-games"?"active":""}">
            <span>Recent Updates</span>
          </a>

          <!-- Games List Dropdown -->
          <div class="nav-dropdown">
            <button class="steamrip-nav-item flex items-center gap-1 ${t==="games-list"||t==="collections"?"active":""}">
              <span>Games List</span>
              <svg class="w-3 h-3 text-gray-400 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
            <div class="nav-dropdown-menu">
              <a href="/games-list" onclick="goRoute('/games-list'); return false;" class="nav-dropdown-item ${t==="games-list"?"active":""}">
                <span>All Games (A-Z)</span>
                <span class="text-[10px] bg-[#271e3d] text-gray-400 px-2 py-0.5 rounded">4,850+</span>
              </a>
              <a href="/collections" onclick="goRoute('/collections'); return false;" class="nav-dropdown-item ${t==="collections"?"active":""}">
                <span>Games Collections</span>
              </a>
            </div>
          </div>

          <!-- FAQ Dropdown -->
          <div class="nav-dropdown">
            <button class="steamrip-nav-item flex items-center gap-1 ${t==="faq"||t==="steps-for-games"?"active":""}">
              <span>FAQ</span>
              <svg class="w-3 h-3 text-gray-400 ml-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
            <div class="nav-dropdown-menu">
              <a href="/faq" onclick="goRoute('/faq'); return false;" class="nav-dropdown-item ${t==="faq"?"active":""}">
                <span>All FAQs</span>
              </a>
              <a href="/steps-for-games" onclick="goRoute('/steps-for-games'); return false;" class="nav-dropdown-item ${t==="steps-for-games"?"active":""}">
                <span>How to Run Games</span>
              </a>
            </div>
          </div>

          <!-- Discord -->
          <a href="https://discord.gg/NBVFJsmy9y" target="_blank" rel="noopener" class="steamrip-nav-item text-[#a855f7] hover:text-[#c537ff]">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994.021-.041.001-.09-.041-.106a13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.929 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.893.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/></svg>
            <span>Discord</span>
          </a>
        </nav>

        <!-- Right Action Components -->
        <div class="flex items-center gap-2">
          <!-- Live Search Bar -->
          <div class="relative w-44 sm:w-64">
            <input
              type="search"
              id="header-search"
              value="${r(e)}"
              placeholder="Search games or mirrors…"
              autocomplete="off"
              class="w-full bg-[#1e172e] border border-[#2f2448] rounded-full py-1.5 pl-8 pr-3 text-xs font-semibold text-white placeholder-gray-400 focus:outline-none focus:border-[#ff0505] focus:ring-1 focus:ring-[#ff0505] transition"
            >
            <svg class="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-2 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            <div id="search-live-dropdown" class="absolute left-0 right-0 top-10 bg-[#181326] border border-[#3b2d56] rounded-xl shadow-2xl z-50 hidden overflow-hidden"></div>
          </div>

          <!-- Random Game Button -->
          <button
            onclick="triggerRandomGame()"
            class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[#1e172e] border border-[#2f2448] text-gray-300 hover:text-[#c537ff] hover:border-[#c537ff] transition"
            title="Random Article / Game"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          </button>
        </div>
      </div>

      <!-- Mobile Navigation Drawer (hidden by default) -->
      <div id="mobile-drawer" class="lg:hidden hidden bg-[#140f21] border-b border-[#251d38] px-4 py-4">
        <div class="flex flex-col gap-2 text-xs font-bold">
          <a href="/" onclick="goRoute('/'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">Home</a>
          <a href="/top-games" onclick="goRoute('/top-games'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">Top Games</a>
          <a href="/updated-games" onclick="goRoute('/updated-games'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">Recent Updates</a>
          <a href="/games-list" onclick="goRoute('/games-list'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">All Games (A-Z)</a>
          <a href="/collections" onclick="goRoute('/collections'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">Collections</a>
          <a href="/faq" onclick="goRoute('/faq'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">FAQ</a>
          <a href="/steps-for-games" onclick="goRoute('/steps-for-games'); toggleMobileMenu(); return false;" class="p-2 hover:bg-[#251d38] rounded">How to Run Games</a>
          <div class="border-t border-[#251d38] my-1 pt-2">
            <span class="text-[10px] text-gray-500 uppercase tracking-widest block mb-2">Categories</span>
            <div class="grid grid-cols-2 gap-1.5">
              ${S.map(o=>`<a href="/category/${o.slug}" onclick="goRoute('/category/${o.slug}'); toggleMobileMenu(); return false;" class="p-1.5 bg-[#1b152b] hover:bg-[#291f42] rounded text-gray-300 text-[11px]">${r(o.name)}</a>`).join("")}
            </div>
          </div>
        </div>
      </div>
    </header>
  `}function u(){return`
    <footer class="site-footer dark-skin dark-widgetized-area bg-[#0b0813] border-t border-[#1d162b] text-[#a09cb0] mt-20 pt-12 pb-8" id="footer">
      <div id="footer-widgets-container" class="max-w-[1250px] mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
          <!-- Col 1: Our Goal (Exact SteamRIP Copy) -->
          <div>
            <div class="the-global-title has-block-head-4 !mb-3 border-none pb-0">
              <div class="the-subtitle text-sm">Our Goal:</div>
            </div>
            <p class="text-xs leading-relaxed text-gray-400 text-justify">
              No Doubt everyone loves free games of any platform. SteamRIP is the arena for free games, it allows you to download all your favorite games completely free. All Games are Pre-Installed, which means you don’t need to install the games. Our games are compressed and no content has been removed, which decreases the game size. We reorganized the download method and we will strive for being the legit platform for free Pre-Installed games without any cost. Our site name does not represent the RIP released games.
            </p>
          </div>

          <!-- Col 2: Official Site (Exact SteamRIP Copy) -->
          <div>
            <div class="the-global-title has-block-head-4 !mb-3 border-none pb-0">
              <div class="the-subtitle text-sm">Official Site</div>
            </div>
            <p class="text-xs leading-relaxed text-gray-400 text-justify mb-4">
              Only trust the official site: steamrip.com and avoid the fake copycats. Always check URL for verification.
            </p>
            <div class="bg-[#151022] border border-[#2b2140] p-3 rounded-xl flex items-center gap-3">
              <div class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse flex-shrink-0"></div>
              <span class="text-xs font-bold text-gray-200">100% Pre-Installed • Zero Adware • Fast Mirrors</span>
            </div>
          </div>

          <!-- Col 3: Useful Links -->
          <div>
            <div class="the-global-title has-block-head-4 !mb-3 border-none pb-0">
              <div class="the-subtitle text-sm">Important Guides</div>
            </div>
            <div class="flex flex-col gap-2 text-xs font-semibold">
              <a href="/steps-for-games" onclick="goRoute('/steps-for-games'); return false;" class="hover:text-[#c537ff] transition">How to Run Games Guide</a>
              <a href="/faq" onclick="goRoute('/faq'); return false;" class="hover:text-[#c537ff] transition">Frequently Asked Questions (FAQ)</a>
              <a href="/games-list" onclick="goRoute('/games-list'); return false;" class="hover:text-[#c537ff] transition">Complete Games List (A-Z)</a>
              <a href="/request-games" onclick="goRoute('/request-games'); return false;" class="hover:text-[#c537ff] transition">Request a New Game</a>
              <a href="https://discord.gg/NBVFJsmy9y" target="_blank" rel="noopener" class="hover:text-[#c537ff] transition flex items-center gap-1">
                <span>Community Discord Server</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Site Info Bar (Exact SteamRIP Copy & Links) -->
      <div id="site-info" class="border-t border-[#181224] pt-6">
        <div class="max-w-[1250px] mx-auto px-4 flex flex-col md:flex-row items-center justify-between text-xs text-gray-500 gap-4">
          <div class="copyright-text copyright-text-first">
            © Copyright 2026 All Rights Reserved
          </div>
          <div class="copyright-text copyright-text-second flex items-center gap-2 flex-wrap justify-center font-medium">
            <a href="/about" onclick="goRoute('/about'); return false;" class="hover:text-gray-300 transition">About</a>
            <span>|</span>
            <a href="/request-games" onclick="goRoute('/request-games'); return false;" class="hover:text-gray-300 transition">Request Games</a>
            <span>|</span>
            <a href="/privacy-policy" onclick="goRoute('/privacy-policy'); return false;" class="hover:text-gray-300 transition">Privacy Policy</a>
            <span>|</span>
            <a href="/terms-and-conditions" onclick="goRoute('/terms-and-conditions'); return false;" class="hover:text-gray-300 transition">Terms & Conditions</a>
            <span>|</span>
            <a href="/contact-us" onclick="goRoute('/contact-us'); return false;" class="hover:text-gray-300 transition">Contact Us</a>
          </div>
          <div class="flex items-center gap-3">
            <a href="https://discord.gg/NBVFJsmy9y" target="_blank" rel="noopener" class="text-gray-400 hover:text-white transition" title="Discord">
              <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994.021-.041.001-.09-.041-.106a13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.929 1.793 8.18 1.793 12.061 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.893.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.028zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/></svg>
            </a>
            <a href="https://www.reddit.com/r/SteamRip/" target="_blank" rel="noopener" class="text-gray-400 hover:text-white transition" title="Reddit">
              <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.702zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.197-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  `}function C(e){const t=I(e.thumbnail_url),s=e.category||L(e.title,e.slug),o=E(e.title),a=e.title,n=t?`data-src="${r(t)}"`:"",i=o?`<span class="tagmetafield">${r(o)}</span>`:"";return`
    <article data-id="${e.id}" class="post-item group cursor-pointer" onclick="goRoute('/game/${e.id}')">
      <div class="post-thumb-wrap">
        <span class="post-cat">${r(s)}</span>
        ${i}
        
        <a href="/game/${e.id}" onclick="goRoute('/game/${e.id}'); return false;" class="block w-full h-full">
          <img
            ${n}
            src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 410'%3E%3Crect width='300' height='410' fill='%23171324'/%3E%3C/svg%3E"
            alt="${r(a)}"
            class="post-thumb-img opacity-0 transition-opacity duration-300"
            onload="this.classList.remove('opacity-0')"
            onerror="this.onerror=null;this.classList.remove('opacity-0');this.src='/logo.png';"
          >
        </a>

        <div class="post-thumb-overlay" onclick="goRoute('/game/${e.id}')">
          <span class="game-meta-line">
            <svg class="w-3 h-3 text-[#ff0505] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"></path></svg>
            ${r(e.file_size||"Direct Download")}
          </span>
          <h2 class="the-post-title" title="${r(a)}">
            <a href="/game/${e.id}" onclick="goRoute('/game/${e.id}'); return false;">${r(a)}</a>
          </h2>
        </div>
      </div>
    </article>
  `}function A(e=""){return`
    <div class="flex items-center gap-1.5 flex-wrap text-xs font-bold mb-6">
      <button onclick="goRoute('/');" class="px-3.5 py-1.5 rounded-full ${e?"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]":"bg-[#ff0505] text-white shadow-md"} transition">All</button>
      <button onclick="goRoute('/category/action');" class="px-3.5 py-1.5 rounded-full ${e==="action"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Action</button>
      <button onclick="goRoute('/category/adventure');" class="px-3.5 py-1.5 rounded-full ${e==="adventure"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Adventure</button>
      <button onclick="goRoute('/category/horror');" class="px-3.5 py-1.5 rounded-full ${e==="horror"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Horror</button>
      <button onclick="goRoute('/category/multiplayer');" class="px-3.5 py-1.5 rounded-full ${e==="multiplayer"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Multiplayer</button>
      <button onclick="goRoute('/category/racing');" class="px-3.5 py-1.5 rounded-full ${e==="racing"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Racing</button>
      <button onclick="goRoute('/category/anime');" class="px-3.5 py-1.5 rounded-full ${e==="anime"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Anime</button>
      <button onclick="goRoute('/category/vr');" class="px-3.5 py-1.5 rounded-full ${e==="vr"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">VR</button>
      <button onclick="goRoute('/top-games');" class="px-3.5 py-1.5 rounded-full ${e==="top"?"bg-[#ff0505] text-white shadow-md":"bg-[#1e172e] text-gray-300 hover:text-white hover:bg-[#2c2242]"} transition">Top Games</button>
    </div>
  `}function g(){const e=document.getElementById("header-search");e&&(e.oninput=t=>{clearTimeout(B),B=setTimeout(()=>{F(t.target.value)},250)},e.onkeydown=t=>{if(t.key==="Enter"){const s=document.getElementById("search-live-dropdown");s&&s.classList.add("hidden");const o=e.value.trim();h(`/?search=${encodeURIComponent(o)}`)}}),document.addEventListener("click",t=>{const s=document.getElementById("search-live-dropdown");s&&!t.target.closest("#header-search")&&!t.target.closest("#search-live-dropdown")&&s.classList.add("hidden")})}async function $(){const e=new URLSearchParams(window.location.search),t=Math.max(1,parseInt(e.get("page")||"1",10)),s=e.get("search")||"",o=24;c.innerHTML=`
    ${p(s,"home")}

    <!-- Hero Notice Ticker -->
    <div class="bg-[#1b122c] border-b border-[#2d1e48] py-2 px-4">
      <div class="max-w-[1250px] mx-auto flex items-center justify-between text-xs font-semibold gap-3">
        <div class="flex items-center gap-2 text-gray-200 truncate">
          <span class="bg-[#ff0505] text-white px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider">NOTICE</span>
          <span>All games are pre-installed & compressed. Download, extract and play instantly!</span>
        </div>
        <a href="https://discord.gg/NBVFJsmy9y" target="_blank" rel="noopener" class="hidden sm:inline-flex items-center gap-1 text-[#ff0505] hover:underline flex-shrink-0 font-bold">
          Join Discord &rarr;
        </a>
      </div>
    </div>

    <main class="max-w-[1250px] mx-auto px-4 py-8">
      <!-- Section Title -->
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">${s?`Search Results for: "${r(s)}"`:"Recently Added Games"}</h3>
      </div>

      ${A()}

      <!-- Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3.5 sm:gap-4" id="games-grid">
        <div class="col-span-full py-20 text-center text-gray-400 font-semibold flex flex-col items-center justify-center gap-3">
          <div class="w-8 h-8 border-2 border-[#ff0505] border-t-transparent rounded-full animate-spin"></div>
          <span>Loading SteamRIP games archive…</span>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-14 flex items-center justify-center gap-2" id="pagination-container"></div>
    </main>

    ${u()}
  `,g();const a=document.getElementById("games-grid"),n=document.getElementById("pagination-container");try{const i=await y({page:t,pageSize:o,search:s,sort:"latest"});if(!i.items||i.items.length===0){a.innerHTML=`
        <div class="col-span-full py-16 text-center bg-[#151121] border border-[#271f38] rounded-2xl p-8">
          <p class="text-base font-bold text-gray-200 mb-1">No games found.</p>
          <p class="text-xs text-gray-400 mb-4">No titles matched your search query. Try another keyword or browse all categories.</p>
          <button onclick="goRoute('/');" class="shortc-button purple !py-2 !px-5 text-xs">View All Games</button>
        </div>
      `;return}a.innerHTML=i.items.map(C).join(""),M(),a.querySelectorAll(".post-item").forEach(l=>{l.onclick=()=>h(`/game/${l.dataset.id}`)}),T(n,t,i.pages,l=>{const d=new URLSearchParams;l>1&&d.set("page",l),s&&d.set("search",s),h(`/?${d.toString()}`)})}catch(i){a.innerHTML=`
      <div class="col-span-full py-16 text-center text-red-400 font-bold bg-[#1b1426] border border-red-900/40 rounded-xl p-6">
        <p class="mb-2">Database Connection Notice</p>
        <p class="text-xs text-gray-400">${r(i.message)}</p>
      </div>
    `}}async function O(e){const t=new URLSearchParams(window.location.search),s=Math.max(1,parseInt(t.get("page")||"1",10)),o=24,a=S.find(l=>l.slug===e)||{name:e.charAt(0).toUpperCase()+e.slice(1)};c.innerHTML=`
    ${p("",e)}

    <main class="max-w-[1250px] mx-auto px-4 py-8">
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-2 text-xs text-gray-400 mb-4">
        <a href="/" onclick="goRoute('/'); return false;" class="hover:text-white">Home</a>
        <span>/</span>
        <span class="text-white font-semibold">Category: ${r(a.name)}</span>
      </nav>

      <!-- Section Title -->
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">${r(a.name)} Games</h3>
      </div>

      ${A(e)}

      <!-- Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3.5 sm:gap-4" id="games-grid">
        <div class="col-span-full py-20 text-center text-gray-400 font-semibold flex flex-col items-center justify-center gap-3">
          <div class="w-8 h-8 border-2 border-[#ff0505] border-t-transparent rounded-full animate-spin"></div>
          <span>Loading ${r(a.name)} games…</span>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-14 flex items-center justify-center gap-2" id="pagination-container"></div>
    </main>

    ${u()}
  `,g();const n=document.getElementById("games-grid"),i=document.getElementById("pagination-container");try{const l=await y({page:s,pageSize:o,category:e});if(!l.items||l.items.length===0){n.innerHTML=`
        <div class="col-span-full py-16 text-center bg-[#151121] border border-[#271f38] rounded-2xl p-8">
          <p class="text-base font-bold text-gray-200 mb-1">No games found in this category yet.</p>
          <p class="text-xs text-gray-400 mb-4">Our background scraper is currently importing more titles.</p>
          <button onclick="goRoute('/');" class="shortc-button purple !py-2 !px-5 text-xs">Browse All Games</button>
        </div>
      `;return}n.innerHTML=l.items.map(C).join(""),M(),n.querySelectorAll(".post-item").forEach(d=>{d.onclick=()=>h(`/game/${d.dataset.id}`)}),T(i,s,l.pages,d=>{h(`/category/${e}?page=${d}`)})}catch(l){n.innerHTML=`
      <div class="col-span-full py-16 text-center text-red-400 font-bold bg-[#1b1426] border border-red-900/40 rounded-xl p-6">
        <p>Failed to load category: ${r(l.message)}</p>
      </div>
    `}}async function V(){const e=new URLSearchParams(window.location.search),t=Math.max(1,parseInt(e.get("page")||"1",10)),s=24;c.innerHTML=`
    ${p("","top-games")}

    <main class="max-w-[1250px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Top Games — Most Popular Releases</h3>
      </div>
      ${A("top")}
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3.5 sm:gap-4" id="games-grid">
        <div class="col-span-full py-20 text-center text-gray-400 font-semibold flex flex-col items-center justify-center gap-3">
          <div class="w-8 h-8 border-2 border-[#ff0505] border-t-transparent rounded-full animate-spin"></div>
          <span>Loading top games…</span>
        </div>
      </div>
      <div class="mt-14 flex items-center justify-center gap-2" id="pagination-container"></div>
    </main>
    ${u()}
  `,g();const o=document.getElementById("games-grid"),a=document.getElementById("pagination-container");try{const n=await y({page:t,pageSize:s,sort:"top"});o.innerHTML=n.items.map(C).join(""),M(),o.querySelectorAll(".post-item").forEach(i=>{i.onclick=()=>h(`/game/${i.dataset.id}`)}),T(a,t,n.pages,i=>h(`/top-games?page=${i}`))}catch(n){o.innerHTML=`<div class="col-span-full py-16 text-center text-red-400 font-bold">${r(n.message)}</div>`}}async function U(){const e=new URLSearchParams(window.location.search),t=Math.max(1,parseInt(e.get("page")||"1",10)),s=24;c.innerHTML=`
    ${p("","updated-games")}
    <main class="max-w-[1250px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Recent Updates & Patches</h3>
      </div>
      ${A()}
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3.5 sm:gap-4" id="games-grid">
        <div class="col-span-full py-20 text-center text-gray-400 font-semibold flex flex-col items-center justify-center gap-3">
          <div class="w-8 h-8 border-2 border-[#ff0505] border-t-transparent rounded-full animate-spin"></div>
          <span>Loading updated games…</span>
        </div>
      </div>
      <div class="mt-14 flex items-center justify-center gap-2" id="pagination-container"></div>
    </main>
    ${u()}
  `,g();const o=document.getElementById("games-grid"),a=document.getElementById("pagination-container");try{const n=await y({page:t,pageSize:s,sort:"updated"});o.innerHTML=n.items.map(C).join(""),M(),o.querySelectorAll(".post-item").forEach(i=>{i.onclick=()=>h(`/game/${i.dataset.id}`)}),T(a,t,n.pages,i=>h(`/updated-games?page=${i}`))}catch(n){o.innerHTML=`<div class="col-span-full py-16 text-center text-red-400 font-bold">${r(n.message)}</div>`}}async function N(){c.innerHTML=`
    ${p("","games-list")}
    <main class="max-w-[1250px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">SteamRIP Complete Games List (A-Z)</h3>
      </div>
      <p class="text-xs text-gray-400 mb-6 leading-relaxed">
        Browse the complete archive of pre-installed PC games. Use the search filter or click any letter to jump directly.
      </p>

      <!-- Instant Filter Bar -->
      <div class="bg-[#181326] border border-[#2c2242] rounded-xl p-4 mb-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="relative w-full sm:w-96">
          <input
            type="search"
            id="list-filter-input"
            placeholder="Type to filter titles instantly…"
            class="w-full bg-[#120e1e] border border-[#2f2448] rounded-lg py-2 pl-9 pr-4 text-xs font-semibold text-white placeholder-gray-400 focus:outline-none focus:border-[#ff0505]"
          >
          <svg class="w-4 h-4 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
        <div id="list-counter" class="text-xs text-gray-400 font-bold">Loading titles…</div>
      </div>

      <!-- Table Container -->
      <div class="bg-[#140f21] border border-[#241a36] rounded-xl overflow-hidden shadow-xl" id="list-table-container">
        <div class="py-16 text-center text-gray-400 flex flex-col items-center justify-center gap-3">
          <div class="w-8 h-8 border-2 border-[#ff0505] border-t-transparent rounded-full animate-spin"></div>
          <span>Loading catalog index…</span>
        </div>
      </div>
    </main>
    ${u()}
  `,g();try{let n=function(l){if(l.length===0){o.innerHTML='<div class="p-8 text-center text-xs text-gray-400">No games matched your filter.</div>';return}const d=l.map((f,x)=>`
          <tr onclick="goRoute('/game/${f.id}')" class="hover:bg-[#201833] cursor-pointer transition border-b border-[#201831] last:border-none text-xs">
            <td class="py-3 px-4 text-gray-400 font-mono text-[11px] w-12">${x+1}</td>
            <td class="py-3 px-4 font-bold text-white">${r(f.title)}</td>
            <td class="py-3 px-4 text-[#ff0505] font-semibold">${r(f.category||L(f.title,f.slug))}</td>
            <td class="py-3 px-4 text-gray-400">${r(f.file_size||"Full Version")}</td>
            <td class="py-3 px-4 text-right">
              <span class="inline-flex items-center gap-1 text-[#ff0505] font-bold text-xs hover:underline">
                Download &rarr;
              </span>
            </td>
          </tr>
        `).join("");o.innerHTML=`
        <table class="w-full text-left">
          <thead>
            <tr class="bg-[#1a142b] border-b border-[#281f3d] text-[11px] uppercase tracking-wider text-gray-400 font-bold">
              <th class="py-3 px-4">#</th>
              <th class="py-3 px-4">Game Title</th>
              <th class="py-3 px-4">Category</th>
              <th class="py-3 px-4">Size</th>
              <th class="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            ${d}
          </tbody>
        </table>
      `};var e=n;const t=await y({page:1,pageSize:100,sort:"title"}),s=t.items||[],o=document.getElementById("list-table-container"),a=document.getElementById("list-counter");a&&(a.textContent=`Showing ${s.length} of ${t.total} games in database`),n(s);const i=document.getElementById("list-filter-input");i&&(i.oninput=l=>{const d=l.target.value.toLowerCase().trim(),f=s.filter(x=>x.title.toLowerCase().includes(d)||x.category&&x.category.toLowerCase().includes(d));n(f)})}catch(t){const s=document.getElementById("list-table-container");s&&(s.innerHTML=`<div class="p-8 text-center text-red-400 font-bold">${r(t.message)}</div>`)}}function W(){const e=[{title:"Top Co-op & Multiplayer Hits",slug:"multiplayer",desc:"Best games to play online with friends without complicated setup.",count:"15+ Games"},{title:"Horror & Psychological Thrillers",slug:"horror",desc:"Terrifying survival horror, indie nightmares, and escape rooms.",count:"20+ Games"},{title:"High-Octane Racing & Simulators",slug:"racing",desc:"Top racing simulators, arcade drifters, and realistic vehicle mechanics.",count:"23+ Games"},{title:"Epic Role-Playing & Open Worlds",slug:"rpg",desc:"Immersive open worlds, fantasy epics, and deep story campaigns.",count:"10+ Games"},{title:"Virtual Reality (VR) Masterpieces",slug:"vr",desc:"Full VR experiences ready for Quest, Index, and PCVR headsets.",count:"8+ Games"},{title:"Action & Fast Shooters",slug:"action",desc:"Adrenaline-fueled combat, tactical shooters, and high-energy brawlers.",count:"25+ Games"}];c.innerHTML=`
    ${p("","collections")}
    <main class="max-w-[1250px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Featured Game Collections</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        ${e.map(t=>`
          <div onclick="goRoute('/category/${t.slug}')" class="bg-[#181326] border border-[#2b2140] hover:border-[#ff0505] rounded-2xl p-6 cursor-pointer transition-all group flex flex-col justify-between shadow-xl">
            <div>
              <span class="text-[10px] font-black uppercase text-[#ff0505] bg-[#2d121c] px-2.5 py-1 rounded-full border border-red-950 inline-block mb-3">${r(t.count)}</span>
              <h3 class="text-base font-bold text-white group-hover:text-[#ff0505] transition mb-2">${r(t.title)}</h3>
              <p class="text-xs text-gray-400 leading-relaxed mb-4">${r(t.desc)}</p>
            </div>
            <span class="inline-flex items-center gap-1.5 text-xs font-bold text-white group-hover:text-[#ff0505] transition">
              <span>Explore Collection</span>
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            </span>
          </div>
        `).join("")}
      </div>
    </main>
    ${u()}
  `,g()}function _(){const e=[{q:"Are the games on SteamRIP completely safe to download?",a:"Yes, 100%. All games are obtained directly from clean verified sources and pre-installed without any adware, cryptominers, or malware. We compress the raw clean game directories so you can extract and play immediately."},{q:"Do I need to install or run any installer setups?",a:"No! That is the core advantage of SteamRIP. All games are 100% Pre-Installed. You simply extract the compressed archive (.zip or .rar) using WinRAR or 7-Zip, and run the game's executable (.exe) as Administrator."},{q:"What should I do if I get a missing DLL error (e.g. VCRUNTIME140.dll or MSVCP140.dll)?",a:"Missing DLL errors occur when your Windows installation lacks the Microsoft Visual C++ Redistributable packages or DirectX runtimes. Download and install the 'Visual C++ All-in-One' runtime pack (2015-2022) and run the DirectX End-User Runtime installer."},{q:"Why is Windows Defender or my antivirus flagging the game executable?",a:"Game fixes and Steam emulators are frequently detected as false positives by Windows Defender and third-party antivirus software because they redirect Steam API calls. You can safely add the game directory to your antivirus exclusions list."},{q:"Where are game save files located?",a:"Depending on the game, save files are usually stored in '%APPDATA%', '%LOCALAPPDATA%', or 'C:\\Users\\YourUser\\Saved Games', or directly within the game folder under a 'saves' or 'Steam_settings' subfolder."},{q:"Can I play multiplayer and online co-op?",a:"Games with a '+ Co-op' or 'Multiplayer' tag include online fixes (often using Steam Spacewar AppID 480). To play with friends, both you and your friend must have Steam open in the background."}];c.innerHTML=`
    ${p("","faq")}
    <main class="max-w-[1000px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Frequently Asked Questions (FAQ)</h3>
      </div>
      <p class="text-xs text-gray-400 mb-8 leading-relaxed">
        Everything you need to know about downloading, extracting, and playing pre-installed games from SteamRIP.
      </p>

      <div class="flex flex-col gap-4">
        ${e.map((t,s)=>`
          <div class="bg-[#181326] border border-[#2b2140] rounded-xl overflow-hidden shadow-lg">
            <div class="p-5 flex items-start gap-3">
              <span class="w-6 h-6 rounded-full bg-[#ff0505] text-white flex items-center justify-center font-bold text-xs flex-shrink-0 mt-0.5">${s+1}</span>
              <div>
                <h4 class="text-sm font-bold text-white mb-2">${r(t.q)}</h4>
                <p class="text-xs text-gray-300 leading-relaxed">${r(t.a)}</p>
              </div>
            </div>
          </div>
        `).join("")}
      </div>
    </main>
    ${u()}
  `,g()}function Z(){c.innerHTML=`
    ${p("","steps-for-games")}
    <main class="max-w-[1050px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">How to Run Pre-Installed Games (Step-by-Step)</h3>
      </div>
      <p class="text-xs text-gray-400 mb-8 leading-relaxed">
        Follow these steps to guarantee your game runs without crashes, missing DLLs, or startup issues.
      </p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <!-- Step 1 -->
        <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div class="w-10 h-10 rounded-full bg-[#ff0505] text-white font-black flex items-center justify-center text-sm mb-4">1</div>
            <h4 class="text-base font-bold text-white mb-2">1. Download Game</h4>
            <p class="text-xs text-gray-400 leading-relaxed mb-4">
              Click any of the verified direct download mirrors (Buzzheavier, FileDitch, Mega, GoFile). We recommend using a download manager (IDM, FDM, or Brave Browser) for top speeds.
            </p>
          </div>
          <span class="text-[11px] text-emerald-400 font-bold flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            No Speed Caps
          </span>
        </div>

        <!-- Step 2 -->
        <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div class="w-10 h-10 rounded-full bg-[#c537ff] text-white font-black flex items-center justify-center text-sm mb-4">2</div>
            <h4 class="text-base font-bold text-white mb-2">2. Extract Archive</h4>
            <p class="text-xs text-gray-400 leading-relaxed mb-4">
              Once downloaded, right click the .rar or .zip file and select <strong>'Extract Here'</strong> using WinRAR or 7-Zip. Do NOT run the game directly from inside the archive!
            </p>
          </div>
          <span class="text-[11px] text-purple-400 font-bold flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            Use WinRAR or 7-Zip
          </span>
        </div>

        <!-- Step 3 -->
        <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div class="w-10 h-10 rounded-full bg-[#007dff] text-white font-black flex items-center justify-center text-sm mb-4">3</div>
            <h4 class="text-base font-bold text-white mb-2">3. Run as Administrator</h4>
            <p class="text-xs text-gray-400 leading-relaxed mb-4">
              Open the extracted folder, find the main game .exe file, right-click it, and select <strong>'Run as Administrator'</strong>. That's it! Have fun and play.
            </p>
          </div>
          <span class="text-[11px] text-sky-400 font-bold flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            Zero Installation Needed
          </span>
        </div>
      </div>

      <!-- Essential Runtimes Notice -->
      <div class="bg-[#161224] border border-[#2e2348] rounded-2xl p-6">
        <h4 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-[#ff0505]"></span>
          Essential Gaming Runtimes (Prevent Errors)
        </h4>
        <p class="text-xs text-gray-300 leading-relaxed mb-4">
          If you encounter errors such as "Application unable to start correctly (0xc000007b)" or missing DLL files, you must have all Microsoft Visual C++ runtimes and DirectX installed:
        </p>
        <div class="flex flex-wrap gap-3">
          <a href="https://aka.ms/vs/17/release/vc_redist.x64.exe" target="_blank" rel="noopener" class="px-4 py-2 bg-[#211a36] hover:bg-[#2e234c] border border-[#372a56] rounded-lg text-xs font-bold text-white transition inline-flex items-center gap-2">
            <span>Visual C++ 2015-2022 (x64)</span>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          </a>
          <a href="https://www.microsoft.com/en-us/download/details.aspx?id=35" target="_blank" rel="noopener" class="px-4 py-2 bg-[#211a36] hover:bg-[#2e234c] border border-[#372a56] rounded-lg text-xs font-bold text-white transition inline-flex items-center gap-2">
            <span>DirectX End-User Runtimes</span>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          </a>
        </div>
      </div>
    </main>
    ${u()}
  `,g()}function Q(){c.innerHTML=`
    ${p("","about")}
    <main class="max-w-[950px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">About SteamRIP</h3>
      </div>
      <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 sm:p-8 space-y-4 text-xs sm:text-sm text-gray-300 leading-relaxed shadow-xl">
        <p>
          <strong>SteamRIP</strong> was created to deliver free pre-installed PC games without convoluted setups, suspicious installers, or speed limits.
        </p>
        <p>
          Every title on our platform is <strong>100% Pre-Installed</strong>. Our games are thoroughly compressed with no content removed, preserving all audio, cinematic video, and bonus materials while dramatically reducing download time.
        </p>
        <h4 class="text-sm font-bold text-white pt-2">Our Core Principles:</h4>
        <ul class="list-disc pl-5 space-y-1.5 text-gray-400">
          <li><strong>No Installers:</strong> Never worry about repackers or installer errors. Extract and play.</li>
          <li><strong>High-Speed Cloud Mirrors:</strong> Multiple direct fast hosts (Buzzheavier, FileDitch, Mega, GoFile).</li>
          <li><strong>Regular Updates:</strong> Continuous patching to latest game builds, DLCs, and co-op fixes.</li>
          <li><strong>Zero Malware:</strong> Complete transparency, zero deceptive adware, and verified files.</li>
        </ul>
      </div>
    </main>
    ${u()}
  `,g()}function J(){c.innerHTML=`
    ${p("","request-games")}
    <main class="max-w-[850px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Request a Game</h3>
      </div>
      <p class="text-xs text-gray-400 mb-6 leading-relaxed">
        Can't find a title in our database? Submit a request and our automated scrapers will index and upload it.
      </p>

      <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 sm:p-8 shadow-xl">
        <form onsubmit="handleRequestSubmit(event)" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">Game Title *</label>
            <input type="text" id="req-title" required placeholder="e.g. Black Myth: Wukong" class="w-full bg-[#120e1e] border border-[#2c2242] rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-[#ff0505]">
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">Steam or Store URL (Optional)</label>
            <input type="url" id="req-url" placeholder="https://store.steampowered.com/app/..." class="w-full bg-[#120e1e] border border-[#2c2242] rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-[#ff0505]">
          </div>
          <div>
            <label class="block text-xs font-bold text-gray-300 mb-1">Additional Notes</label>
            <textarea id="req-note" rows="3" placeholder="Specify required build version, DLCs, or multiplayer preference..." class="w-full bg-[#120e1e] border border-[#2c2242] rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-[#ff0505]"></textarea>
          </div>
          <button type="submit" class="shortc-button purple !py-2.5 !px-6 text-xs font-bold">Submit Game Request</button>
        </form>
      </div>
    </main>
    ${u()}
  `,g()}window.handleRequestSubmit=e=>{e.preventDefault();const t=document.getElementById("req-title").value;H(`Request submitted for "${t}"!`),e.target.reset()};function Y(){c.innerHTML=`
    ${p()}
    <main class="max-w-[950px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Privacy Policy</h3>
      </div>
      <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 sm:p-8 space-y-4 text-xs sm:text-sm text-gray-300 leading-relaxed shadow-xl">
        <p>Your privacy is important to us. SteamRIP does not collect any personal identity information, credit cards, or tracking cookies from our visitors.</p>
        <p>Log files and standard web server telemetry (IP address, user agent, requested pages) are strictly used for DDoS protection, traffic analytics, and infrastructure maintenance.</p>
      </div>
    </main>
    ${u()}
  `,g()}function X(){c.innerHTML=`
    ${p()}
    <main class="max-w-[950px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Terms & Conditions</h3>
      </div>
      <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 sm:p-8 space-y-4 text-xs sm:text-sm text-gray-300 leading-relaxed shadow-xl">
        <p>By using SteamRIP, you agree that files provided on this site are for testing, educational, and evaluation purposes only.</p>
        <p>We encourage all users to support the game developers by purchasing original copies on Steam, Epic Games, GOG, or respective official stores.</p>
      </div>
    </main>
    ${u()}
  `,g()}function K(){c.innerHTML=`
    ${p()}
    <main class="max-w-[850px] mx-auto px-4 py-8">
      <div class="the-global-title has-block-head-4 mb-4">
        <h3 class="the-subtitle">Contact Us</h3>
      </div>
      <div class="bg-[#181326] border border-[#2b2140] rounded-2xl p-6 sm:p-8 space-y-4 shadow-xl">
        <p class="text-xs text-gray-300 leading-relaxed">
          For DMCA queries, broken mirror links, or general feedback, join our active Community Discord or contact us directly.
        </p>
        <div class="pt-2">
          <a href="https://discord.gg/NBVFJsmy9y" target="_blank" rel="noopener" class="shortc-button purple !py-2.5 !px-6 text-xs inline-flex items-center gap-2">
            <span>Join Discord Support</span>
          </a>
        </div>
      </div>
    </main>
    ${u()}
  `,g()}function ee(e){return e?e.includes("<p")||e.includes("<div")||e.includes("<br")?e.replace(/<style[^>]*>.*?<\/style>/gi,"").replace(/<script[^>]*>.*?<\/script>/gi,"").replace(/<(?!\/?(p|strong|b|em|i|br|ul|li)\b)[^>]+>/gi,""):`<p>${r(e)}</p>`:"<p>Pre-installed game ready to play without complex installation steps.</p>"}async function G(e){c.innerHTML=`
    ${p()}
    <main class="max-w-[1150px] mx-auto px-4 py-8">
      <div class="py-24 text-center text-gray-400 font-semibold flex flex-col items-center justify-center gap-3">
        <div class="w-8 h-8 border-2 border-[#ff0505] border-t-transparent rounded-full animate-spin"></div>
        <span>Loading game & mirrors…</span>
      </div>
    </main>
    ${u()}
  `,g();try{const t=await D(e),s=I(t.thumbnail_url),o=t.category||L(t.title,t.slug),a=E(t.title),n=q(t.title),i=t.files||[],l=(t.files||[]).filter(b=>{const m=(b.url||"").toLowerCase(),v=(b.label||"").toLowerCase();return!(m.includes("://steamrip.com")||m.includes("//steamrip.com")||v.includes("buzzheavier")||m.includes("bzzhr.to")||m.includes("buzzheavier"))}),d=l.filter(b=>{const m=(b.url||"").toLowerCase();return(b.label||"").toLowerCase().includes("gofile")||m.includes("gofile.io")}),f=d.length>0?d:l;let x="";f.length>0?x=f.map(b=>{let m="text-purple-400 bg-purple-950/60 border-purple-800/40",v="purple";const w=b.label||"Direct Download";return w.toLowerCase().includes("gofile")?(m="text-emerald-400 bg-emerald-950/60 border-emerald-800/40",v="green"):w.toLowerCase().includes("fileditch")?(m="text-sky-400 bg-sky-950/60 border-sky-800/40",v="blue"):w.toLowerCase().includes("megadb")?(m="text-rose-400 bg-rose-950/60 border-rose-800/40",v="purple"):w.toLowerCase().includes("direct")&&(m="text-emerald-400 bg-emerald-950/60 border-emerald-800/40",v="green"),`
            <div class="bg-[#1b152b] border border-[#2c2244] hover:border-[#5a4382] rounded-xl p-4 flex flex-col justify-between transition-all group">
              <div class="flex items-center justify-between mb-3">
                <span class="inline-flex items-center gap-1.5 text-xs font-bold ${m} border px-2.5 py-1 rounded-full">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  ${r(w)}
                </span>
                <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Fast Cloud</span>
              </div>
              <div class="flex items-center gap-2 mt-2">
                <a
                  href="${r(b.url)}"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="shortc-button ${v} flex-1 !py-3 !text-xs !font-bold"
                  onclick="showToast('Opening download mirror in new tab…')"
                >
                  <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                  <span>Download (${r(w)})</span>
                </a>
                <button
                  onclick="copyLink('${r(b.url)}')"
                  class="p-3 bg-[#130f1e] border border-[#2e2346] hover:border-[#ff0505] text-gray-300 hover:text-white rounded-lg text-xs font-bold transition flex items-center justify-center flex-shrink-0"
                  title="Copy direct mirror URL"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                </button>
              </div>
            </div>
          `}).join(""):x=`
        <div class="col-span-full p-5 bg-[#1b152b] border border-[#2c2244] rounded-xl text-center">
          <div class="inline-flex items-center gap-2 text-xs font-bold text-gray-200 mb-1">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Cloud Mirrors Indexing
          </div>
          <p class="text-[11px] text-gray-400">High-speed cloud mirrors (GoFile, FileDitch, Mega) are currently indexing for this archive. Please refresh in a moment.</p>
        </div>
      `;const P=t.requirements?`
        <div class="mt-8 bg-[#141022] border border-[#2a203f] rounded-2xl p-6">
          <div class="the-global-title !mb-4 border-none pb-0">
            <h3 class="the-subtitle text-base">System Requirements</h3>
          </div>
          <div class="text-xs sm:text-sm text-gray-300 whitespace-pre-wrap leading-relaxed font-mono bg-[#100c1b] p-4 sm:p-5 rounded-xl border border-[#231b36]">
            ${r(t.requirements)}
          </div>
        </div>
      `:"";c.innerHTML=`
      ${p()}
      <div class="relative overflow-hidden">
        <div class="absolute inset-0 bg-cover bg-center blur-3xl opacity-20 pointer-events-none scale-125" style="background-image: url('${r(s)}');"></div>
        <div class="absolute inset-0 bg-gradient-to-b from-transparent via-[#0e0b16] to-[#0e0b16] pointer-events-none"></div>

        <main class="relative max-w-[1150px] mx-auto px-4 py-8">
          <!-- Breadcrumb -->
          <nav class="flex items-center gap-2 text-xs text-gray-400 mb-6">
            <a href="/" onclick="goRoute('/'); return false;" class="hover:text-white transition">Home</a>
            <span>/</span>
            <a href="/category/${r(o.toLowerCase())}" onclick="goRoute('/category/${r(o.toLowerCase())}'); return false;" class="hover:text-[#ff0505] transition">${r(o)}</a>
            <span>/</span>
            <span class="text-white font-medium truncate max-w-sm sm:max-w-md">${r(n)}</span>
          </nav>

          <!-- Title -->
          <h1 class="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white mb-6 leading-tight tracking-tight">
            ${r(t.title)}
          </h1>

          <!-- Content Grid -->
          <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
            <!-- Poster -->
            <div class="md:col-span-5 lg:col-span-4">
              <div class="sticky top-24">
                <div class="relative rounded-2xl overflow-hidden border border-[#3b2e56] shadow-2xl bg-[#120e1e] group">
                  ${s?`<img src="${r(s)}" alt="${r(t.title)}" class="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105" onerror="this.onerror=null;this.src='/logo.png';">`:'<div class="w-full aspect-[3/4] bg-[#171324] flex items-center justify-center text-gray-500 text-xs">No Poster Available</div>'}
                  ${a?`<span class="tagmetafield">${r(a)}</span>`:""}
                  <span class="post-cat">${r(o)}</span>
                </div>

                <div class="mt-4 flex items-center gap-2">
                  <a href="#download-section" class="flex-1 py-3 bg-[#ff0505] hover:bg-[#d90429] text-white text-xs font-black uppercase text-center rounded-xl shadow-lg transition">
                    Jump to Download
                  </a>
                  <button
                    onclick="copyLink(window.location.href)"
                    class="px-3.5 py-3 bg-[#1b152b] hover:bg-[#281f3e] border border-[#2f2348] text-gray-300 hover:text-white rounded-xl text-xs font-bold transition flex items-center justify-center"
                    title="Share Game"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"></path></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Meta & Mirrors -->
            <div class="md:col-span-7 lg:col-span-8 flex flex-col gap-6">
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div class="bg-[#171224] border border-[#281f3b] rounded-xl p-3.5 text-center">
                  <span class="text-[10px] uppercase font-bold text-gray-400 block mb-1">Status</span>
                  <span class="text-xs font-extrabold text-emerald-400 flex items-center justify-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    Pre-Installed
                  </span>
                </div>
                <div class="bg-[#171224] border border-[#281f3b] rounded-xl p-3.5 text-center">
                  <span class="text-[10px] uppercase font-bold text-gray-400 block mb-1">Size</span>
                  <span class="text-xs font-extrabold text-white">${r(t.file_size||"Full Version")}</span>
                </div>
                <div class="bg-[#171224] border border-[#281f3b] rounded-xl p-3.5 text-center">
                  <span class="text-[10px] uppercase font-bold text-gray-400 block mb-1">Category</span>
                  <span class="text-xs font-extrabold text-[#ff0505]">${r(o)}</span>
                </div>
                <div class="bg-[#171224] border border-[#281f3b] rounded-xl p-3.5 text-center">
                  <span class="text-[10px] uppercase font-bold text-gray-400 block mb-1">OS</span>
                  <span class="text-xs font-extrabold text-white">Windows 64-Bit</span>
                </div>
              </div>

              <!-- Overview -->
              <div class="bg-[#151122] border border-[#281f3b] rounded-2xl p-6">
                <div class="the-global-title !mb-4 border-none pb-0">
                  <h3 class="the-subtitle text-base">Game Description</h3>
                </div>
                <div class="text-xs sm:text-sm text-gray-300 leading-relaxed space-y-3 prose-dark">
                  ${ee(t.description)}
                </div>
              </div>

              <!-- Notice Box -->
              <div class="bg-[#24131d] border-l-4 border-[#ff0505] p-4 rounded-r-xl text-xs text-gray-300 leading-relaxed flex items-start gap-3">
                <svg class="w-5 h-5 text-[#ff0505] flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                <div>
                  <strong class="text-white block mb-0.5">Important Installation Notice:</strong>
                  This game is 100% pre-installed. You do not need to install it. If you face any missing DLL or runtime errors, ensure DirectX and the Visual C++ Redistributables (2015-2022) are installed on your PC.
                </div>
              </div>

              <!-- Download Section -->
              <div id="download-section" class="bg-[#161224] border border-[#2b2140] rounded-2xl p-6 shadow-xl">
                <div class="the-global-title !mb-4 border-none pb-0 flex items-center justify-between">
                  <h3 class="the-subtitle text-base">Direct Download Links</h3>
                  <span class="text-[11px] text-gray-400 font-semibold">${i.length} Mirror(s) Available</span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  ${x}
                </div>
              </div>
            </div>
          </div>

          ${P}

          <!-- How to Run -->
          <div class="mt-8 bg-[#141022] border border-[#2a203f] rounded-2xl p-6">
            <div class="the-global-title !mb-4 border-none pb-0">
              <h3 class="the-subtitle text-base">How to Run Pre-Installed Games</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div class="bg-[#1a1429] border border-[#281f3d] p-5 rounded-xl flex items-start gap-3.5">
                <span class="w-7 h-7 rounded-full bg-[#ff0505] text-white flex items-center justify-center font-black flex-shrink-0 text-xs">1</span>
                <div>
                  <strong class="text-white block mb-1 text-sm font-bold">1. Download</strong>
                  <p class="text-gray-400 leading-relaxed">Click any of the download mirrors above to obtain the compressed game archive.</p>
                </div>
              </div>
              <div class="bg-[#1a1429] border border-[#281f3d] p-5 rounded-xl flex items-start gap-3.5">
                <span class="w-7 h-7 rounded-full bg-[#c537ff] text-white flex items-center justify-center font-black flex-shrink-0 text-xs">2</span>
                <div>
                  <strong class="text-white block mb-1 text-sm font-bold">2. Extract</strong>
                  <p class="text-gray-400 leading-relaxed">Right-click the downloaded .rar/.zip file and select 'Extract Here' using WinRAR or 7-Zip.</p>
                </div>
              </div>
              <div class="bg-[#1a1429] border border-[#281f3d] p-5 rounded-xl flex items-start gap-3.5">
                <span class="w-7 h-7 rounded-full bg-[#007dff] text-white flex items-center justify-center font-black flex-shrink-0 text-xs">3</span>
                <div>
                  <strong class="text-white block mb-1 text-sm font-bold">3. Play Game</strong>
                  <p class="text-gray-400 leading-relaxed">Open the extracted directory and run the main executable (.exe) as Administrator.</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
      ${u()}
    `}catch(t){c.innerHTML=`
      ${p()}
      <main class="max-w-[1100px] mx-auto px-4 py-20 text-center text-red-400 font-bold">
        <h2 class="text-xl mb-2">Game Not Found</h2>
        <p class="text-xs text-gray-400 mb-6">${r(t.message)}</p>
        <button onclick="goRoute('/');" class="shortc-button purple !py-2.5 !px-6 text-xs">Back to Games Catalog</button>
      </main>
      ${u()}
    `}}function T(e,t,s,o){if(!e||s<=1){e&&(e.innerHTML="");return}let a="";a+=`
    <button class="page-nav-pill" ${t<=1?"disabled":""} data-page="${t-1}">
      &larr; Prev
    </button>
  `;const n=Math.max(1,t-2),i=Math.min(s,t+2);for(let l=n;l<=i;l++)a+=`
      <button class="page-nav-pill ${l===t?"active":""}" data-page="${l}">
        ${l}
      </button>
    `;a+=`
    <button class="page-nav-pill" ${t>=s?"disabled":""} data-page="${t+1}">
      Next &rarr;
    </button>
  `,e.innerHTML=a,e.querySelectorAll("button[data-page]").forEach(l=>{l.onclick=()=>{const d=parseInt(l.dataset.page,10);!isNaN(d)&&d>=1&&d<=s&&d!==t&&(o(d),window.scrollTo({top:0,behavior:"smooth"}))}})}function h(e){window.history.pushState({},"",e),j(),window.scrollTo({top:0,behavior:"smooth"})}window.goRoute=h;window.toggleMobileMenu=()=>{const e=document.getElementById("mobile-drawer");e&&e.classList.toggle("hidden")};window.copyLink=e=>{e&&(navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(e).then(()=>H("Direct link copied to clipboard!")).catch(()=>prompt("Copy download link:",e)):prompt("Copy download link:",e))};window.triggerRandomGame=async()=>{try{const e=await z();e&&e.id&&h(`/game/${e.id}`)}catch{H("Unable to pick random game right now.")}};async function j(){const e=window.location.pathname;if(e==="/"||e==="")await $();else if(e.startsWith("/game/")){const t=e.split("/")[2]||"",s=parseInt(t,10);if(!isNaN(s))await G(s);else if(t)try{const o=await y({search:t,pageSize:1});o.items&&o.items.length>0?await G(o.items[0].id):await $()}catch{await $()}else await $()}else if(e.startsWith("/category/")){const t=e.split("/")[2]||"";await O(t)}else e==="/top-games"?await V():e==="/updated-games"?await U():e==="/games-list"?await N():e==="/collections"?W():e==="/faq"?_():e==="/steps-for-games"?Z():e==="/about"?Q():e==="/request-games"?J():e==="/privacy-policy"?Y():e==="/terms-and-conditions"?X():e==="/contact-us"?K():await $()}window.addEventListener("popstate",j);document.addEventListener("DOMContentLoaded",j);
