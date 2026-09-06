import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { TokenChips } from "@/components/studio/TokenChips";
import { DEFAULT_CONTROLS, useSessionStore } from "@/lib/store/sessionStore";
import type { AnalysedToken } from "@/lib/schemas/text";

const tokens: AnalysedToken[] = [
  {
    index: 0,
    surface: "मुझे",
    start_offset: 0,
    end_offset: 4,
    script: "Devanagari",
    language: "hi",
    normalized: "मुझे",
    token_type: "word",
    codepoints: [],
    pronunciation: { phonemes: "m ʊ dʒ ʱ eː", confidence: 0.95, is_uncertain: false, source: "g2p" },
  },
  {
    index: 1,
    surface: "meeting",
    start_offset: 5,
    end_offset: 12,
    script: "Latin",
    language: "en",
    normalized: "meeting",
    token_type: "word",
    codepoints: [],
    pronunciation: { phonemes: "m iː t ɪ ŋ", confidence: 0.5, is_uncertain: true, source: "g2p" },
  },
];

beforeEach(() => {
  useSessionStore.setState({
    tokens,
    selectedTokenIndex: null,
    controls: DEFAULT_CONTROLS,
  });
});

describe("TokenChips", () => {
  it("renders a chip per word token with an uncertainty indicator", () => {
    render(<TokenChips />);
    expect(screen.getByText("मुझे")).toBeInTheDocument();
    expect(screen.getByText("meeting")).toBeInTheDocument();
    expect(screen.getByLabelText("Uncertain pronunciation")).toBeInTheDocument();
  });

  it("selects a token on click and updates the store", () => {
    render(<TokenChips />);
    fireEvent.click(screen.getByText("meeting"));
    expect(useSessionStore.getState().selectedTokenIndex).toBe(1);
  });

  it("deselects an already-selected token on a second click", () => {
    render(<TokenChips />);
    fireEvent.click(screen.getByText("meeting"));
    fireEvent.click(screen.getByText("meeting"));
    expect(useSessionStore.getState().selectedTokenIndex).toBeNull();
  });
});
