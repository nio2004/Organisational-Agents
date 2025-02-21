"use client";
import { signIn, signOut, useSession } from "next-auth/react";
import { useEffect, useState } from "react";
declare module 'next-auth' {
  interface Session {
    accessToken?: string;
  }
}
export default function GoogleCalendarPage() {
  const { data: session } = useSession();
  const [calendars, setCalendars] = useState([]);
  const [selectedCalendar, setSelectedCalendar] = useState("");

  useEffect(() => {
    if (session?.accessToken) {
      fetch("/api/google-calendar")
        .then((res) => {
          if (res.status === 401) {
            console.error("❌ Invalid Credentials - Signing out...");
            signOut(); // Automatically sign out user if unauthorized
            return null;
          }
          return res.json();
        })
        .then((data) => {
          if (data?.calendars) setCalendars(data.calendars);
        })
        .catch((error) => console.error("❌ Error fetching calendars:", error));
    }
  }, [session]);

  console.log("Session Data:", session);

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-xl font-bold mb-4">Google Calendar Integration</h1>

      {!session ? (
        <button
          onClick={() => signIn("google")}
          className="px-4 py-2 bg-blue-500 text-white rounded"
        >
          Sign in with Google
        </button>
      ) : (
        <>
          <button
            onClick={() => signOut()}
            className="mb-4 px-4 py-2 bg-red-500 text-white rounded"
          >
            Sign Out
          </button>

          <h2 className="text-lg font-semibold">Select a Calendar:</h2>
          <select
            className="p-2 border rounded w-full mt-2"
            onChange={(e) => setSelectedCalendar(e.target.value)}
          >
            <option value="">-- Choose Calendar --</option>
            {calendars.map((cal: any) => (
              <option key={cal.id} value={cal.id}>
                {cal.summary}
              </option>
            ))}
          </select>

          {selectedCalendar && (
            <div className="mt-6">
              <h2 className="text-lg font-semibold">Embedded Calendar:</h2>
              <iframe
                src={`https://calendar.google.com/calendar/embed?src=${selectedCalendar}&ctz=UTC`}
                className="w-full h-96 border-none mt-2"
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
