import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    reactStrictMode: true,
    images: {
        domains: ["localhost"],
    },
    // API proxy is handled by src/app/api/v1/[...path]/route.ts
    // to properly forward Authorization headers
};

export default nextConfig;
