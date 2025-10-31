/**
 * Mock for rehype-raw
 * Used in Jest tests to avoid ESM issues
 */

export default function rehypeRaw() {
  return () => {};
}
