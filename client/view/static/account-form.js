document.querySelectorAll("[data-password-confirmation]").forEach((form) => {
  const password = form.querySelector("[data-password]");
  const confirmation = form.querySelector("[data-confirm-password]");
  if (!password || !confirmation) return;

  const isOptional = !password.required;
  const message = "Les deux mots de passe doivent être identiques.";

  function validatePasswords() {
    const hasPassword = password.value.length > 0;
    const hasConfirmation = confirmation.value.length > 0;
    const hasMismatch = password.value !== confirmation.value;

    password.setCustomValidity(
      isOptional && hasConfirmation && !hasPassword ? message : ""
    );
    confirmation.setCustomValidity(
      (!isOptional && hasMismatch) ||
      (isOptional && hasPassword && (!hasConfirmation || hasMismatch))
        ? message
        : ""
    );
  }

  password.addEventListener("input", validatePasswords);
  confirmation.addEventListener("input", validatePasswords);
  form.addEventListener("submit", (event) => {
    validatePasswords();
    if (!password.checkValidity() || !confirmation.checkValidity()) {
      event.preventDefault();
      form.reportValidity();
    }
  });
});
