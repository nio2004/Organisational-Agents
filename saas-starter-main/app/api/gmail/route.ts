import { google } from "googleapis";
import { getServerSession } from "next-auth";
import { authOptions } from "../auth/[...nextauth]/route";

export async function GET() {
  const session = await getServerSession(authOptions);
  if (!session || !session.accessToken) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  try {
    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials({ access_token: session.accessToken });

    const gmail = google.gmail({ version: "v1", auth: oauth2Client });

    const response = await gmail.users.messages.list({
      userId: "me",
      maxResults: 5,
    });

    const emails = await Promise.all(
      response.data.messages?.map(async (msg) => {
        const message = await gmail.users.messages.get({
          userId: "me",
          id: msg.id!,
        });

        return {
          id: msg.id,
          snippet: message.data.snippet,
        };
      }) || []
    );

    return Response.json(emails);
  } catch (error) {
    return Response.json({ error: "Failed to fetch emails" }, { status: 500 });
  }
}
