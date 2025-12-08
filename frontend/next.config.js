/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // This is set at build time via Docker build args in CI/CD
    // Falls back to localhost for local development
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api',
  },
}

module.exports = nextConfig
