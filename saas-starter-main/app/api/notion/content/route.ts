import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { Client } from "@notionhq/client";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const pageId = searchParams.get("pageId");

  if (!pageId) {
    return NextResponse.json({ error: "Page ID is required" }, { status: 400 });
  }

  // Fetch Notion access token from cookies
  const token = (await cookies()).get("notion_access_token")?.value;

  if (!token) {
    return NextResponse.json({ error: "Unauthorized: No valid token" }, { status: 401 });
  }

  const notion = new Client({ auth: token });

  try {
    const blocks = await notion.blocks.children.list({ block_id: pageId });

    return new NextResponse(
      JSON.stringify({ blocks: blocks.results }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*", // Allow all origins
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      }
    );
  } catch (error) {
    const errorMessage = (error as any).message;
    return new NextResponse(
      JSON.stringify({ error: `Notion API Error: ${errorMessage}` }),
      {
        status: 500,
        headers: {
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  }
}

// Handle CORS Preflight Requests (OPTIONS)
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
