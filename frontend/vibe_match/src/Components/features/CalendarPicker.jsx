'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import { ChevronLeft, ChevronRight, X } from 'lucide-react';
import './CalendarPicker.css';

const MONTHS = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const DAYS = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá'];

// Parse YYYY-MM-DD as local date (avoid UTC shift)
function parseLocalDate(dateStr) {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export default function CalendarPicker({ selectedDate, onSelect, onClose, isOpen }) {
  const [currentMonth, setCurrentMonth] = useState(() => {
    if (typeof window === 'undefined') return { year: new Date().getFullYear(), month: new Date().getMonth() };
    const d = selectedDate ? parseLocalDate(selectedDate) : new Date();
    return { year: d.getFullYear(), month: d.getMonth() };
  });
  const [hoveredDate, setHoveredDate] = useState(null);
  const pickerRef = useRef(null);

  // Update currentMonth when selectedDate changes
  useEffect(() => {
    if (selectedDate) {
      const d = parseLocalDate(selectedDate);
      setCurrentMonth({ year: d.getFullYear(), month: d.getMonth() });
    }
  }, [selectedDate]);

  // Close on outside click
  useEffect(() => {
    if (typeof window === 'undefined') return;
    function handleClickOutside(e) {
      if (pickerRef.current && !pickerRef.current.contains(e.target)) {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  const daysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();
  const isToday = (year, month, day) => {
    const today = new Date();
    return today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
  };
  const isSelected = (year, month, day) => {
    if (!selectedDate) return false;
    const d = parseLocalDate(selectedDate);
    return d.getFullYear() === year && d.getMonth() === month && d.getDate() === day;
  };
  const isPast = (year, month, day) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const d = new Date(year, month, day);
    return d < today;
  };

  const prevMonth = () => setCurrentMonth(m => ({
    year: m.month === 0 ? m.year - 1 : m.year,
    month: m.month === 0 ? 11 : m.month - 1
  }));
  const nextMonth = () => setCurrentMonth(m => ({
    year: m.month === 11 ? m.year + 1 : m.year,
    month: m.month === 11 ? 0 : m.month + 1
  }));

  const handleDayClick = (day) => {
    const dateStr = `${currentMonth.year}-${String(currentMonth.month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    onSelect(dateStr);
  };

  const weekRows = (() => {
    const rows = [];
    const totalDays = daysInMonth(currentMonth.year, currentMonth.month);
    const firstDay = firstDayOfMonth(currentMonth.year, currentMonth.month);
    let day = 1;

    for (let i = 0; i < 6; i++) {
      const row = [];
      for (let j = 0; j < 7; j++) {
        if (i === 0 && j < firstDay) {
          row.push(null);
        } else if (day > totalDays) {
          row.push(null);
        } else {
          row.push(day++);
        }
      }
      rows.push(row);
      if (day > totalDays) break;
    }
    return rows;
  })();

  if (!isOpen) return null;

  return (
    <div className="calendar-picker" ref={pickerRef} role="dialog" aria-label="Seleccionar fecha">
      <div className="calendar-picker__header">
        <button className="calendar-picker__nav" onClick={prevMonth} aria-label="Mes anterior">
          <ChevronLeft size={18} />
        </button>
        <div className="calendar-picker__title">
          {MONTHS[currentMonth.month]} {currentMonth.year}
        </div>
        <button className="calendar-picker__nav" onClick={nextMonth} aria-label="Mes siguiente">
          <ChevronRight size={18} />
        </button>
      </div>

      <div className="calendar-picker__weekdays">
        {DAYS.map(d => <div key={d} className="calendar-picker__weekday">{d}</div>)}
      </div>

      <div className="calendar-picker__days">
        {weekRows.map((week, wi) => (
          <div key={wi} className="calendar-picker__week">
            {week.map((day, di) => {
              if (day === null) return <div key={`empty-${wi}-${di}`} className="calendar-picker__day empty" />;
              const today = isToday(currentMonth.year, currentMonth.month, day);
              const selected = isSelected(currentMonth.year, currentMonth.month, day);
              const past = isPast(currentMonth.year, currentMonth.month, day);
              const hovered = hoveredDate === day;

              return (
                <button
                  key={day}
                  className={`calendar-picker__day ${today ? 'today' : ''} ${selected ? 'selected' : ''} ${past ? 'past' : ''} ${hovered ? 'hovered' : ''}`}
                  onClick={() => !past && handleDayClick(day)}
                  onMouseEnter={() => !past && setHoveredDate(day)}
                  onMouseLeave={() => setHoveredDate(null)}
                  disabled={past}
                  aria-label={`${day} de ${MONTHS[currentMonth.month]} ${currentMonth.year}`}
                  aria-selected={selected}
                  aria-current={today ? 'date' : undefined}
                >
                  {day}
                </button>
              );
            })}
          </div>
        ))}
      </div>

      <div className="calendar-picker__footer">
        <button className="calendar-picker__clear" onClick={() => onSelect(null)}>
          <X size={14} /> Limpiar
        </button>
        <button className="calendar-picker__today" onClick={() => {
          const today = new Date();
          const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
          onSelect(dateStr);
        }}>
          Hoy
        </button>
      </div>
    </div>
  );
}