export function generateId(): string {
  if (typeof globalThis.crypto !== "undefined" && typeof globalThis.crypto.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }

  const fallback = new Uint8Array(16);
  for (let index = 0; index < fallback.length; index += 1) {
    fallback[index] = Math.floor(Math.random() * 256);
  }

  // Format into UUID v4 style: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
  fallback[6] = (fallback[6] & 0x0f) | 0x40;
  fallback[8] = (fallback[8] & 0x3f) | 0x80;

  const hex = Array.from(fallback, (value) => value.toString(16).padStart(2, "0"));
  const segment = (start: number, end: number) => hex.slice(start, end).join("");

  return `${segment(0, 4)}-${segment(4, 6)}-${segment(6, 8)}-${segment(8, 10)}-${segment(10, 16)}`;
}
