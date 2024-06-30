// tailwind.config.js
module.exports = {
  content: [
    '../templates/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      
      backgroundImage: {
        iit: "url('images/bg.png')",
      }
    },
  },
  plugins: [],
}
