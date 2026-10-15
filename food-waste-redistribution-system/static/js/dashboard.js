/**
 * EcoDine AI - Dashboard Visualizations (Chart.js)
 * Renders interactive surplus distribution, category breakdown, and status metrics.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check if Chart.js is available
  if (typeof Chart === 'undefined') return;

  // Custom Color Themes
  const greenPalette = ['#15803d', '#22c55e', '#86efac', '#f97316', '#fbbf24', '#0284c7'];

  // 1. Food Category Breakdown Chart (Doughnut)
  const categoryCanvas = document.getElementById('categoryChart');
  if (categoryCanvas) {
    try {
      const rawLabels = categoryCanvas.getAttribute('data-labels') || '[]';
      const rawValues = categoryCanvas.getAttribute('data-values') || '[]';
      const labels = JSON.parse(rawLabels);
      const values = JSON.parse(rawValues);

      new Chart(categoryCanvas.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: labels.length ? labels : ['Cooked Meals', 'Bakery & Bread', 'Fresh Produce', 'Dairy & Sweets'],
          datasets: [{
            data: values.length ? values : [90, 30, 22, 14],
            backgroundColor: greenPalette,
            borderWidth: 2,
            borderColor: '#ffffff',
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                boxWidth: 14,
                padding: 14,
                font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 }
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return ` ${context.label}: ${context.raw} kg`;
                }
              }
            }
          },
          cutout: '68%'
        }
      });
    } catch (e) {
      console.warn("Failed to render categoryChart:", e);
    }
  }

  // 2. Redistribution Flow Status Chart (Bar)
  const statusCanvas = document.getElementById('statusChart');
  if (statusCanvas) {
    try {
      const availableKg = parseFloat(statusCanvas.getAttribute('data-available') || '104.5');
      const claimedKg = parseFloat(statusCanvas.getAttribute('data-claimed') || '44.0');
      const redistributedKg = parseFloat(statusCanvas.getAttribute('data-redistributed') || '59.5');

      new Chart(statusCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['Available (Active)', 'Claimed / In-Transit', 'Successfully Redistributed'],
          datasets: [{
            label: 'Food Volume (kg)',
            data: [availableKg, claimedKg, redistributedKg],
            backgroundColor: ['#22c55e', '#f97316', '#15803d'],
            borderRadius: 8,
            maxBarThickness: 45
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return ` ${context.raw} kg surplus`;
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9' },
              ticks: {
                callback: function(val) { return val + ' kg'; },
                font: { family: "'Plus Jakarta Sans', sans-serif" }
              }
            },
            x: {
              grid: { display: false },
              ticks: { font: { family: "'Plus Jakarta Sans', sans-serif", weight: '600' } }
            }
          }
        }
      });
    } catch (e) {
      console.warn("Failed to render statusChart:", e);
    }
  }
});
