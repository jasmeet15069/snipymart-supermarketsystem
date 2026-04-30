import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1f2933",
        line: "#d9e2ec",
        mint: "#0f9f6e",
        coral: "#d64545",
        amber: "#b7791f",
        cyan: "#087ea4"
      },
      boxShadow: {
        panel: "0 1px 2px rgba(31,41,51,0.08)"
      }
    }
  },
  plugins: []
};

export default config;
