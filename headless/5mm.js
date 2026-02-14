document.addEventListener('DOMContentLoaded', function() {
  // SVG hover highlighting: hovering a line, legend entry, or table year row
  // dims all other series
  var svg = document.querySelector('svg');
  if (svg) {
    var svgElements = svg.querySelectorAll(
      '[id^="year-"], [id^="goal-"], [id^="legend-line-"], [id^="legend-text-"]'
    );
    var tableRows = document.querySelectorAll('tr[data-series]');

    function getSeriesKey(el) {
      return el.dataset.series || el.id.replace(/^legend-(?:line|text)-/, '');
    }

    function highlight(key) {
      svgElements.forEach(function(other) {
        if (getSeriesKey(other) !== key) {
          other.classList.add('dimmed');
        }
      });
    }

    function clearHighlight() {
      svgElements.forEach(function(other) {
        other.classList.remove('dimmed');
      });
    }

    svgElements.forEach(function(el) {
      el.addEventListener('mouseenter', function() { highlight(getSeriesKey(el)); });
      el.addEventListener('mouseleave', clearHighlight);
    });

    tableRows.forEach(function(tr) {
      tr.addEventListener('mouseenter', function() { highlight(tr.dataset.series); });
      tr.addEventListener('mouseleave', clearHighlight);
    });
  }

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
