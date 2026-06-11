// utils/textNormalizer.ts
export const normalizeText = (text: string): string => {
  return text.toLowerCase().trim().replace(/[^\w\s\u0900-\u097F]/g, "").replace(/\s+/g, " ");
};

export const extractNumbers = (text: string): number | null => {
  const matches = text.match(/\d+/);
  return matches ? parseInt(matches[0], 10) : null;
};

export const isGreeting = (text: string): boolean => {
  const greetings = ["namaste", "नमस्ते", "हैलो", "hello", "नमस्कार", "hi"];
  return greetings.some((g) => text.includes(g));
};