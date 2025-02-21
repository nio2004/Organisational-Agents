import { redirect } from 'next/navigation';
// import { Settings } from './settings';
import { getTeamForUser, getUser } from '@/lib/db/queries';
import GoogleCalendarPage from '@/components/googlecalendar';
import NotionPagePreview from '@/components/NotionPagePreview';

export default async function SettingsPage() {
  const user = await getUser();

  if (!user) {
    redirect('/sign-in');
  }

  const teamData = await getTeamForUser(user.id);

  if (!teamData) {
    throw new Error('Team not found');
  }

  return (
    <div className='flex justify-evenly'>
      {/* DashBoard */}
      <div>
        <GoogleCalendarPage />
      </div>
      <div>
        <NotionPagePreview />
      </div>
    </div>
  );
}
