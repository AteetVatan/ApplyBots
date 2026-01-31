/**
 * API proxy route to forward requests to the backend.
 * 
 * This ensures headers (including Authorization) are properly forwarded,
 * which Next.js rewrites don't always handle correctly.
 */

import { NextRequest, NextResponse } from "next/server";

// Disable caching for all API routes
export const dynamic = "force-dynamic";
export const fetchCache = "force-no-store";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

async function proxyRequest(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await params;
  const pathname = path.join("/");
  const url = new URL(`/api/v1/${pathname}`, BACKEND_URL);
  
  // Forward query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.append(key, value);
  });

  // Build headers as plain object (more reliable for Node.js fetch)
  const authHeader = request.headers.get("authorization");
  const contentType = request.headers.get("content-type");
  
  // Debug logging
  console.log(`[Proxy] ${request.method} ${pathname}`);
  console.log(`[Proxy] Auth header present: ${!!authHeader}`);
  if (authHeader) {
    console.log(`[Proxy] Auth header value: ${authHeader.substring(0, 30)}...`);
  }
  
  const headers: Record<string, string> = {};
  if (authHeader) {
    headers["Authorization"] = authHeader;
  }
  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  // Get request body for non-GET requests
  let body: BodyInit | null = null;
  if (request.method !== "GET" && request.method !== "HEAD") {
    body = await request.text();
  }

  console.log(`[Proxy] Forwarding to: ${url.toString()}`);
  console.log(`[Proxy] Headers being sent:`, JSON.stringify(headers));

  try {
    const response = await fetch(url.toString(), {
      method: request.method,
      headers,
      body,
      cache: "no-store",
    });

    // Forward the response
    const responseData = await response.text();
    
    console.log(`[Proxy] Backend response: ${response.status} ${response.statusText}`);
    if (response.status >= 400) {
      console.log(`[Proxy] Error response body: ${responseData}`);
    }
    
    // Handle 204 No Content - cannot have a body
    if (response.status === 204) {
      return new NextResponse(null, {
        status: 204,
        statusText: "No Content",
      });
    }
    
    return new NextResponse(responseData, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "application/json",
      },
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return NextResponse.json(
      { detail: "Backend service unavailable" },
      { status: 503 }
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  return proxyRequest(request, context);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  return proxyRequest(request, context);
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  return proxyRequest(request, context);
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  return proxyRequest(request, context);
}

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  return proxyRequest(request, context);
}
