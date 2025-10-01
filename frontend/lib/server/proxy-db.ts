import { NextRequest, NextResponse } from "next/server"

const DATABASE_SERVICE_URL = process.env.DATABASE_SERVICE_URL

const READ_BODY_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"])

export async function proxyDatabaseRequest(
  request: NextRequest,
  path: string
): Promise<NextResponse> {
  if (!DATABASE_SERVICE_URL) {
    return NextResponse.json(
      { error: "Database service URL is not configured." },
      { status: 500 }
    )
  }

  const search = request.nextUrl.search
  const targetUrl = new URL(`${path}${search}`, DATABASE_SERVICE_URL)

  const headers = new Headers(request.headers)
  headers.set("host", targetUrl.host)
  headers.delete("content-length")

  const init: RequestInit = {
    method: request.method,
    headers,
    redirect: "manual",
  }

  if (READ_BODY_METHODS.has(request.method)) {
    const body = await request.arrayBuffer()
    init.body = body
  }

  const response = await fetch(targetUrl, init)
  const responseHeaders = new Headers(response.headers)

  return new NextResponse(response.body, {
    status: response.status,
    headers: responseHeaders,
  })
}
