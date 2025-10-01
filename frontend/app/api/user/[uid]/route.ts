import { NextRequest, NextResponse } from "next/server"
import { proxyDatabaseRequest } from "@/lib/server/proxy-db"

type RouteContext = {
  params: {
    uid: string
  }
}

export async function GET(request: NextRequest, context: RouteContext) {
  const { uid } = context.params

  if (!uid) {
    return NextResponse.json({ error: "User ID is required" }, { status: 400 })
  }

  return proxyDatabaseRequest(request, `/user/${uid}`)
}
