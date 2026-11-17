document.addEventListener('click', function (e) {
  var btn = e.target.closest('.add-to-cart');
  if (!btn) return;
  e.preventDefault();

  fetch(btn.getAttribute('href'), {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(function (res) {
      if (res.redirected) {          // کاربر وارد نشده، می‌ره صفحه ورود
        window.location.href = res.url;
        return null;
      }
      return res.json();
    })
    .then(function (data) {
      if (!data) return;
      var badge = document.getElementById('cartCountBadge');
      if (badge) {
        badge.textContent = data.count;
        badge.classList.toggle('zero', data.count === 0);
      }
    });
});