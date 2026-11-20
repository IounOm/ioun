// Accessibility lint — merge into eslint.config.mjs (web-kit, see README.md).
// Next.js: eslint-config-next already registers the jsx-a11y plugin, so only spread the rules.
// Other React stacks: `bun add -d eslint-plugin-jsx-a11y` and keep the plugin import.
import jsxA11y from "eslint-plugin-jsx-a11y";

export const a11y = [
  {
    files: ["**/*.{jsx,tsx}"],
    plugins: { "jsx-a11y": jsxA11y },
    rules: {
      ...jsxA11y.flatConfigs.recommended.rules,
      // Shared UI primitives forward these props; check the rendered element instead.
      "jsx-a11y/label-has-associated-control": ["error", { assert: "either", depth: 3 }],
      "jsx-a11y/no-autofocus": ["error", { ignoreNonDOM: true }],
      "jsx-a11y/anchor-is-valid": "error",
      "jsx-a11y/control-has-associated-label": "error",
    },
  },
];

// eslint.config.mjs:  export default [...base, ...a11y];
