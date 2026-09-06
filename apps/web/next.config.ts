import path from "node:path";

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Pin the workspace root to this app: an unrelated lockfile higher up
  // the filesystem tree would otherwise make Next.js guess the wrong
  // root for file tracing.
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
