 document.addEventListener("DOMContentLoaded", function() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(toastEl => new bootstrap.Toast(toastEl).show());
  });