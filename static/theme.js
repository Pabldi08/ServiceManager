const STORAGE_KEY = "serviceManagerTheme";
const validThemes = ["light", "dark"];
const themeToggle = document.querySelector("[data-theme-toggle]");
const themeToggleLabel = document.querySelector("[data-theme-toggle-label]");
const dialogOpeners = document.querySelectorAll("[data-dialog-open]");
const dialogClosers = document.querySelectorAll("[data-dialog-close]");
const dialogs = document.querySelectorAll("dialog");
const autoOpenDialog = document.querySelector("[data-auto-open-dialog]");
let lastDialogTrigger = null;

function loadTheme() {
  const storedTheme = localStorage.getItem(STORAGE_KEY);
  return validThemes.includes(storedTheme) ? storedTheme : "light";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;

  if (!themeToggle || !themeToggleLabel) {
    return;
  }

  const isDark = theme === "dark";
  themeToggle.setAttribute("aria-pressed", String(isDark));
  themeToggle.setAttribute("aria-label", isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
  themeToggleLabel.textContent = isDark ? "Light" : "Dark";
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

themeToggle?.addEventListener("click", () => {
  const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  saveTheme(nextTheme);
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

dialogs.forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
      closeDialog(dialog);
    }
  });

  dialog.addEventListener("close", () => {
    lastDialogTrigger?.focus();
  });
});

if (autoOpenDialog) {
  openDialog(autoOpenDialog, null);
}
