import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET() {
  const token = (await cookies()).get("notion_access_token")?.value || null;
  return NextResponse.json({ access_token: token });
}
