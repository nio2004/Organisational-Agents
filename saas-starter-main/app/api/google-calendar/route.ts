import { google } from "googleapis";
import { getServerSession } from "next-auth";
import { NextResponse } from "next/server";
import { authOptions } from "../auth/[...nextauth]/route";

export async function GET() {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.accessToken) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: session.accessToken });

    const calendar = google.calendar({ version: "v3", auth });

    // Fetch user calendar list
    const calendarList = await calendar.calendarList.list();

    return NextResponse.json({ calendars: calendarList.data.items || [] });
  } catch (error: any) {
    console.error("Google Calendar API error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}


// import { getSession } from "next-auth/react";
// import { NextResponse } from "next/server";

// export async function GET() {
//   const session = await getSession();

//   if (!session?.accessToken) {
//     console.log("User not authenticated"+session);
//     return NextResponse.json({ error: "User not authenticated" }, { status: 401 });
//   }

//   const res = await fetch("https://www.googleapis.com/calendar/v3/users/me/calendarList", {
//     headers: {
//       Authorization: `Bearer ${session.accessToken}`,
//     },
//   });

//   const data = await res.json();
//   return NextResponse.json(data);
// }
