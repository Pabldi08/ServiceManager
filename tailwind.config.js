/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./app/**/*.py",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      boxShadow: {
        app: "0 18px 50px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
};
