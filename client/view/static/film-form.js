"use strict";

function initializeEntitySelector(selector) {
  const mode = selector.dataset.selectionMode;
  const inputName = selector.dataset.inputName;
  const searchUrl = selector.dataset.searchUrl;
  const minimumLength = Number(selector.dataset.minQueryLength || 1);
  const searchInput = selector.querySelector("[data-entity-search]");
  const selectedList = selector.querySelector("[data-selected-items]");
  const results = selector.querySelector("[data-search-results]");
  const selectedInputs = selector.querySelector("[data-selected-inputs]");
  const labelInputName = selectedInputs.dataset.labelInputName;
  const selectedItems = new Map(
    Array.from(selectedInputs.querySelectorAll("[data-selected-input]")).map(
      (input) => [input.value, input.dataset.label || ""],
    ),
  );
  let matches = [];
  let debounceTimer;
  let activeRequest;

  function renderSelected() {
    selectedList.replaceChildren();
    selectedInputs.replaceChildren();

    selectedItems.forEach((label, id) => {
      const item = document.createElement("li");
      item.className = "selected-entity";

      const text = document.createElement("span");
      text.textContent = label;

      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "selected-entity-remove";
      removeButton.dataset.removeEntity = id;
      removeButton.setAttribute("aria-label", `Retirer ${label} de la sélection`);
      removeButton.textContent = "Retirer";

      const input = document.createElement("input");
      input.type = "hidden";
      input.name = inputName;
      input.value = id;
      input.dataset.selectedInput = "";
      input.dataset.label = label;

      item.append(text, removeButton);
      selectedList.append(item);
      selectedInputs.append(input);

      if (labelInputName) {
        const labelInput = document.createElement("input");
        labelInput.type = "hidden";
        labelInput.name = labelInputName;
        labelInput.value = label;
        labelInput.dataset.selectedLabelInput = "";
        selectedInputs.append(labelInput);
      }
    });
  }

  function renderResults() {
    results.replaceChildren();
    const availableItems = matches.filter(
      (item) => !selectedItems.has(String(item.id)),
    );
    if (availableItems.length === 0) {
      results.textContent = "Aucun résultat.";
      return;
    }

    availableItems.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "entity-result";
      button.setAttribute("role", "option");
      button.textContent = option.label;
      button.addEventListener("click", () => {
        if (mode === "single") {
          selectedItems.clear();
        }
        selectedItems.set(String(option.id), option.label);
        renderSelected();
        renderResults();
      });
      results.append(button);
    });
  }

  async function search(query) {
    activeRequest = new AbortController();
    const requestController = activeRequest;
    const url = new URL(searchUrl, window.location.origin);
    url.searchParams.set("q", query);

    try {
      const response = await fetch(url, {
        headers: { Accept: "application/json" },
        signal: requestController.signal,
      });
      if (!response.ok) {
        throw new Error(`Entity search failed with HTTP ${response.status}`);
      }
      const data = await response.json();
      if (!Array.isArray(data)) {
        throw new Error("Entity search returned an invalid response.");
      }
      if (searchInput.value.trim() !== query) return;
      matches = data.filter(
        (item) => item && item.id !== undefined && typeof item.label === "string",
      );
      renderResults();
    } catch (error) {
      if (error.name === "AbortError") return;
      console.error("Entity search failed.", error);
      results.textContent = "La recherche a échoué. Réessayez.";
    }
  }

  function scheduleSearch() {
    clearTimeout(debounceTimer);
    activeRequest?.abort();
    matches = [];
    const query = searchInput.value.trim();
    if (query.length < minimumLength) {
      results.textContent = query
        ? `Saisissez au moins ${minimumLength} caractère(s).`
        : "Saisissez un terme pour rechercher.";
      return;
    }

    results.textContent = "Recherche en cours…";
    debounceTimer = setTimeout(() => search(query), 250);
  }

  selectedList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-entity]");
    if (!button) return;
    selectedItems.delete(button.dataset.removeEntity);
    renderSelected();
    renderResults();
  });
  searchInput.addEventListener("input", scheduleSearch);

  renderSelected();
  results.textContent = `Saisissez au moins ${minimumLength} caractère(s) pour rechercher.`;
}

function initializeSupportRows() {
  const supportRows = document.getElementById("support-rows");
  const supportTemplate = document.getElementById("support-row-template");
  if (!supportRows || !supportTemplate) return;

  function updateSupportFields(row) {
    const typeSelect = row.querySelector("[data-support-type]");
    const mode = typeSelect.selectedOptions[0]?.dataset.mode;
    const physicalField = row.querySelector("[data-physical-field]");
    const digitalField = row.querySelector("[data-digital-field]");
    const locationInput = physicalField.querySelector("input");
    const urlInput = digitalField.querySelector("input");
    const isPhysical = mode === "physical";
    const isDigital = mode === "digital";

    physicalField.hidden = !isPhysical;
    physicalField.style.display = isPhysical ? "grid" : "none";
    digitalField.hidden = !isDigital;
    digitalField.style.display = isDigital ? "grid" : "none";
    locationInput.required = isPhysical;
    urlInput.required = isDigital;
    if (isPhysical) urlInput.value = "";
    if (isDigital) locationInput.value = "";
  }

  function bindSupportRow(row) {
    row.querySelector("[data-support-type]").addEventListener("change", () => {
      updateSupportFields(row);
    });
    row.querySelector("[data-remove-support]").addEventListener("click", () => {
      row.remove();
    });
    updateSupportFields(row);
  }

  supportRows.querySelectorAll("[data-support-row]").forEach(bindSupportRow);

  document.getElementById("add-support").addEventListener("click", () => {
    const row = supportTemplate.content.firstElementChild.cloneNode(true);
    supportRows.append(row);
    bindSupportRow(row);
  });
}

document.querySelectorAll("[data-entity-selector]").forEach(initializeEntitySelector);
initializeSupportRows();
