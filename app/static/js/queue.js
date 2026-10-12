/**
 * CareSync - Live Queue Board Real-time Polling
 * Refreshes queue display automatically every 5 seconds.
 */

document.addEventListener('DOMContentLoaded', function () {
  const displayBoard = document.getElementById('liveQueueBoard');
  if (!displayBoard) return;

  function refreshQueue() {
    fetch('/queue/api/live')
      .then(res => res.json())
      .then(data => {
        if (!data || !data.queue) return;

        const consulting = data.queue.filter(q => q.status === 'In Consultation');
        const waiting = data.queue.filter(q => q.status === 'Waiting');

        // Update In Consultation Hero
        const activeContainer = document.getElementById('activeConsultationsList');
        if (activeContainer) {
          if (consulting.length === 0) {
            activeContainer.innerHTML = '<div class="text-muted p-4 text-center">No active consultations in progress.</div>';
          } else {
            activeContainer.innerHTML = consulting.map(c => `
              <div class="col-md-6 mb-3">
                <div class="queue-hero-token">
                  <div class="small text-uppercase text-light mb-1">Room: ${c.doctor_code || 'OPD'}</div>
                  <div class="token-big">#${c.queue_number}</div>
                  <div class="h5 mt-2 mb-0 text-white">${c.patient_name}</div>
                  <div class="small text-info">${c.doctor_name} (${c.specialty})</div>
                </div>
              </div>
            `).join('');
          }
        }

        // Update Waiting List
        const waitingContainer = document.getElementById('waitingTokensList');
        if (waitingContainer) {
          if (waiting.length === 0) {
            waitingContainer.innerHTML = '<div class="text-muted p-3 text-center">Waiting list is currently empty.</div>';
          } else {
            waitingContainer.innerHTML = waiting.map(w => `
              <div class="queue-token-pill">
                <div class="token-num">#${w.queue_number}</div>
                <div class="small text-white fw-bold text-truncate">${w.patient_name}</div>
                <div class="text-muted" style="font-size: 0.7rem">${w.doctor_name}</div>
              </div>
            `).join('');
          }
        }

        // Update last updated indicator
        const timeInd = document.getElementById('queueLastUpdated');
        if (timeInd) {
          const now = new Date();
          timeInd.innerText = `Last updated: ${now.toLocaleTimeString()}`;
        }
      })
      .catch(err => console.error("Error updating live queue:", err));
  }

  // Poll every 5 seconds
  setInterval(refreshQueue, 5000);
});
