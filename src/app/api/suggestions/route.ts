import { NextResponse } from 'next/server';

export async function GET() {
  const suggestions = [
    {
      id: 's1',
      title: 'Deep Focus: Geisel Library',
      start: 14,
      end: 16.5,
      reason: 'Perfect 2.5h gap in your afternoon schedule.',
      rank: 1
    },
    {
      id: 's2',
      title: 'Networking: Tech Meetup',
      start: 18,
      end: 19.5,
      reason: 'Relevant to your "Deep Work" topics today.',
      rank: 2
    },
    {
      id: 's3',
      title: 'Recovery: Evening Yoga',
      start: 20,
      end: 21,
      reason: 'Recommended after your High Priority gym session.',
      rank: 3
    }
  ];

  return NextResponse.json(suggestions);
}