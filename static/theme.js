const STORAGE_KEY = "serviceManagerTheme";
const themeOptions = document.querySelectorAll("[data-theme-choice]");
const validThemes = ["light", "dark", "system"];

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;

  themeOptions.forEach((option) => {
    const isSelected = option.dataset.themeChoice === theme;
    option.setAttribute("aria-pressed", String(isSelected));
  });
}

function loadTheme() {
  const storedTheme = localStorage.getItem(STORAGE_KEY);

  if (validThemes.includes(storedTheme)) {
    return storedTheme;
  }

  return "system";
}

function saveTheme(theme) {
  localStorage.setItem(STORAGE_KEY, theme);
  applyTheme(theme);
}

const currentTheme = loadTheme();
applyTheme(currentTheme);

themeOptions.forEach((option) => {
  option.addEventListener("click", () => saveTheme(option.dataset.themeChoice));
});
