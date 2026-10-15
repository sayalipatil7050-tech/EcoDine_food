/**
 * EcoDine AI - Main Client Script
 * Handles responsive menu, flash alert dismissal, modals, and client validations.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const icon = mobileBtn.querySelector('i');
      if (icon) {
        if (navLinks.classList.contains('active')) {
          icon.classList.remove('fa-bars');
          icon.classList.add('fa-times');
        } else {
          icon.classList.remove('fa-times');
          icon.classList.add('fa-bars');
        }
      }
    });
  }

  // 2. Alert Dismissal
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Auto-dismiss success flash alerts after 6 seconds
  setTimeout(() => {
    document.querySelectorAll('.alert-success').forEach(alert => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 250);
    });
  }, 6000);

  // 3. Smart Redistribution Claim Modal Handler
  const claimButtons = document.querySelectorAll('.open-claim-modal');
  const claimModal = document.getElementById('claimFoodModal');
  const closeModalBtn = document.querySelector('.modal-close-btn');
  const cancelClaimBtn = document.querySelector('.cancel-claim-btn');

  if (claimButtons.length > 0 && claimModal) {
    claimButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        const title = btn.getAttribute('data-title');
        const qty = btn.getAttribute('data-qty');
        const meals = btn.getAttribute('data-meals');
        const donor = btn.getAttribute('data-donor');
        const address = btn.getAttribute('data-address');

        // Fill modal fields
        const modalDonationId = document.getElementById('modalDonationId');
        const modalTitle = document.getElementById('modalFoodTitle');
        const modalInfo = document.getElementById('modalDonationDetails');
        
        if (modalDonationId) modalDonationId.value = id;
        if (modalTitle) modalTitle.textContent = title;
        if (modalInfo) {
          modalInfo.innerHTML = `<strong>${qty} kg</strong> (~${meals} meals) from <em>${donor}</em><br><small><i class="fas fa-map-marker-alt"></i> ${address}</small>`;
        }

        // Set default pickup time to +1 hour from now
        const pickupInput = document.getElementById('estimatedPickupTime');
        if (pickupInput && !pickupInput.value) {
          const now = new Date();
          now.setHours(now.getHours() + 1);
          pickupInput.value = now.toTimeString().substring(0, 5);
        }

        claimModal.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    });

    const closeModal = () => {
      claimModal.classList.remove('active');
      document.body.style.overflow = '';
    };

    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    if (cancelClaimBtn) cancelClaimBtn.addEventListener('click', closeModal);
    
    // Close on clicking backdrop
    claimModal.addEventListener('click', (e) => {
      if (e.target === claimModal) closeModal();
    });
  }

  // 4. Form Submit Loading States
  const forms = document.querySelectorAll('form:not(.no-spin)');
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        const originalText = submitBtn.innerHTML;
        // Check HTML5 validity
        if (form.checkValidity()) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing...`;
          // Fallback reset after 8 seconds in case of slow connection
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
          }, 8000);
        }
      }
    });
  });
});
