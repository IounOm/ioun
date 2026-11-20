// Accessibility smoke test with vitest-axe (web-kit, see README.md).
// Setup once: `bun add -d vitest jsdom @testing-library/react vitest-axe`,
// vitest config `environment: "jsdom"`, and in the setup file:
//   import "vitest-axe/extend-expect";
// axe in jsdom cannot check color contrast or layout: contrast is covered by the token rules and
// the Chrome DevTools MCP Lighthouse audit (docs/patterns/ui-review.md).
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";

import { SignInForm } from "./sign-in-form";

describe("SignInForm accessibility", () => {
  it("has no axe violations in its default state", async () => {
    const { container } = render(<SignInForm />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it("has no axe violations when showing a field error", async () => {
    const { container } = render(<SignInForm initialError="invalid" />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
