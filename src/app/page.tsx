'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Calendar, Sparkles, RefreshCcw, Search, Plus, Settings, 
  ChevronLeft, ChevronRight, X, Check, Trash2, Layout, 
  Palette, MapPin, AlignLeft, Flag
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const HOURS = Array.from({ length: 15 }, (_, i) => i + 8); // 8 AM to 10 PM
const SLOT_HEIGHT = 80;

const CATALOG_TEMPLATES = [
  { name: 'Deep Work', icon: '💻', color: 'bg-indigo-500', duration: 2, category: 'Work' },
  { name: 'Gym', icon: '💪', color: 'bg-rose-500', duration: 1.5, category: 'Health' },
  { name: 'Study Session', icon: '📚', color: 'bg-amber-500', duration: 1, category: 'Education' },
  { name: 'Dinner', icon: '🍽️', color: 'bg-emerald-500', duration: 1, category: 'Personal' },
  { name: 'Quick Sync', icon: '⚡', color: 'bg-blue-400', duration: 0.5, category: 'Work' },
];

const THEMES = [
  { name: 'Modern White', class: 'bg-slate-50' },
  { name: 'Midnight', class: 'bg-slate-900' },
  { name: 'Soft Peach', class: 'bg-orange-50' },
  { name: 'Mint Breeze', class: 'bg-emerald-50' },
];

type Priority = 'High' | 'Medium' | 'Low';

interface CalendarEvent {
  id: string;
  title: string;
  start: number;
  end: number;
  color: string;
  priority: Priority;
  location?: string;
  notes?: string;
}

interface Suggestion {
  id: string;
  title: string;
  start: number;
  end: number;
  reason: string;
  rank: number;
}

