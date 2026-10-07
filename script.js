const bookingForm = document.getElementById("bookingForm");
const bookingStatus = document.getElementById("booking-status");
const serviceDetail = document.getElementById("service-detail");
const serviceDetailImage = document.getElementById("service-detail-image");
const serviceDetailTitle = document.getElementById("service-detail-title");
const serviceDetailPrice = document.getElementById("service-detail-price");
const serviceDetailDescription = document.getElementById("service-detail-description");
const serviceInput = document.getElementById("booking-style");
let selectedService = null;

document.querySelectorAll(".service-card").forEach((card) => {
  card.addEventListener("click", () => {
    selectedService = {
      name: card.dataset.service,
      price: card.dataset.price,
    };
    serviceDetailImage.src = card.dataset.image;
    serviceDetailImage.alt = `${selectedService.name} style example from the portfolio`;
    serviceDetailTitle.textContent = selectedService.name;
    serviceDetailPrice.textContent = selectedService.price;
    serviceDetailDescription.textContent = card.dataset.description;
    serviceDetail.showModal();
  });
});

serviceDetail.querySelector(".service-detail-close").addEventListener("click", () => {
  serviceDetail.close();
});

serviceDetail.addEventListener("click", (event) => {
  if (event.target === serviceDetail) {
    serviceDetail.close();
  }
});

document.getElementById("choose-service").addEventListener("click", () => {
  if (!selectedService) {
    return;
  }

  serviceInput.value = `${selectedService.name} (${selectedService.price})`;
  serviceDetail.close();
  bookingForm.scrollIntoView({ behavior: "smooth", block: "center" });
  serviceInput.focus({ preventScroll: true });
});

bookingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  bookingStatus.textContent = "";

  const submitButton = bookingForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;

  const formData = new FormData(bookingForm);
  const requestData = Object.fromEntries(formData.entries());
  requestData.details = requestData.details.trim();

  try {
    const response = await fetch("/api/bookings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData),
    });
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "We couldn't save your request. Please try again.");
    }

    bookingStatus.textContent = result.message;
    bookingForm.reset();
  } catch (error) {
    bookingStatus.textContent = error instanceof Error
      ? error.message
      : "We couldn't reach the booking service. Please try again later.";
  } finally {
    submitButton.disabled = false;
  }
});