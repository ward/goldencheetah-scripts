document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.sortable').forEach(function(th) {
    th.addEventListener('click', function() {
      var table = th.closest('table');
      var col = parseInt(th.dataset.col);
      var rows = Array.from(table.querySelectorAll('tr')).filter(function(r) {
        return !r.querySelector('th');
      });
      var asc = th.dataset.sort === 'desc';
      document.querySelectorAll('.sortable').forEach(function(h) { delete h.dataset.sort; });
      th.dataset.sort = asc ? 'asc' : 'desc';
      rows.sort(function(a, b) {
        var av = parseFloat(a.cells[col].textContent.replace(/,/g, '')) || 0;
        var bv = parseFloat(b.cells[col].textContent.replace(/,/g, '')) || 0;
        return asc ? av - bv : bv - av;
      });
      rows.forEach(function(row) { table.appendChild(row); });
    });
  });
});
