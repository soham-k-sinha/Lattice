"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

interface AIMessageProps {
  content: string;
  thinking?: string[];
  action?: "card" | "split" | "tracker";
}

type FormattedBlock =
  | { type: "paragraph"; content: string }
  | { type: "list"; items: string[] }
  | { type: "code"; content: string; language?: string };

const isListLine = (line: string) => /^[-*]\s+/.test(line);
const isCodeFence = (line: string) => line.trim().startsWith("```");

const cleanText = (value: string) =>
  value
    .replace(/^[-*]+\s*/g, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*\*/g, "")
    .replace(/`([^`]+)`/g, "$1")
    .trim();

const LABEL_ICONS: Record<string, string> = {
  "purchase recommendation": "🎯",
  spending: "💸",
  market: "📊",
  sentiment: "🗣️",
  confidence: "✅",
  "additional advice": "💡",
};

const SECTION_EMOJI: Record<string, string> = {
  "reasoning summary": "🧠",
  "financial reasoning (transparent)": "📒",
  "market reasoning (transparent)": "📈",
  "sentiment reasoning (transparent)": "🌐",
};

function normalizeHeadings(raw: string): string {
  return raw
    .replace(/Additional Advice:/gi, "\nAdditional Advice:")
    .replace(
      /Financial Reasoning\s*\(transparent\):/gi,
      "\nFinancial Reasoning (transparent):"
    )
    .replace(
      /Market Reasoning\s*\(transparent\):/gi,
      "\nMarket Reasoning (transparent):"
    )
    .replace(
      /Sentiment Reasoning\s*\(transparent\):/gi,
      "\nSentiment Reasoning (transparent):"
    )
    .replace(/Reasoning Summary/gi, "\nReasoning Summary");
}

function formatContent(content: string): FormattedBlock[] {
  if (!content) return [];

  const normalized = normalizeHeadings(content);
  const lines = normalized.split("\n");
  const blocks: FormattedBlock[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];

    if (!line.trim()) {
      index += 1;
      continue;
    }

    if (isCodeFence(line)) {
      const language = line.trim().slice(3).trim() || undefined;
      index += 1;
      const codeLines: string[] = [];
      while (index < lines.length && !isCodeFence(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      if (index < lines.length && isCodeFence(lines[index])) {
        index += 1;
      }
      blocks.push({ type: "code", content: codeLines.join("\n"), language });
      continue;
    }

    if (isListLine(line)) {
      const items: string[] = [];
      while (index < lines.length && isListLine(lines[index])) {
        items.push(lines[index].replace(/^[-*]\s+/, ""));
        index += 1;
      }
      blocks.push({ type: "list", items });
      continue;
    }

    const paragraphLines: string[] = [];
    while (
      index < lines.length &&
      lines[index].trim() &&
      !isListLine(lines[index]) &&
      !isCodeFence(lines[index])
    ) {
      paragraphLines.push(lines[index]);
      index += 1;
    }
    const paragraphContent = paragraphLines.join(" ").trim();
    if (paragraphContent) {
      blocks.push({ type: "paragraph", content: paragraphContent });
    }
  }

  return blocks;
}

export function AIMessage({ content, thinking, action }: AIMessageProps) {
  const [currentThinking, setCurrentThinking] = useState(0);

  useEffect(() => {
    if (thinking && thinking.length > 0) {
      const interval = setInterval(() => {
        setCurrentThinking((prev) => {
          if (prev < thinking.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [thinking]);

  const formattedBlocks = useMemo(() => formatContent(content), [content]);

  return (
    <div className="flex gap-4">
      {/* Reasoning line */}
      <div className="relative w-1 mt-1">
        {thinking ? (
          <motion.div
            className="absolute top-0 left-0 w-full bg-accent rounded-full"
            initial={{ height: "0%" }}
            animate={{ height: "100%" }}
            transition={{ duration: 2, ease: "easeInOut" }}
          />
        ) : (
          <div className="w-full h-6 bg-accent/30 rounded-full" />
        )}
      </div>

      <div className="flex-1">
        <div className="inline-block max-w-2xl">
          <AnimatePresence mode="wait">
            {thinking ? (
              <motion.div
                key="thinking"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                className="bg-card border border-border rounded-2xl px-5 py-3 shadow-sm"
              >
                <p className="text-sm text-muted-foreground thinking-pulse">
                  {thinking[currentThinking]}
                </p>
              </motion.div>
            ) : content ? (
              <motion.div
                key="content"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-card border border-border rounded-2xl px-6 py-5 shadow-sm space-y-4"
              >
                <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-foreground/60">
                  <span role="img" aria-hidden="true">
                    🤖
                  </span>
                  <span>Assistant</span>
                </div>
                {formattedBlocks.map((block, blockIndex) => {
                  if (block.type === "paragraph") {
                    const text = cleanText(block.content);
                    if (!text || text.toLowerCase() === "assistant") {
                      return null;
                    }

                    const headingKey = text.toLowerCase();
                    if (SECTION_EMOJI[headingKey]) {
                      return (
                        <div
                          key={`section-${blockIndex}`}
                          className="pt-2 text-sm font-semibold text-foreground flex items-center gap-2"
                        >
                          <span role="img" aria-hidden="true">
                            {SECTION_EMOJI[headingKey]}
                          </span>
                          <span>
                            {text.replace(/\s*\(transparent\)\s*/i, "")}
                          </span>
                        </div>
                      );
                    }

                    const labelMatch = text.match(/^([^:]+):\s*(.*)$/);
                    if (labelMatch) {
                      const [, rawLabel, value] = labelMatch;
                      const labelKey = rawLabel.trim().toLowerCase();
                      const icon = LABEL_ICONS[labelKey];
                      return (
                        <div
                          key={`label-${blockIndex}`}
                          className="flex gap-3 text-sm leading-relaxed text-foreground/90"
                        >
                          <span className="font-semibold flex items-center gap-1 whitespace-nowrap">
                            {icon && (
                              <span role="img" aria-hidden="true">
                                {icon}
                              </span>
                            )}
                            {rawLabel.trim()}:
                          </span>
                          <span className="flex-1">{value.trim()}</span>
                        </div>
                      );
                    }

                    return (
                      <p
                        key={`paragraph-${blockIndex}`}
                        className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap"
                      >
                        {text}
                      </p>
                    );
                  }

                  if (block.type === "list") {
                    return (
                      <ul
                        key={`list-${blockIndex}`}
                        className="list-disc pl-5 space-y-1 text-sm leading-relaxed text-foreground/90"
                      >
                        {block.items.map((item, itemIndex) => (
                          <li key={itemIndex}>{cleanText(item)}</li>
                        ))}
                      </ul>
                    );
                  }

                  if (block.type === "code") {
                    return (
                      <pre
                        key={`code-${blockIndex}`}
                        className="bg-muted border border-border rounded-xl text-xs font-mono whitespace-pre-wrap px-4 py-3 overflow-x-auto"
                      >
                        <code>{block.content}</code>
                      </pre>
                    );
                  }

                  return null;
                })}
                <div className="pt-1 text-xs text-muted-foreground">
                  ✨ Crafted with your recent spend and live market signals.
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