export default function Calidefy() {
  const [events, setEvents] = useState<CalendarEvent[]>([
    { id: '1', title: 'Coffee with Team', start: 9, end: 10, color: 'bg-blue-500', priority: 'Medium' },
  ]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [currentTheme, setCurrentTheme] = useState(THEMES[0]);
  const [editingEventId, setEditingEventId] = useState<string | null>(null);
  const [dragging, setDragging] = useState<{ start: number; current: number } | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const containerRef = useRef<HTMLDivElement>(null);

  const fetchSuggestions = async () => {
    setLoadingSuggestions(true);
    await new Promise(r => setTimeout(r, 1000));
    try {
      const res = await fetch('/api/suggestions');
      const data = await res.json();
      setSuggestions(data.sort((a: any, b: any) => a.rank - b.rank));
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const getYCoordinate = (clientY: number) => {
    if (!containerRef.current) return 0;
    const rect = containerRef.current.getBoundingClientRect();
    const relativeY = clientY - rect.top + containerRef.current.scrollTop;
    const hour = relativeY / SLOT_HEIGHT + 8;
    return Math.round(hour * 4) / 4;
  };

  // Drag-to-Create Logic (Grid Canvas)
  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('.event-block')) return;
    setEditingEventId(null);
    const startHour = getYCoordinate(e.clientY);
    setDragging({ start: startHour, current: startHour });
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!dragging) return;
    const currentHour = getYCoordinate(e.clientY);
    setDragging(prev => prev ? { ...prev, current: currentHour } : null);
  };

  const handleCanvasMouseUp = () => {
    if (dragging) {
      const start = Math.min(dragging.start, dragging.current);
      const end = Math.max(dragging.start, dragging.current);
      if (end - start >= 0.25) {
        const id = Date.now().toString();
        setEvents([...events, { id, title: "New Event", start, end, color: 'bg-blue-600', priority: 'Medium' }]);
        setEditingEventId(id);
      }
      setDragging(null);
    }
  };

  // Template Drag-and-Drop Logic
  const onTemplateDragStart = (e: React.DragEvent, template: any) => {
    e.dataTransfer.setData('application/json', JSON.stringify(template));
    e.dataTransfer.effectAllowed = 'copy';
  };

  const onGridDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const data = e.dataTransfer.getData('application/json');
    if (!data) return;
    const template = JSON.parse(data);
    const hour = getYCoordinate(e.clientY);
    const start = Math.round(hour * 4) / 4;
    
    const newEvent: CalendarEvent = {
      id: Date.now().toString(),
      title: template.name,
      start,
      end: start + template.duration,
      color: template.color,
      priority: 'Medium'
    };
    setEvents([...events, newEvent]);
    setEditingEventId(newEvent.id);
  };

  const updateEvent = (id: string, updates: Partial<CalendarEvent>) => {
    setEvents(events.map(ev => ev.id === id ? { ...ev, ...updates } : ev));
  };

  const deleteEvent = (id: string) => {
    setEvents(events.filter(ev => ev.id !== id));
    setEditingEventId(null);
  };

  useEffect(() => {
    const handleGlobalMouseUp = () => handleCanvasMouseUp();
    window.addEventListener('mouseup', handleGlobalMouseUp);
    return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
  }, [dragging]);

  return (
    <div className={cn("flex h-screen font-sans select-none overflow-hidden transition-colors duration-500", currentTheme.class)}>
      {/* SIDEBAR: CATALOG & AI */}
      <aside className={cn(
        "bg-white border-r shadow-2xl z-30 flex flex-col transition-all duration-300",
        isSidebarOpen ? "w-80" : "w-0 overflow-hidden opacity-0"
      )}>
        <div className="p-6 border-b flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-2 text-indigo-600 font-black text-2xl tracking-tighter">
            <Layout size={28} strokeWidth={3} /> CALIDEFY
          </div>
          <button onClick={() => setIsSidebarOpen(false)} className="p-1 hover:bg-slate-100 rounded">
            <ChevronLeft size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
          {/* CATALOG SECTION */}
          <section>
            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Event Catalog</h3>
            <div className="grid grid-cols-1 gap-2">
              {CATALOG_TEMPLATES.map(t => (
                <div 
                  key={t.name}
                  draggable
                  onDragStart={(e) => onTemplateDragStart(e, t)}
                  className="flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-xl cursor-grab active:cursor-grabbing hover:border-indigo-300 hover:shadow-md transition-all group"
                >
                  <span className="text-xl group-hover:scale-125 transition-transform">{t.icon}</span>
                  <div className="flex-1">
                    <p className="text-sm font-bold text-slate-700">{t.name}</p>
                    <p className="text-[10px] text-slate-400 font-medium">{t.duration}h • {t.category}</p>
                  </div>
                  <div className={cn("w-2 h-2 rounded-full", t.color)} />
                </div>
              ))}
            </div>
          </section>

          {/* AI SUGGESTIONS */}
          <section className="bg-indigo-50/50 rounded-2xl p-4 border border-indigo-100 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-500/5 rounded-full blur-2xl -mr-10 -mt-10" />
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 font-bold text-indigo-900 text-sm">
                <Sparkles size={16} className="text-indigo-500" /> Smart Suggestions
              </div>
              <button onClick={fetchSuggestions} disabled={loadingSuggestions}>
                <RefreshCcw size={14} className={cn("text-indigo-400", loadingSuggestions && "animate-spin")} />
              </button>
            </div>

            <div className="space-y-3">
              {loadingSuggestions ? (
                <div className="space-y-2 animate-pulse">
                  <div className="h-14 bg-white/50 rounded-xl" />
                  <div className="h-14 bg-white/50 rounded-xl" />
                </div>
              ) : (
                suggestions.map(s => (
                  <div 
                    key={s.id}
                    onClick={() => {
                      setEvents([...events, { id: Date.now().toString(), title: s.title, start: s.start, end: s.end, color: 'bg-indigo-400', priority: 'Medium' }]);
                      setSuggestions(suggestions.filter(x => x.id !== s.id));
                    }}
                    className="bg-white p-3 rounded-xl border border-indigo-100/50 shadow-sm cursor-pointer hover:border-indigo-400 hover:scale-[1.02] transition-all group"
                  >
                    <div className="flex justify-between items-start">
                      <p className="font-bold text-xs text-indigo-900 leading-none">{s.title}</p>
                      <span className="text-[9px] bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded-full font-bold">Rank #{s.rank}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-2 font-medium italic line-clamp-1">{s.reason}</p>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

        <div className="p-6 border-t bg-slate-50/30">
          <button className="flex items-center justify-center gap-2 w-full py-3 bg-slate-900 text-white rounded-xl font-bold text-sm hover:bg-black transition-all shadow-xl shadow-slate-200">
            <RefreshCcw size={16} /> Sync Legacy Calendar
          </button>
        </div>
      </aside>

      {/* MAIN CANVAS */}
      <main className="flex-1 flex flex-col relative">
        {!isSidebarOpen && (
          <button 
            onClick={() => setIsSidebarOpen(true)}
            className="absolute left-6 top-6 z-20 p-2 bg-white border shadow-md rounded-full hover:bg-slate-50 transition-all"
          >
            <Layout size={20} className="text-indigo-600" />
          </button>
        )}

        <header className="h-20 px-10 flex items-center justify-between z-10">
          <div className="flex items-center gap-6">
            <h2 className={cn("text-2xl font-black tracking-tight", currentTheme.name === 'Midnight' ? 'text-white' : 'text-slate-800')}>
              Tuesday, April 14
            </h2>
            <div className="flex bg-white/10 backdrop-blur-md p-1 rounded-xl border border-white/20 shadow-sm">
              <button className="p-2 hover:bg-white/20 rounded-lg transition-all"><ChevronLeft size={18} /></button>
              <button className="px-4 py-1.5 bg-white text-indigo-600 rounded-lg text-xs font-black shadow-sm">TODAY</button>
              <button className="p-2 hover:bg-white/20 rounded-lg transition-all"><ChevronRight size={18} /></button>
            </div>
          </div>

          <div className="flex items-center gap-3">
             <div className="flex bg-white/80 p-1 rounded-xl shadow-sm border">
               {THEMES.map(t => (
                 <button 
                   key={t.name}
                   onClick={() => setCurrentTheme(t)}
                   className={cn(
                    "w-6 h-6 rounded-lg m-0.5 transition-all",
                    t.class,
                    currentTheme.name === t.name ? "ring-2 ring-indigo-500 ring-offset-2 scale-110" : "opacity-60 hover:opacity-100"
                   )}
                 />
               ))}
             </div>
             <button className="p-2.5 bg-white rounded-xl shadow-sm border hover:bg-slate-50 transition-all"><Settings size={20} className="text-slate-600" /></button>
          </div>
        </header>

        <div 
          ref={containerRef}
          onMouseDown={handleCanvasMouseDown}
          onMouseMove={handleCanvasMouseMove}
          onDragOver={(e) => e.preventDefault()}
          onDrop={onGridDrop}
          className="flex-1 overflow-y-auto px-10 pb-20 custom-scrollbar"
        >
          <div className={cn(
            "max-w-5xl mx-auto rounded-[32px] shadow-2xl relative transition-all duration-500 overflow-hidden",
            currentTheme.name === 'Midnight' ? "bg-slate-800/50 border-slate-700" : "bg-white/70 border-white"
          )} style={{ backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.2)' }}>
            
            <div className="relative min-h-[1200px]">
              {/* GRID LINES */}
              {HOURS.map((hour) => (
                <div key={hour} className="h-20 border-b border-slate-200/30 flex items-start px-6 py-4 group">
                  <span className={cn(
                    "text-[10px] font-black w-16 pt-0.5 tracking-tighter",
                    currentTheme.name === 'Midnight' ? "text-slate-400" : "text-slate-300"
                  )}>
                    {hour === 12 ? '12 PM' : hour > 12 ? `${hour - 12} PM` : `${hour} AM`}
                  </span>
                  <div className="flex-1 h-full border-l border-slate-100/20" />
                </div>
              ))}

              {/* RENDER EVENTS */}
              {events.map(ev => (
                <div 
                  key={ev.id}
                  onDoubleClick={(e) => { e.stopPropagation(); setEditingEventId(ev.id); }}
                  className={cn(
                    "event-block absolute left-24 right-6 p-4 rounded-3xl transition-all cursor-pointer group shadow-lg overflow-hidden border-l-8",
                    ev.color,
                    ev.priority === 'Low' ? 'opacity-40 grayscale-[0.2] hover:opacity-100 hover:grayscale-0' : 'opacity-100',
                    ev.priority === 'High' ? 'ring-4 ring-white/30 z-20 scale-[1.01]' : 'z-10',
                    editingEventId === ev.id && "ring-4 ring-indigo-400 ring-offset-4 scale-[1.03] shadow-2xl z-40"
                  )}
                  style={{ 
                    top: `${(ev.start - 8) * SLOT_HEIGHT + 4}px`, 
                    height: `${(ev.end - ev.start) * SLOT_HEIGHT - 8}px`,
                  }}
                >
                  <div className="text-white">
                    <div className="flex items-start justify-between gap-2">
                       <h4 className={cn("font-black leading-tight truncate", ev.priority === 'High' ? "text-lg" : "text-sm")}>
                         {ev.title}
                       </h4>
                       <Flag size={ev.priority === 'High' ? 18 : 12} className={cn(ev.priority === 'High' ? "opacity-100" : "opacity-40")} />
                    </div>
                    <div className="flex items-center gap-3 mt-2 opacity-80 text-[10px] font-bold">
                       <span>{formatHour(ev.start)} - {formatHour(ev.end)}</span>
                       {ev.location && <span className="flex items-center gap-1"><MapPin size={10}/> {ev.location}</span>}
                    </div>
                  </div>

                  {/* INLINE EDIT POPUP (Simplified) */}
                  {editingEventId === ev.id && (
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-md p-4 animate-in fade-in duration-200 flex flex-col gap-3">
                       <div className="flex items-center justify-between">
                         <span className="text-[10px] font-black text-white/50 uppercase">Edit Event</span>
                         <button onClick={(e) => { e.stopPropagation(); setEditingEventId(null); }} className="text-white hover:bg-white/20 p-1 rounded-lg transition-all"><X size={16}/></button>
                       </div>
                       <input 
                         autoFocus
                         className="bg-transparent border-b border-white/30 text-white font-black text-lg outline-none placeholder:text-white/20"
                         value={ev.title}
                         onChange={(e) => updateEvent(ev.id, { title: e.target.value })}
                         onKeyDown={(e) => e.key === 'Enter' && setEditingEventId(null)}
                       />
                       <div className="flex items-center gap-2">
                         <button 
                           onClick={(e) => { e.stopPropagation(); updateEvent(ev.id, { priority: 'High' }); }}
                           className={cn("px-2 py-1 rounded-md text-[9px] font-black transition-all", ev.priority === 'High' ? "bg-rose-500 text-white" : "bg-white/10 text-white/50 hover:bg-white/20")}
                         >HIGH</button>
                         <button 
                           onClick={(e) => { e.stopPropagation(); updateEvent(ev.id, { priority: 'Low' }); }}
                           className={cn("px-2 py-1 rounded-md text-[9px] font-black transition-all", ev.priority === 'Low' ? "bg-slate-500 text-white" : "bg-white/10 text-white/50 hover:bg-white/20")}
                         >LOW</button>
                         <div className="flex-1" />
                         <button onClick={(e) => { e.stopPropagation(); deleteEvent(ev.id); }} className="p-2 bg-rose-500/20 text-rose-400 hover:bg-rose-500 hover:text-white rounded-xl transition-all">
                           <Trash2 size={16} />
                         </button>
                       </div>
                    </div>
                  )}
                </div>
              ))}

              {/* DRAGGING PREVIEW */}
              {dragging && (
                <div 
                  className="absolute left-24 right-6 bg-indigo-500/20 border-2 border-indigo-400 border-dashed rounded-[32px] z-0 backdrop-blur-[4px] pointer-events-none"
                  style={{ 
                    top: `${(Math.min(dragging.start, dragging.current) - 8) * SLOT_HEIGHT}px`,
                    height: `${Math.abs(dragging.current - dragging.start) * SLOT_HEIGHT}px` 
                  }}
                />
              )}
            </div>
          </div>
        </div>
      </main>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0,0,0,0.05);
          border-radius: 10px;
        }
        .custom-scrollbar:hover::-webkit-scrollbar-thumb {
          background: rgba(0,0,0,0.1);
        }
      `}</style>
    </div>
  );
}

function formatHour(h: number) {
  const hour = Math.floor(h);
  const minutes = Math.round((h % 1) * 60);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour;
  return `${displayHour}:${minutes === 0 ? '00' : minutes} ${ampm}`;
}