/**
 * CareSync - Main Interactive Script
 * Handles mobile sidebar, appointment slot loading, form validations, and alerts.
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const toggleBtn = document.getElementById('mobileMenuToggle');
  const sidebar = document.getElementById('appSidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });

    // Close when clicking outside
    document.addEventListener('click', function (e) {
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target) && sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
      }
    });
  }

  // 2. Auto-dismiss flash notifications
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s ease';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // 3. Confirmation Dialog on Destructive Actions
  const confirmElements = document.querySelectorAll('.confirm-action');
  confirmElements.forEach(function (element) {
    element.addEventListener('click', function (e) {
      const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed with this action?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // 4. Dynamic Appointment Slot Picker
  const doctorSelect = document.getElementById('bookingDoctorSelect');
  const dateInput = document.getElementById('bookingDateInput');
  const slotsContainer = document.getElementById('slotsContainer');
  const selectedSlotInput = document.getElementById('selectedTimeSlot');

  function fetchSlots() {
    if (!doctorSelect || !dateInput || !slotsContainer) return;

    const doctorId = doctorSelect.value;
    const dateVal = dateInput.value;

    if (!doctorId || !dateVal) {
      slotsContainer.innerHTML = '<p class="text-muted small">Please select a doctor and date to view available appointment slots.</p>';
      return;
    }

    slotsContainer.innerHTML = '<div class="text-center py-3"><div class="spinner-border spinner-border-sm text-primary" role="status"></div> Loading available slots...</div>';

    fetch(`/appointments/slots?doctor_id=${doctorId}&date=${dateVal}`)
      .then(res => res.json())
      .then(data => {
        slotsContainer.innerHTML = '';
        if (!data.slots || data.slots.length === 0) {
          slotsContainer.innerHTML = '<div class="alert alert-warning small mb-0">No appointment slots available for this doctor on the selected date. Please choose another date.</div>';
          if (selectedSlotInput) selectedSlotInput.value = '';
          return;
        }

        const grid = document.createElement('div');
        grid.className = 'slots-grid';

        let hasAvailable = false;
        data.slots.forEach(slot => {
          const slotBtn = document.createElement('div');
          slotBtn.className = `slot-item ${slot.is_available ? 'available' : 'booked'}`;
          slotBtn.innerHTML = `<div>${slot.time}</div><small class="d-block" style="font-size: 0.65rem">${slot.status}</small>`;

          if (slot.is_available) {
            hasAvailable = true;
            slotBtn.addEventListener('click', function () {
              document.querySelectorAll('.slot-item').forEach(el => el.classList.remove('selected'));
              slotBtn.classList.add('selected');
              if (selectedSlotInput) {
                selectedSlotInput.value = slot.time;
              }
            });
          }

          grid.appendChild(slotBtn);
        });

        if (!hasAvailable) {
          slotsContainer.innerHTML = '<div class="alert alert-secondary small mb-2">All time slots on this date are either past or already booked.</div>';
        }

        slotsContainer.appendChild(grid);
      })
      .catch(err => {
        slotsContainer.innerHTML = '<p class="text-danger small">Error loading appointment slots. Please retry.</p>';
      });
  }

  if (doctorSelect && dateInput) {
    doctorSelect.addEventListener('change', fetchSlots);
    dateInput.addEventListener('change', fetchSlots);
    // Initial fetch if values present
    if (doctorSelect.value && dateInput.value) {
      fetchSlots();
    }
  }

  // 5. Table Quick Search
  const tableSearchInput = document.getElementById('tableSearchInput');
  if (tableSearchInput) {
    tableSearchInput.addEventListener('input', function () {
      const term = this.value.toLowerCase();
      const rows = document.querySelectorAll('.searchable-table tbody tr');
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
      });
    });
  }
});
