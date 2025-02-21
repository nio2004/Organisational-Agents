import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ success: true });

  // Clear notion_access_token cookie
  response.headers.set(
    "Set-Cookie",
    "notion_access_token=; Path=/; HttpOnly; Secure; Max-Age=0"
  );

  return response;
}
