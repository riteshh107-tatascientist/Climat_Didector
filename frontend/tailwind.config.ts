/** ClimateGuard AI design system.
 * Deliberately restrained palette: deep green (brand/healthy), teal
 * (secondary), amber/orange/red reserved ONLY for risk semantics — never
 * used decoratively elsewhere in the app. See docs/design-system.md. */
import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9f4", 100: "#dbf0e3", 200: "#b8e0c9", 300: "#8bcaa9",
          400: "#5aad85", 500: "#37906a", 600: "#277355", 700: "#1f5c46",
          800: "#1a4a3a", 900: "#163d30", 950: "#0b221a",
        },
        teal: {
          50: "#effcfb", 100: "#d6f5f3", 200: "#b0eae7", 300: "#7ad9d5",
          400: "#42bfbc", 500: "#279fa0", 600: "#1e7f82", 700: "#1c6669",
          800: "#1c5255", 900: "#1a4547",
        },
        risk: {
          low: "#2f9e5c",
          moderate: "#d99a1f",
          high: "#e2711d",
          critical: "#d1352b",
        },
        surface: {
          DEFAULT: "#ffffff",
          subtle: "#f7f8f7",
          muted: "#eef1ef",
          dark: "#0f1713",
        },
        ink: {
          DEFAULT: "#14201b",
          muted: "#4b5a53",
          faint: "#7c8b83",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      borderRadius: {
        xl: "0.875rem",
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 23 17 / 0.06), 0 1px 3px 0 rgb(15 23 17 / 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
