"use client";

import { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react"; // Import refresh icon from lucide-react

const NotionPagePreview = () => {
  const [notionPages, setNotionPages] = useState<any[]>([]);
  const [pageContent, setPageContent] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

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

  useEffect(() => {
    if (notionPages.length > 0) {
      fetchNotionContent(notionPages[0].id); // Automatically fetch first page content
    }
  }, [notionPages]);

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
    setLoading(true);
    console.log("Fetching content for page ID:", pageId);
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
    setLoading(false);
  };

  const handleReload = () => {
    if (notionPages.length > 0) {
      fetchNotionContent(notionPages[0].id);
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
      <div className="w-full max-w-2xl flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Notion Page Preview</h2>
        <button onClick={handleReload} className="p-2 rounded-full bg-gray-200 hover:bg-gray-300">
          <RefreshCw className={`w-5 h-5 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

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
              {block.type === "to_do" && (
                <div className="flex items-center space-x-2">
                  <input type="checkbox" checked={block.to_do?.checked} readOnly />
                  <span>{block.to_do?.rich_text?.[0]?.text?.content}</span>
                </div>
              )}
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
