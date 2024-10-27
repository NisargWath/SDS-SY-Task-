let currentStep = 1;
const totalSteps = 5;
const steps = document.querySelectorAll(".form-step");

function showStep(step) {
  steps.forEach((stepElement, index) => {
    stepElement.classList.toggle("active", index === step - 1);
  });
}

function nextStep() {
  if (currentStep < totalSteps) {
    currentStep++;
    showStep(currentStep);
  }
}

function prevStep() {
  if (currentStep > 1) {
    currentStep--;
    showStep(currentStep);
  }
}

showStep(currentStep);

function openPaymentModal() {
  document.getElementById("paymentModal").style.display = "flex";
}

function closePaymentModal() {
  document.getElementById("paymentModal").style.display = "none";
}

function completePayment() {
  alert("Registration Completed successfully!");
  closePaymentModal();
}
