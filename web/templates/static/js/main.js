// Affiche automatiquement les messages flash Bootstrap en toast
document.addEventListener("DOMContentLoaded", function() {
  const toastElList = [].slice.call(document.querySelectorAll('.toast'));
  toastElList.forEach(toastEl => new bootstrap.Toast(toastEl).show());
});

// HTMX: le token CSRF est injecté côté base.html; pas d'action ici.

// Petite notification après ajout panier (évite les erreurs si la fonction est appelée côté templates)
function showAddedToast() {
  // Rien de complexe ici, on laisse le flash backend gérer l'info.
}

// Autocomplétion d'adresse (France) via api-adresse.data.gouv.fr
document.addEventListener("DOMContentLoaded", () => {
  const addrInputs = document.querySelectorAll('[data-addr-autocomplete="fr"]');
  addrInputs.forEach((input) => {
    const results = input.parentElement.querySelector("[data-addr-results]");
    if (!results) return;

    let controller;
    const fillFields = (props) => {
      const line2Sel = input.dataset.addrLine2;
      const postalSel = input.dataset.addrPostal;
      const citySel = input.dataset.addrCity;
      const countrySel = input.dataset.addrCountry;
      input.value = [props.housenumber, props.street || props.name].filter(Boolean).join(" ").trim();
      if (line2Sel) {
        const el = document.querySelector(line2Sel);
        if (el) el.value = "";
      }
      if (postalSel) {
        const el = document.querySelector(postalSel);
        if (el) el.value = props.postcode || "";
      }
      if (citySel) {
        const el = document.querySelector(citySel);
        if (el) el.value = props.city || props.locality || "";
      }
      if (countrySel) {
        const el = document.querySelector(countrySel);
        if (el) el.value = "France";
      }
    };

    const renderResults = (features) => {
      results.innerHTML = "";
      results.classList.remove("show");
      if (!features.length) return;
      features.slice(0, 5).forEach((feat) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "dropdown-item";
        btn.textContent = feat.properties.label;
        btn.addEventListener("click", () => {
          fillFields(feat.properties);
          results.innerHTML = "";
          results.classList.remove("show");
        });
        results.appendChild(btn);
      });
      results.classList.add("show");
    };

    const search = async (q) => {
      if (controller) controller.abort();
      controller = new AbortController();
      try {
        const res = await fetch(`https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(q)}&limit=5`, {
          signal: controller.signal,
        });
        const data = await res.json();
        renderResults(data.features || []);
      } catch (e) {
        if (e.name !== "AbortError") {
          results.innerHTML = "";
        }
      }
    };

    input.addEventListener("input", () => {
      const q = input.value.trim();
      if (q.length < 3) {
        results.innerHTML = "";
        results.classList.remove("show");
        return;
      }
      search(q);
    });

    document.addEventListener("click", (ev) => {
      if (!results.contains(ev.target) && ev.target !== input) {
        results.innerHTML = "";
        results.classList.remove("show");
      }
    });
  });
});
