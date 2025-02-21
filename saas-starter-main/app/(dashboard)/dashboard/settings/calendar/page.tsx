"use client";
import { useEffect, useState } from 'react';
import { fetchCalendarEvents } from '@/app/api/calendar/route';


export default function CalendarEvents() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const getEvents = async () => {
      const events = await fetchCalendarEvents();
      setEvents(events);
    };
    getEvents();
  }, []);

  return (
    <div>
      <h2>Your Calendar Events</h2>
      <ul>
        {events.map(event => (
          <li key={event.id}>{event.summary}</li>
        ))}
      </ul>
    </div>
  );
}