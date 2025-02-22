import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { Client } from "@notionhq/client";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const pageId = searchParams.get("pageId");

  if (!pageId) {
    return NextResponse.json({ error: "Page ID is required" }, { status: 400 });
  }

  const token = (await cookies()).get("notion_access_token")?.value;
  console.log("notion T=",token);
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
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      }
    );
  } catch (error) {
    return new NextResponse(
      JSON.stringify({ error: `Notion API Error: ${(error as any).message}` }),
      { status: 500 }
    );
  }
}

// ✅ Create a new TODO item
export async function POST(req: Request) {
  const { searchParams } = new URL(req.url);
  const pageId = searchParams.get("pageId");

  if (!pageId) {
    return NextResponse.json({ error: "Page ID is required" }, { status: 400 });
  }

  const { todoText } = await req.json();
  if (!todoText) {
    return NextResponse.json({ error: "Todo text is required" }, { status: 400 });
  }

  const token = (await cookies()).get("notion_access_token")?.value;
  if (!token) {
    return NextResponse.json({ error: "Unauthorized: No valid token" }, { status: 401 });
  }

  const notion = new Client({ auth: token });

  try {
    const response = await notion.blocks.children.append({
      block_id: pageId,
      children: [
        {
          object: "block",
          type: "to_do",
          to_do: {
            rich_text: [{ text: { content: todoText } }],
            checked: false,
          },
        },
      ],
    });

    return NextResponse.json({ success: true, block: response }, { status: 201 });
  } catch (error) {
    return NextResponse.json({ error: `Failed to create TODO: ${(error as any).message}` }, { status: 500 });
  }
}

// ✅ Update a TODO item (mark as completed or edit text)
export async function PATCH(req: Request) {
  const { blockId, newText, checked } = await req.json();
  if (!blockId) {
    return NextResponse.json({ error: "Block ID is required" }, { status: 400 });
  }

  const token = (await cookies()).get("notion_access_token")?.value;
  if (!token) {
    return NextResponse.json({ error: "Unauthorized: No valid token" }, { status: 401 });
  }

  const notion = new Client({ auth: token });

  try {
    const response = await notion.blocks.update({
      block_id: blockId,
      to_do: {
        rich_text: newText ? [{ text: { content: newText } }] : undefined,
        checked: checked !== undefined ? checked : undefined,
      },
    });

    return NextResponse.json({ success: true, block: response }, { status: 200 });
  } catch (error) {
    return NextResponse.json({ error: `Failed to update TODO: ${(error as any).message}` }, { status: 500 });
  }
}

// ✅ Delete a TODO item
export async function DELETE(req: Request) {
  const { blockId } = await req.json();
  if (!blockId) {
    return NextResponse.json({ error: "Block ID is required" }, { status: 400 });
  }

  const token = (await cookies()).get("notion_access_token")?.value;
  if (!token) {
    return NextResponse.json({ error: "Unauthorized: No valid token" }, { status: 401 });
  }

  const notion = new Client({ auth: token });

  try {
    await notion.blocks.delete({ block_id: blockId });

    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error) {
    return NextResponse.json({ error: `Failed to delete TODO: ${(error as any).message}` }, { status: 500 });
  }
}

// ✅ Handle CORS Preflight Requests
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
