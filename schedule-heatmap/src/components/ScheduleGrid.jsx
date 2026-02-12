import { useState } from 'react';
import PropTypes from 'prop-types';
import TimeSlotCell from './TimeSlotCell';
import CourseTooltip from './CourseTooltip';
import { indexToDayName } from '../utils/scheduleUtils';
import './ScheduleGrid.css';

function ScheduleGrid({ scheduleGrid, timeSlots }) {
    const [tooltip, setTooltip] = useState({
        visible: false,
        courses: [],
        position: { top: 0, left: 0 },
        pinnedSlot: null
    });

    const handleCellClick = (slot, dayIndex, slotIndex, element) => {
        // If clicking the same cell, close the tooltip
        if (tooltip.pinnedSlot === `${dayIndex}-${slotIndex}`) {
            setTooltip({
                visible: false,
                courses: [],
                position: { top: 0, left: 0 },
                pinnedSlot: null
            });
            return;
        }

        // If cell has no courses, close tooltip
        if (slot.courses.length === 0) {
            setTooltip({
                visible: false,
                courses: [],
                position: { top: 0, left: 0 },
                pinnedSlot: null
            });
            return;
        }

        const rect = element.getBoundingClientRect();

        // Position tooltip to the right of the cell
        let tooltipLeft = rect.right + 10;
        let tooltipTop = Math.max(10, rect.top); // At least 10px from top

        // If tooltip would go off right edge, position it to the left instead
        const tooltipWidth = 450; // max-width from CSS
        if (tooltipLeft + tooltipWidth > window.innerWidth) {
            tooltipLeft = rect.left - tooltipWidth - 10;
        }

        // Ensure tooltip doesn't go off bottom
        const maxHeight = window.innerHeight * 0.8; // 80vh from CSS
        if (tooltipTop + maxHeight > window.innerHeight) {
            tooltipTop = window.innerHeight - maxHeight - 10;
        }

        setTooltip({
            visible: true,
            courses: slot.courses,
            position: {
                top: tooltipTop,
                left: tooltipLeft
            },
            pinnedSlot: `${dayIndex}-${slotIndex}`
        });
    };

    const days = [1, 2, 3, 4, 5]; // Monday through Friday only

    return (
        <div className="schedule-grid-container">
            <div className="schedule-grid">
                {/* Header row with time slots */}
                <div className="grid-header">
                    <div className="time-column-header">Day</div>
                    {timeSlots.map((slot, slotIndex) => (
                        <div key={slotIndex} className="day-header">
                            {slot.displayTime}
                        </div>
                    ))}
                </div>

                {/* Day rows */}
                {days.map(dayIndex => (
                    <div key={dayIndex} className="time-row">
                        <div className="time-label">{indexToDayName(dayIndex)}</div>
                        {timeSlots.map((slot, slotIndex) => {
                            const cellData = scheduleGrid[dayIndex][slotIndex];
                            return (
                                <TimeSlotCell
                                    key={`${dayIndex}-${slotIndex}`}
                                    slot={cellData}
                                    dayIndex={dayIndex}
                                    slotIndex={slotIndex}
                                    onClick={handleCellClick}
                                    isActive={tooltip.pinnedSlot === `${dayIndex}-${slotIndex}`}
                                />
                            );
                        })}
                    </div>
                ))}
            </div>

            <CourseTooltip
                courses={tooltip.courses}
                position={tooltip.position}
                visible={tooltip.visible}
            />
        </div>
    );
}

ScheduleGrid.propTypes = {
    scheduleGrid: PropTypes.object.isRequired,
    timeSlots: PropTypes.array.isRequired,
};

export default ScheduleGrid;
