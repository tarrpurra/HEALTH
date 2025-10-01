/** @type {import('next').NextConfig} */
const normalizePath = (path) => {
  const withLeadingSlash = path ? (path.startsWith("/") ? path : `/${path}`) : "/api/ws"
  if (withLeadingSlash.length > 1 && withLeadingSlash.endsWith("/")) {
    return withLeadingSlash.slice(0, -1)
  }
  return withLeadingSlash
}

const normalizeDestination = (url) => {
  if (!url) return url
  if (url.startsWith("ws://")) {
    return `http://${url.slice(5)}`
  }
  if (url.startsWith("wss://")) {
    return `https://${url.slice(6)}`
  }
  return url
}

const wsProxyPath = normalizePath(process.env.NEXT_PUBLIC_WS_PATH)
const wsServiceUrl = normalizeDestination(process.env.WS_SERVICE_URL)

const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    if (!wsServiceUrl) {
      return []
    }

    return [
      {
        source: wsProxyPath,
        destination: wsServiceUrl,
      },
    ]
  },
}

export default nextConfig
