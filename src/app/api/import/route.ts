import { NextResponse } from 'next/server';

export async function POST() {
  // In a real app, this would use OAuth and Google/Outlook APIs
  const mockImportedEvents = [
    {
      id: 'imp1',
      title: 'Legacy: Monday Sync',
      start: 10,
      end: 11,
      color: 'bg-slate-400'
    },
    {
      id: 'imp2',
      title: 'Legacy: Lunch with Sarah',
      start: 12,
      end: 13,
      color: 'bg-slate-400'
    }
  ];

  return NextResponse.json(mockImportedEvents);
}