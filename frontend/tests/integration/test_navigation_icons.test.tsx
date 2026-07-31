import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { App } from "../../src/app/App";
import { AppThemeProvider } from "../../src/theme";
import { primaryNavigation } from "../../src/app/navigation";

function renderApp() {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ title: "Not found" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    }),
  );

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <AppThemeProvider>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/inventory"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    </AppThemeProvider>,
  );
}

describe("navigation icon coverage", () => {
  it("renders every primary destination with a labeled icon pill", () => {
    renderApp();

    for (const destination of primaryNavigation) {
      const link = screen.getByRole("link", { name: destination.label });
      expect(link).toBeInTheDocument();
      expect(link.querySelector("svg")).not.toBeNull();
    }
  });
});
