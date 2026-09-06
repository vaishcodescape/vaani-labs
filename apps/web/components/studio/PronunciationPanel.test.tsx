import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { PronunciationPanel } from "@/components/studio/PronunciationPanel";
import { DEFAULT_CONTROLS, useSessionStore } from "@/lib/store/sessionStore";
import type { AnalysedToken } from "@/lib/schemas/text";

vi.mock("@/lib/api/client", () => ({
  api: {
    pronunciationCandidates: vi.fn().mockResolvedValue({
      surface: "meeting",
      candidates: [
        { phonemes: "m iː t ɪ ŋ", confidence: 0.55, source: "g2p" },
        { phonemes: "m iː ʈ ɪ ŋ", confidence: 0.31, source: "g2p-alt" },
      ],
    }),
    createLexiconEntry: vi.fn().mockResolvedValue({}),
  },
}));

const token: AnalysedToken = {
  index: 0,
  surface: "meeting",
  start_offset: 0,
  end_offset: 7,
  script: "Latin",
  language: "en",
  normalized: "meeting",
  token_type: "word",
  codepoints: [],
  pronunciation: { phonemes: "m iː t ɪ ŋ", confidence: 0.55, is_uncertain: true, source: "g2p" },
};

beforeEach(() => {
  useSessionStore.setState({
    tokens: [token],
    selectedTokenIndex: 0,
    controls: DEFAULT_CONTROLS,
  });
});

describe("PronunciationPanel", () => {
  it("shows a prompt when no token is selected", () => {
    useSessionStore.setState({ selectedTokenIndex: null });
    render(<PronunciationPanel />);
    expect(screen.getByText(/select a token/i)).toBeInTheDocument();
  });

  it("lists fetched candidates and applies the selected one to the store", async () => {
    render(<PronunciationPanel />);
    await waitFor(() => expect(screen.getByText("m iː ʈ ɪ ŋ")).toBeInTheDocument());

    fireEvent.click(screen.getByText("m iː ʈ ɪ ŋ"));

    expect(useSessionStore.getState().tokens[0]?.pronunciation.phonemes).toBe("m iː ʈ ɪ ŋ");
    expect(useSessionStore.getState().tokens[0]?.pronunciation.source).toBe("g2p-alt");
  });
});
