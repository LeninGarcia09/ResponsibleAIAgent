/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://rai-backend.graymoss-a8a3aef8.westus3.azurecontainerapps.io/api',
  },
}

module.exports = nextConfig
