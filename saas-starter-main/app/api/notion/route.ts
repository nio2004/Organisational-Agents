import { NextRequest, NextResponse } from "next/server";
import { Client } from "@notionhq/client";

const notion = new Client({ auth: process.env.NOTION_API_KEY });

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const pageId = searchParams.get("pageId");

  if (!pageId) {
    return NextResponse.json({ error: "Missing page ID" }, { status: 400 });
  }

  try {
    const response = await notion.pages.retrieve({ page_id: pageId });

    return NextResponse.json(response);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch Notion page" }, { status: 500 });
  }
}
