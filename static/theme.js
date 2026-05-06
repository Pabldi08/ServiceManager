const STORAGE_KEY = "serviceManagerTheme";
const validThemes = ["light", "dark", "system"];
const themeOptions = document.querySelectorAll("[data-theme-choice]");
const themeIndicator = document.querySelector(".theme-indicator");
const hostDialog = document.getElementById("host-dialog");
const dialogOpeners = document.querySelectorAll("[data-dialog-open]");
const dialogClosers = document.querySelectorAll("[data-dialog-close]");
let lastDialogTrigger = null;

function loadTheme() {
  const storedTheme = localStorage.getItem(STORAGE_KEY);
  return validThemes.includes(storedTheme) ? storedTheme : "system";
}

function moveThemeIndicator(theme) {
  if (!themeIndicator) {
    return;
  }

  const index = validThemes.indexOf(theme);
  themeIndicator.style.transform = `translateX(${index * 100}%)`;
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  moveThemeIndicator(theme);

  themeOptions.forEach((option) => {
    const isSelected = option.dataset.themeChoice === theme;
    option.setAttribute("aria-pressed", String(isSelected));
  });
}

function saveTheme(theme) {
  localStorage.setItem(STORAGE_KEY, theme);
  applyTheme(theme);
}

function openDialog(dialog, trigger) {
  if (!dialog) {
    return;
  }

  lastDialogTrigger = trigger;
  dialog.showModal();
}

function closeDialog(dialog) {
  if (!dialog || !dialog.open) {
    return;
  }

  dialog.close();
  lastDialogTrigger?.focus();
}

applyTheme(loadTheme());

themeOptions.forEach((option) => {
  option.addEventListener("click", () => saveTheme(option.dataset.themeChoice));
});

dialogOpeners.forEach((opener) => {
  opener.addEventListener("click", () => {
    const dialog = document.getElementById(opener.dataset.dialogOpen);
    openDialog(dialog, opener);
  });
});

dialogClosers.forEach((closer) => {
  closer.addEventListener("click", () => closeDialog(closer.closest("dialog")));
});

hostDialog?.addEventListener("click", (event) => {
  if (event.target === hostDialog) {
    closeDialog(hostDialog);
  }
});

hostDialog?.addEventListener("close", () => {
  lastDialogTrigger?.focus();
});
