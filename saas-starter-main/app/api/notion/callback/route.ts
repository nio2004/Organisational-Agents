import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const code = searchParams.get("code");

  if (!code) {
    return NextResponse.json({ error: "No authorization code provided" }, { status: 400 });
  }

  try {
    const response = await fetch("https://api.notion.com/v1/oauth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Basic ${Buffer.from(
          `${process.env.NOTION_CLIENT_ID}:${process.env.NOTION_CLIENT_SECRET}`
        ).toString("base64")}`,
      },
      body: JSON.stringify({
        grant_type: "authorization_code",
        code,
        redirect_uri: process.env.NOTION_REDIRECT_URI,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json({ error: "Failed to fetch access token" }, { status: 500 });
    }
    const responseHeaders = new Headers();
    responseHeaders.append(
      "Set-Cookie",
      `notion_access_token=${data.access_token}; Path=/; HttpOnly; Secure`
    );

    // Redirect to dashboard after successful login
    return NextResponse.redirect("http://localhost:3000/dashboard", { headers: responseHeaders });
    // return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "OAuth callback failed" }, { status: 500 });
  }
}
