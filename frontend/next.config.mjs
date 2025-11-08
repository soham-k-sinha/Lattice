/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Reduce dev mode noise
  devIndicators: {
    buildActivityPosition: 'bottom-right',
  },
  // Suppress hydration warnings (from browser extensions)
  reactStrictMode: false,
}

export default nextConfig
