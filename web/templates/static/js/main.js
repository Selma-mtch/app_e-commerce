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
