"use client";

import { useState, useEffect } from "react";

const NotionPagePreview = () => {
  const [notionPages, setNotionPages] = useState<any[]>([]);
  const [pageContent, setPageContent] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [accessToken, setAccessToken] = useState<string | null>(null);

  useEffect(() => {
    const fetchToken = async () => {
      const res = await fetch("/api/notion/token");
      const data = await res.json();
      if (data.access_token) {
        setAccessToken(data.access_token);
        fetchNotionPages();
      }
    };
    fetchToken();
  }, []);

  const fetchNotionPages = async () => {
    try {
      const res = await fetch("/api/notion/pages");
      const data = await res.json();
      if (res.ok && data.pages.length > 0) {
        setNotionPages(data.pages);
      } else {
        setError("No shared Notion pages found.");
      }
    } catch {
      setError("Failed to fetch Notion pages.");
    }
  };

  const fetchNotionContent = async (pageId: string) => {
    try {
      const res = await fetch(`/api/notion/content?pageId=${pageId}`);
      const data = await res.json();
      if (res.ok) {
        setPageContent(data.blocks);
      } else {
        setError("Failed to fetch Notion content.");
      }
    } catch (err) {
      setError("Error fetching content.");
    }
  };

  const handleLogin = () => {
    window.location.href = "/api/notion/login";
  };

  const handleLogout = async () => {
    await fetch("/api/notion/logout", { method: "POST" });
    setAccessToken(null);
    setNotionPages([]);
    setPageContent([]);
  };

  return (
    <div className="flex flex-col items-center p-4">
      <h2 className="text-2xl font-semibold mb-4">Notion Page Preview</h2>

      {!accessToken ? (
        <button
          onClick={handleLogin}
          className="bg-green-600 text-white px-4 py-2 rounded-md mb-4"
        >
          Login with Notion
        </button>
      ) : (
        <button
          onClick={handleLogout}
          className="bg-red-600 text-white px-4 py-2 rounded-md mb-4"
        >
          Logout
        </button>
      )}

      {error && <p className="text-red-500 mt-2">{error}</p>}

      {notionPages.length > 0 ? (
        notionPages.map((page) => (
          <button
            key={page.id}
            onClick={() => fetchNotionContent(page.id)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md mt-2"
          >
            Load Notion Content
          </button>
        ))
      ) : (
        <p className="text-gray-500">No Notion pages found.</p>
      )}

      {/* Render Notion Page Content */}
      <div className="w-full max-w-2xl mt-6 p-4 border rounded-lg bg-gray-100">
        {pageContent.length > 0 ? (
          pageContent.map((block) => (
            <div key={block.id} className="mb-4">
              {block.type === "paragraph" && <p>{block.paragraph?.rich_text?.[0]?.text?.content}</p>}
              {block.type === "heading_1" && <h1 className="text-2xl font-bold">{block.heading_1?.rich_text?.[0]?.text?.content}</h1>}
              {block.type === "heading_2" && <h2 className="text-xl font-bold">{block.heading_2?.rich_text?.[0]?.text?.content}</h2>}
              {block.type === "heading_3" && <h3 className="text-lg font-bold">{block.heading_3?.rich_text?.[0]?.text?.content}</h3>}
              {block.type === "bulleted_list_item" && <li>{block.bulleted_list_item?.rich_text?.[0]?.text?.content}</li>}
              {block.type === "numbered_list_item" && <ol>{block.numbered_list_item?.rich_text?.[0]?.text?.content}</ol>}
            </div>
          ))
        ) : (
          <p className="text-gray-500">No content loaded yet.</p>
        )}
      </div>
    </div>
  );
};

export default NotionPagePreview;
