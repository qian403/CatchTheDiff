/**
 * Environment-aware logger.
 * In production builds, console output is suppressed to avoid leaking stack
 * traces. Hook a reporting backend here later if needed.
 */
const isDev = import.meta.env.DEV;

export const logger = {
  error: (...args: unknown[]): void => {
    if (isDev) console.error(...args);
  },
  warn: (...args: unknown[]): void => {
    if (isDev) console.warn(...args);
  },
  info: (...args: unknown[]): void => {
    if (isDev) console.info(...args);
  },
};
