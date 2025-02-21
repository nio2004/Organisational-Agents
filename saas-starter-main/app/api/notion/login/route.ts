import { NextRequest, NextResponse } from "next/server";

export async function GET() {
  const notionAuthUrl = `https://api.notion.com/v1/oauth/authorize?client_id=${process.env.NOTION_CLIENT_ID}&response_type=code&owner=user&redirect_uri=${process.env.NOTION_REDIRECT_URI}`;

  return NextResponse.redirect(notionAuthUrl);
}
