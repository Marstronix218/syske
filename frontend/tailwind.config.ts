import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#6366f1",
        energy: {
          high: "#f97316",
          steady: "#14b8a6",
          calm: "#60a5fa",
        },
      },
    },
  },
  plugins: [],
};

export default config;
