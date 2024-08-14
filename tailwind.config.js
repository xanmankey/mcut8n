/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/**/*.js"],
  safelist: [
    // Font sizes
    "text-xs",
    "text-sm",
    "text-tiny",
    "text-base",
    "text-lg",
    "text-xl",
    "text-2xl",
    "text-3xl",
    "text-4xl",
    "text-5xl",
    "text-6xl",
    "text-7xl",
    "text-8xl",
    "text-9xl",
  ],
  theme: {
    screens: {
      sm: { max: "640px" },
      // => @media (min-width: 640px) { ... }

      md: { max: "768px" },
      // => @media (min-width: 768px) { ... }

      lg: { max: "1024px" },
      // => @media (min-width: 1024px) { ... }

      xl: { max: "1280px" },
      // => @media (min-width: 1280px) { ... }

      "2xl": { max: "1536px" },
      // => @media (min-width: 1536px) { ... }
    },
  },
  plugins: [],
};
