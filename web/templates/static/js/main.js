// Affiche automatiquement les messages flash Bootstrap en toast
document.addEventListener("DOMContentLoaded", function() {
  const toastElList = [].slice.call(document.querySelectorAll('.toast'));
  toastElList.forEach(toastEl => new bootstrap.Toast(toastEl).show());
});

// HTMX: le token CSRF est injecté côté base.html; pas d'action ici.
