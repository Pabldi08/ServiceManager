const STORAGE_KEY = "serviceManagerTheme";
const themeSelect = document.getElementById("theme-select");

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
}

function loadTheme() {
  return localStorage.getItem(STORAGE_KEY) || "system";
}

function saveTheme(theme) {
  localStorage.setItem(STORAGE_KEY, theme);
  applyTheme(theme);
}

const currentTheme = loadTheme();
applyTheme(currentTheme);

if (themeSelect) {
  themeSelect.value = currentTheme;
  themeSelect.addEventListener("change", () => saveTheme(themeSelect.value));
}
