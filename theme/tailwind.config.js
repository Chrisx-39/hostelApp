/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../hostel/templates/**/*.html',
    './static_src/**/*.css',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
}
