import { useState } from 'react';
import PropTypes from 'prop-types';
import { getEnrollmentColor, indexToDayName } from '../utils/scheduleUtils';
import './TimeSlotCell.css';

function TimeSlotCell({ slot, dayIndex, onHover, onLeave }) {
    const [isHovered, setIsHovered] = useState(false);

    const handleMouseEnter = (e) => {
        setIsHovered(true);
        onHover(slot, dayIndex, e.currentTarget);
    };

    const handleMouseLeave = () => {
        setIsHovered(false);
        onLeave();
    };

    const backgroundColor = getEnrollmentColor(slot.enrollment);
    const hasClasses = slot.courses.length > 0;

    return (
        <div
            className={`time-slot-cell ${isHovered ? 'hovered' : ''} ${hasClasses ? 'has-classes' : ''}`}
            style={{ backgroundColor }}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            title={hasClasses ? `${slot.courses.length} course(s), ${slot.enrollment} students` : 'No classes'}
        >
            {slot.enrollment > 0 && (
                <span className="enrollment-count">{slot.enrollment}</span>
            )}
        </div>
    );
}

TimeSlotCell.propTypes = {
    slot: PropTypes.shape({
        startTime: PropTypes.string.isRequired,
        endTime: PropTypes.string.isRequired,
        displayTime: PropTypes.string.isRequired,
        courses: PropTypes.array.isRequired,
        enrollment: PropTypes.number.isRequired,
    }).isRequired,
    dayIndex: PropTypes.number.isRequired,
    onHover: PropTypes.func.isRequired,
    onLeave: PropTypes.func.isRequired,
};

export default TimeSlotCell;
