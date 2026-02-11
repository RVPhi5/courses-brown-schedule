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
        position: { top: 0, left: 0 }
    });

    const handleCellHover = (slot, dayIndex, element) => {
        if (slot.courses.length === 0) {
            setTooltip({ visible: false, courses: [], position: { top: 0, left: 0 } });
            return;
        }

        const rect = element.getBoundingClientRect();
        const tooltipLeft = rect.right + 10;
        const tooltipTop = rect.top;

        setTooltip({
            visible: true,
            courses: slot.courses,
            position: {
                top: tooltipTop,
                left: tooltipLeft
            }
        });
    };

    const handleCellLeave = () => {
        setTooltip({ visible: false, courses: [], position: { top: 0, left: 0 } });
    };

    const days = [0, 1, 2, 3, 4, 5, 6]; // Sunday through Saturday

    return (
        <div className="schedule-grid-container">
            <div className="schedule-grid">
                {/* Header row with day names */}
                <div className="grid-header">
                    <div className="time-column-header">Time</div>
                    {days.map(dayIndex => (
                        <div key={dayIndex} className="day-header">
                            {indexToDayName(dayIndex)}
                        </div>
                    ))}
                </div>

                {/* Time rows */}
                {timeSlots.map((slot, slotIndex) => (
                    <div key={slotIndex} className="time-row">
                        <div className="time-label">{slot.displayTime}</div>
                        {days.map(dayIndex => {
                            const cellData = scheduleGrid[dayIndex][slotIndex];
                            return (
                                <TimeSlotCell
                                    key={`${dayIndex}-${slotIndex}`}
                                    slot={cellData}
                                    dayIndex={dayIndex}
                                    onHover={handleCellHover}
                                    onLeave={handleCellLeave}
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
